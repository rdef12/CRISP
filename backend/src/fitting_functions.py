import numpy as np
import cv2 as cv
from scipy.optimize import curve_fit, OptimizeWarning
import warnings
import matplotlib.pyplot as plt
from scipy.special import voigt_profile
from itertools import product
import math
import io
import base64

from src.modified_pybragg import fitBP, bortfeld, fit_bortfeld_odr, bortfeld_for_odr
from src.uncertainty_functions import *
from src.image_processing import inverse_rotation_of_coords

warnings.filterwarnings("ignore", category=OptimizeWarning)

# GLOBAL PLOT SETTINGS
plt.rc('font', family='serif')
plt.rc('mathtext', fontset='cm')  # Computer Modern for math
plt.rc('text', usetex=False)

LEGEND_CONFIG = {
    "fancybox": True,
    "shadow": True,
}

def linear_function(x_coord, parameters):
    return parameters[0] * x_coord + parameters[1]

def fitting_procedure(x_data, y_data, y_uncertainties):
    """
    NOTE: Insert from LSFR-20
    Is this necessarily Chi squared, or just a least squares fit?
    """
    weights = 1. / y_uncertainties**2
    repeated_term = (np.sum(weights) * np.sum(x_data**2 * weights)
                     - np.sum(x_data * weights)**2)
    slope = ((np.sum(weights) * np.sum(x_data * y_data * weights)
              - np.sum(x_data * weights) * np.sum(y_data * weights))
             / repeated_term)
    slope_uncertainty = np.sqrt(np.sum(weights) / repeated_term)
    offset = ((np.sum(y_data * weights) * np.sum(x_data**2 * weights)
               - np.sum(x_data * weights) * np.sum(x_data * y_data * weights))
              / repeated_term)
    offset_uncertainty = np.sqrt(np.sum(x_data**2 * weights) / repeated_term)

    return (np.array([slope, offset]), np.array([slope_uncertainty,
                                                 offset_uncertainty]))


def chi_squared_function(y_data, y_uncertainties, predicted_y_data):
    return np.sum(((predicted_y_data - y_data) / y_uncertainties)**2)


def gaussian(w, w0, a, sgm):
    '''
    a = scale factor
    sgm = standard deviation/sigma
    '''
    return (a/sgm) * np.exp(-0.5 * ((w - w0)/sgm)**2)


def gaussian_with_background_noise(w, w0, a, sgm, background):
    '''
    a = scale factor
    sgm = standard deviation/sigma
    '''
    return (a/sgm) * np.exp(-0.5 * ((w - w0)/sgm)**2) + background


def voigt(w, w0, a, sgm, gamma):
    '''
    a = scale factor
    sgm = standard deviation/sigma
    gamma = Lorentzian HWHM
    '''
    return a * voigt_profile(w-w0, sgm, gamma)


def voigt_with_background_noise(w, w0, a, sgm, gamma, background):
    '''
    a = scale factor
    sgm = standard deviation/sigma
    gamma = Lorentzian HWHM
    '''
    return a * voigt_profile(w-w0, sgm, gamma) + background



def extract_beam_profile(image, brightness_errors, horizontal_coord, v_bounds):
    pixel_vertical_coords = np.arange(v_bounds[0], v_bounds[1]+ 1)
    column_of_brightness_vals = image[v_bounds[0]: v_bounds[1] + 1, horizontal_coord]
    column_of_brightness_errors = brightness_errors[v_bounds[0]: v_bounds[1] + 1, horizontal_coord]
    return pixel_vertical_coords, column_of_brightness_vals, column_of_brightness_errors 


def fit_gaussian_to_beam_profile(pixel_vertical_coords, column_of_brightness_vals, column_of_brightness_errors, background_brightness):

     # The following is looking to see if the gaussian tails are likely present
     # since the choice of gaussian background estimate depends on this - room for improvement
    if (np.std(column_of_brightness_vals[10:]) <= 2) or (np.std(column_of_brightness_vals[-10:]) <= 2):
        background_estimate = np.min(column_of_brightness_vals)
    else:
        background_estimate = background_brightness # Doesn't always give a good fit for the top cam
    
    column_of_brightness_vals -= background_estimate
    gaussian_center_estimate = pixel_vertical_coords[np.argmax(column_of_brightness_vals)]
    gaussian_sigma_estimate = np.std(column_of_brightness_vals)
    gaussian_scale_estimate = np.max(column_of_brightness_vals) * gaussian_sigma_estimate * np.sqrt(2*np.pi)
        
    try:
        gaussian_paramters, parameter_cov = curve_fit(gaussian, pixel_vertical_coords, column_of_brightness_vals,
                                            p0 = (gaussian_center_estimate,
                                                    gaussian_scale_estimate,
                                                    gaussian_sigma_estimate),
                                            sigma=column_of_brightness_errors,
                                            absolute_sigma=True)
        
        column_of_brightness_vals += background_estimate
        gaussian_paramters, parameter_cov = curve_fit(gaussian_with_background_noise, pixel_vertical_coords, column_of_brightness_vals,
                                            p0 = (gaussian_paramters[0],
                                                    gaussian_paramters[1],
                                                    gaussian_paramters[2],
                                                    background_estimate),
                                            sigma=column_of_brightness_errors,
                                            absolute_sigma=True)
        
        error_on_gaussian_center = np.sqrt(parameter_cov[0, 0])
        
        num_of_dof = len(pixel_vertical_coords) - 4 # Because 4 fit parameters
        fitted_pixel_values = gaussian_with_background_noise(pixel_vertical_coords, gaussian_paramters[0], gaussian_paramters[1], gaussian_paramters[2], gaussian_paramters[3])
        reduced_chi_squared = chi_squared_function(column_of_brightness_vals, column_of_brightness_errors, fitted_pixel_values) / num_of_dof
        
        #Check for Covariance estimation failure
        if gaussian_paramters[2] <= 1: # Sketchy method for now
            print("Covariance estimation failed")
            successful_fit = False
        else:
            successful_fit = True
        
        return gaussian_paramters, error_on_gaussian_center, reduced_chi_squared, successful_fit
    
    except RuntimeError as e:
        successful_fit = False
        return float("nan"), float("nan"), float("nan"),  successful_fit
        
    #     voigt_paramters, parameter_cov = curve_fit(voigt, pixel_vertical_coords, column_of_brightness_vals,
    #                                         p0 = (gaussian_center_estimate,
    #                                                 gaussian_scale_estimate,
    #                                                 gaussian_sigma_estimate,
    #                                                 0),
    #                                         sigma=column_of_brightness_errors,
    #                                         absolute_sigma=True)
        
    #     column_of_brightness_vals += background_estimate
    #     voigt_paramters, parameter_cov = curve_fit(voigt_with_background_noise, pixel_vertical_coords, column_of_brightness_vals,
    #                                         p0 = (voigt_paramters[0],
    #                                                 voigt_paramters[1],
    #                                                 voigt_paramters[2],
    #                                                 voigt_paramters[3],
    #                                                 background_estimate),
    #                                         sigma=column_of_brightness_errors,
    #                                         absolute_sigma=True)
        
    #     error_on_voigt_center = np.sqrt(parameter_cov[0, 0])
        
    #     num_of_dof = len(pixel_vertical_coords) - 5 # Because 4 fit parameters
    #     fitted_pixel_values = voigt_with_background_noise(pixel_vertical_coords, voigt_paramters[0], voigt_paramters[1], voigt_paramters[2], voigt_paramters[3], voigt_paramters[4])
    #     reduced_chi_squared = chi_squared_function(column_of_brightness_vals, column_of_brightness_errors, fitted_pixel_values) / num_of_dof
        
    #     # Check for Covariance estimation failure
    #     if voigt_paramters[2] <= 1: # Sketchy method for now
    #         print("Covariance estimation failed")
    #         successful_fit = False
    #         return float("nan"), float("nan"), float("nan"),  successful_fit
    #     else:
    #         successful_fit = True
            
    #         return voigt_paramters, error_on_voigt_center, reduced_chi_squared, successful_fit

    # except RuntimeError as e:
    #     successful_fit = False
    #     return float("nan"), float("nan"), float("nan"),  successful_fit     
    

def fit_beam_profile_along_full_roi(channel, channel_std, h_bounds, v_bounds, show_fit_qualities: bool=False,
                                    save_best_fit_data: bool=False):
    try:
        (background_brightness, _, _, _) = cv.minMaxLoc(channel[v_bounds[0]: v_bounds[1] + 1, h_bounds[0]: h_bounds[1] + 1])
        
        roi_horizontal_coords = np.arange(h_bounds[0], h_bounds[1], 1)
        total_profile_brightness, unc_total_profile_brightness = [], []

        fitted_parameters_array = np.empty((0, 4), float) # FOR GAUSSIAN FITTING
        #fitted_parameters_array = np.empty((0, 5), float) # FOR VOIGT FITTING
        beam_center_error_array = np.array([])
        reduced_chi_squared_array = []
        
        failed_fits = []
        for index, horizontal_coord in enumerate(roi_horizontal_coords):
            pixel_vertical_coords, column_of_brightness_vals, column_of_brightness_errors = extract_beam_profile(channel, channel_std, horizontal_coord, v_bounds)
            
            fitted_parameters, error_on_beam_center, reduced_chi_squared, success = fit_gaussian_to_beam_profile(pixel_vertical_coords, column_of_brightness_vals,
                                                                                                                    column_of_brightness_errors, background_brightness)
            if not success:
                failed_fits.append(index)
                continue # Should start from next index of for loop, not appending these beam center positions
            
            reduced_chi_squared_array.append(reduced_chi_squared)
            fitted_parameters_array = np.vstack((fitted_parameters_array, fitted_parameters))
            beam_center_error_array = np.append(beam_center_error_array, error_on_beam_center)
            total_profile_brightness.append(np.sum(column_of_brightness_vals))
            unc_total_profile_brightness.append(normal_addition_in_quadrature(column_of_brightness_errors))
            
        roi_horizontal_coords = np.delete(roi_horizontal_coords, failed_fits) # Failed fits deleted from array - no data added when the fit failed (so would be differences in array lengths without this fix)
        print("The number of Gaussian fits which failed is {}".format(len(failed_fits)))
        
        rcs_plot_bytes = plot_reduced_chi_squared_values(roi_horizontal_coords, reduced_chi_squared_array, save_data=False, show_plot=show_fit_qualities)
        
        index_of_worst_accepted_fit = np.argmax(reduced_chi_squared_array)
        index_of_best_accepted_fit = np.argmin(reduced_chi_squared_array)
        
        best_fit_gaussian_plot_bytes = plot_beam_profile(channel, channel_std, roi_horizontal_coords[index_of_best_accepted_fit], v_bounds, background_brightness, np.min(reduced_chi_squared_array),
                                                        profile_type="Best Fit", save_best_fit_data=save_best_fit_data, show_plot=show_fit_qualities)
        worst_fit_gaussian_plot_bytes= plot_beam_profile(channel, channel_std, roi_horizontal_coords[index_of_worst_accepted_fit], v_bounds, background_brightness, np.max(reduced_chi_squared_array),
                                                        profile_type="Worst Fit", show_plot=show_fit_qualities)
        
        best_fit_horizontal_coord = roi_horizontal_coords[index_of_best_accepted_fit]
        worst_fit_horizontal_coord = roi_horizontal_coords[index_of_worst_accepted_fit]
        overlayed_average_image_bytes = render_best_worst_fit_locations(channel, best_fit_horizontal_coord, worst_fit_horizontal_coord, v_bounds)
        
        plot_byte_strings = [rcs_plot_bytes, best_fit_gaussian_plot_bytes, worst_fit_gaussian_plot_bytes, overlayed_average_image_bytes]
        return roi_horizontal_coords, fitted_parameters_array, beam_center_error_array, reduced_chi_squared_array, total_profile_brightness, unc_total_profile_brightness, plot_byte_strings
    except Exception as e:
        raise Exception("Error in fitting beam profile along full ROI: ", e)
    

def render_best_worst_fit_locations(image, best_fit_horizontal_coord, worst_fit_horizontal_coord, v_bounds):
    plt.imshow(image, cmap='gray')
    plt.axvline(best_fit_horizontal_coord, color='green', alpha=0.5)
    plt.axvline(worst_fit_horizontal_coord, color='red', alpha=0.5)
    plt.axhline(v_bounds[0], color='blue', alpha=0.5)
    plt.axhline(v_bounds[1], color='blue', alpha=0.5)
    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    return base64.b64encode(buf.read()).decode('utf-8')


def plot_beam_profile(channel, channel_std, horizontal_coord, v_bounds, global_background_estimate, reduced_chi_squared, profile_type: str=None,
                      save_best_fit_data: bool=False, show_plot: bool=False):
    
    pixel_vertical_coords, column_of_brightness_vals, column_of_brightness_errors = extract_beam_profile(channel, channel_std, horizontal_coord, v_bounds)
    fitted_parameters, _, reduced_chi_squared, _ = fit_gaussian_to_beam_profile(pixel_vertical_coords, column_of_brightness_vals, column_of_brightness_errors,
                                                                                                          global_background_estimate)

    gaussian_center, scale_factor, sigma, background_noise = fitted_parameters
    # gaussian_center, scale_factor, sigma, gamma, background_noise = fitted_parameters # FOR VOIGT FITTING
    
    pixel_height_linspace = np.linspace(pixel_vertical_coords[0], pixel_vertical_coords[-1] + 1, 1000)
    fitted_pixel_values = gaussian_with_background_noise(pixel_height_linspace, gaussian_center, scale_factor, sigma, background_noise)
    #fitted_pixel_values = voigt_with_background_noise(pixel_height_linspace, gaussian_center, scale_factor, sigma, gamma, background_noise) # FOR VOIGT FITTING
    
    # Compute residuals
    residuals = column_of_brightness_vals - gaussian_with_background_noise(pixel_vertical_coords, gaussian_center, scale_factor, sigma, background_noise)
    # residuals = column_of_brightness_vals - voigt_with_background_noise(pixel_vertical_coords, gaussian_center, scale_factor, sigma, gamma, background_noise) # FOR VOIGT FITTING
    
    # Create figure and subplots
    fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(8, 6), sharex=True)
    
    # Plot the beam profile with Gaussian fit
    axs[0].step(pixel_vertical_coords, column_of_brightness_vals, color='black', zorder=9)
    axs[0].errorbar(pixel_vertical_coords, column_of_brightness_vals, yerr=column_of_brightness_errors, 
                    color="black", label="Experimental Data", ms=5, ecolor="blue", zorder=10)
    axs[0].plot(pixel_height_linspace, fitted_pixel_values, color="red", label="Fitted Gaussian Profile \n" + r"$\chi^{2}_R = $" + "{:.3g}".format(reduced_chi_squared))
    axs[0].set_ylabel("Pixel Brightness Value")
    axs[0].set_title("Horizontal Coord = {}".format(horizontal_coord))
    axs[0].legend(**LEGEND_CONFIG)
    axs[0].grid()
    
    # Plot the residuals
    axs[1].scatter(pixel_vertical_coords, residuals, color="black", s=8, label="Residuals")
    axs[1].axhline(0, color='red', linestyle='dashed')
    axs[1].set_xlabel("Pixel's Vertical Image Coordinate")
    axs[1].set_ylabel("Residuals")
    axs[1].grid()
    
    # Adjust layout and show
    fig.tight_layout()
    if show_plot:
        plt.show()
    
    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    return base64.b64encode(buf.read()).decode('utf-8')


def plot_reduced_chi_squared_values(roi_horizontal_coords, reduced_chi_squared_array, save_data: bool=False, show_plot: bool=False):
    
    plt.xlabel("Horizontal Pixel Coordinate")
    plt.ylabel(r"Gaussian Profile $\chi^{2}_R$")
    plt.grid()
    label = r"Best $\chi^{2}_R$: " + "{:.3g} \n".format(np.min(reduced_chi_squared_array)) + r"Worst $\chi^{2}_R$: " + "{:.3g}".format(np.max(reduced_chi_squared_array))
    plt.scatter(roi_horizontal_coords, reduced_chi_squared_array, color="red", s=2, label=label)
    plt.legend(**LEGEND_CONFIG)
    if show_plot:
        plt.show()
    
    if save_data:
        data_array = np.column_stack((roi_horizontal_coords, reduced_chi_squared_array))
        np.savetxt("plotting_data/new_reduced_chi_squared_data.csv", data_array, delimiter=",", header="Horizontal Pixel Coord, Gaussian Reduced Chi Squared")
    
    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    return base64.b64encode(buf.read()).decode('utf-8')


def extract_incident_beam_angle(horizontal_coords, beam_center_vertical_coords, beam_center_errors, 
                                show_angle_plot: bool=True, save_angle_plot: bool=False):
    
    end_of_angle_fitting_range = horizontal_coords[100]
    horizontal_coords = horizontal_coords[0: end_of_angle_fitting_range]
    beam_center_vertical_coords = beam_center_vertical_coords[0: end_of_angle_fitting_range]
    beam_center_errors = beam_center_errors[0: end_of_angle_fitting_range]
    
    line_linspace = np.linspace(horizontal_coords[0], horizontal_coords[-1], 100)
    fitted_line_parameters, fitted_parameter_uncertainties = fitting_procedure(horizontal_coords, beam_center_vertical_coords, beam_center_errors)
    predicted_beam_centers = linear_function(horizontal_coords, fitted_line_parameters)  
    chi_squared_reduced = chi_squared_function(beam_center_vertical_coords, beam_center_errors, predicted_beam_centers) / (len(horizontal_coords) - 2)
    
    fitted_beam_center_positions = linear_function(line_linspace, fitted_line_parameters)
    fitted_angle = np.arctan(fitted_line_parameters[0])
    fitted_tan_angle_uncertainty = fitted_parameter_uncertainties[0]
    unc_fitted_angle = fitted_tan_angle_uncertainty * np.cos(fitted_angle)**2

    fitted_angle, unc_fitted_angle = np.rad2deg(fitted_angle), np.rad2deg(unc_fitted_angle)
    
    fitted_label = r"$\alpha = $" + "{0} +/- {1:.1g}".format(fitted_angle, unc_fitted_angle) + "\u00B0" + "\n" + r"Reduced $\chi^2$ = " + str(round(chi_squared_reduced, 2))
    plt.plot(line_linspace, fitted_beam_center_positions, color="red", label=fitted_label)
    
    plt.errorbar(horizontal_coords, beam_center_vertical_coords, beam_center_errors, color="black", marker="x", label="Experimental Data",
                    ecolor="blue", ls="none")
    plt.xlabel("Pixel's Horizonal Image Coordinate")
    plt.ylabel("Vertical Coordinate of Beam Center Pixels")
    plt.legend(**LEGEND_CONFIG)
    plt.grid()
    if save_angle_plot:
        plt.savefig("plots\incident_beam_angle_plot.png".format(), dpi=600)
    if show_angle_plot:
        plt.show()
        
    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    plot_byte_string = base64.b64encode(buf.read()).decode('utf-8')
    return fitted_angle, unc_fitted_angle, plot_byte_string


###### TODO - REFACTOR THE BELOW FUNCTIONS ##############

def find_peak_of_bortfeld(z_bins, bortfeld_parameters, points_per_bin=100):
    """
    If 100 points per bin, and a bin is a pixel, 0.01 pixel resolution.
    """
    z_length = len(z_bins) * points_per_bin
    z_range = np.linspace(z_bins[0], z_bins[-1], z_length)
    bortfeld_output = bortfeld(z_range, *bortfeld_parameters)
    peak_argument = np.argmax(bortfeld_output)
    peak_z_position = z_range[peak_argument]
    return peak_argument, peak_z_position

def round_to_precision(number, precision):
    rounded_number = np.round(number / precision) * precision
    return rounded_number

def find_peak_position_uncertainty(z_bins, bortfeld_parameters, bortfeld_parameter_uncertainties, points_per_bin=1000, number_of_stds=1):
    
    best_fit_peak_argument, best_fit_peak = find_peak_of_bortfeld(z_bins, bortfeld_parameters, points_per_bin=points_per_bin)
    lower_bound_parameters = bortfeld_parameters - number_of_stds*bortfeld_parameter_uncertainties
    upper_bound_parameters = bortfeld_parameters + number_of_stds*bortfeld_parameter_uncertainties
    all_parameter_combinations = list(product(*zip(lower_bound_parameters, upper_bound_parameters)))
    possible_peak_positions = np.empty((len(all_parameter_combinations)))
    
    for count, parameter_combination in enumerate(all_parameter_combinations):
        _, peak_position = find_peak_of_bortfeld(z_bins, parameter_combination, points_per_bin=points_per_bin)
        possible_peak_positions[count] = peak_position
    best_fit_z_bin_argument = math.ceil(best_fit_peak_argument / points_per_bin)
    z_bin_width = z_bins[best_fit_z_bin_argument] - z_bins[best_fit_z_bin_argument - 1]
    
    uncertainty_order = z_bin_width / points_per_bin
    
    
    lower_peak_index = np.argmin(possible_peak_positions)
    upper_peak_index = np.argmax(possible_peak_positions)
    lower_peak = possible_peak_positions[lower_peak_index]
    upper_peak = possible_peak_positions[upper_peak_index]
    lower_peak_associated_params = all_parameter_combinations[lower_peak_index]
    upper_peak_associated_params = all_parameter_combinations[lower_peak_index]
    
    lower_bound = best_fit_peak - lower_peak
    lower_bound = round_to_precision(lower_bound, uncertainty_order)
    upper_bound = upper_peak - best_fit_peak
    upper_bound = round_to_precision(upper_bound, uncertainty_order)
    
    lower_peak = np.min(possible_peak_positions)
    upper_peak = np.max(possible_peak_positions)
    lower_bound = best_fit_peak - lower_peak
    lower_bound = round_to_precision(lower_bound, uncertainty_order)
    upper_bound = upper_peak - best_fit_peak
    upper_bound = round_to_precision(upper_bound, uncertainty_order)
    
    return [lower_bound, upper_bound], [lower_peak_associated_params, upper_peak_associated_params]


def locate_bragg_peak_in_image(x_positions, beam_center_positions, gaussian_background_estimates, beam_scale_values, beam_center_errors,
                               beam_sigma_values, total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi, save_data: bool=False,
                               show_scintillation_plot: bool=False):
    """
    After this, we need a function which uses the beam angle and bragg peak depth to determine the depth 
    for all over pixels.
    """
    
    initial_bragg_peak_horizontal_coord_index = np.argmax(total_brightness_along_vertical_roi)
    initial_bragg_peak_horizontal_coord = x_positions[initial_bragg_peak_horizontal_coord_index]
    
    half_window = 750
    # Fit to +/- 100 pixels around the peak (using half max brightness includes all points!)
    start_index = max(0, initial_bragg_peak_horizontal_coord_index - half_window)
    end_index = min(len(x_positions), initial_bragg_peak_horizontal_coord_index + half_window + 1)
    x_positions_slice = x_positions[start_index:end_index]
    total_brightness_slice = total_brightness_along_vertical_roi[start_index:end_index]
    unc_brightness_slice = unc_total_brightness_along_vertical_roi[start_index:end_index]
    
    bortfeld_fit = fitBP(x_positions_slice, total_brightness_slice, unc_D=unc_brightness_slice)
    fit_parameters_covariance = bortfeld_fit['bortfeld_fit_cov']
    bortfeld_fit_uncertainties = np.sqrt(np.diag(fit_parameters_covariance))
    
    z = np.linspace(x_positions_slice[0], x_positions_slice[-1], 1000) # I have not passed z in cm here.
    curve = bortfeld(z, *bortfeld_fit['bortfeld_fit_p'])

    predicted_curve = bortfeld(x_positions_slice, *bortfeld_fit['bortfeld_fit_p'])
    chi_squared = chi_squared_function(total_brightness_slice, unc_brightness_slice, predicted_curve)
    reduced_chi_squared = chi_squared / (len(x_positions_slice) - 5) # 5 fitted parameters
    
    fig, ax = plt.subplots()
    ax.plot(z, curve, color="red", label=("Bortfeld fit \n" + r"$\chi^{2}_R$ = " + f"{reduced_chi_squared:.1f}"))
    ax.errorbar(x_positions_slice, total_brightness_slice, yerr=unc_brightness_slice, color="black", label="Experimental Data", ecolor="blue")

    # ax.set_title("{} Camera Bortfeld fit to Bragg curve".format(camera.type.capitalize()))
    ax.set_xlabel("Horizonal Image Coordinate")
    ax.set_ylabel("Total profile Brightness")
    ax.grid()
    ax.legend(**LEGEND_CONFIG)
    if show_scintillation_plot:
        plt.show()
    
    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    plot_byte_string = base64.b64encode(buf.read()).decode('utf-8')
    
    bortfeld_horizontal_coord = z[np.argmax(curve)]
    peak_bounds, _, = find_peak_position_uncertainty(x_positions, bortfeld_fit['bortfeld_fit_p'], bortfeld_fit_uncertainties, points_per_bin=100, number_of_stds=1)
    lower_bound, upper_bound = peak_bounds
    print("Bortfeld horizontal pixel is {0}. lower/upper bound = {1}/{2}".format(bortfeld_horizontal_coord, lower_bound, upper_bound))
    # For the time being, use a symmetric interval with the largest unc
    unc_bortfeld_horizontal_coord = max(lower_bound, upper_bound)
    
    change_in_coord = round(bortfeld_horizontal_coord) - initial_bragg_peak_horizontal_coord
    
    bragg_peak_vertical_coord = beam_center_positions[initial_bragg_peak_horizontal_coord_index + change_in_coord]
    unc_bragg_peak_vertical_coord = beam_center_errors[initial_bragg_peak_horizontal_coord_index + change_in_coord]
    
    print("PIXEL BORTFELD FIT PARAMS: {}".format(bortfeld_fit['bortfeld_fit_p']))
    print("PIXEL BORTFELD PARAM COVARIANCES: {}".format(fit_parameters_covariance))
    
    return (bortfeld_horizontal_coord, bragg_peak_vertical_coord), (unc_bortfeld_horizontal_coord, unc_bragg_peak_vertical_coord), plot_byte_string # Uncertainty not rounded appropriately yet, nor has horizontal coord itself.