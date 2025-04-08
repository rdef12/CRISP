import numpy as np
import cv2 as cv
from scipy.optimize import curve_fit, OptimizeWarning
import warnings
import matplotlib.pyplot as plt
from itertools import product
import math
import io
import base64

from src.modified_pybragg import *
from src.uncertainty_functions import *

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

def least_squares_fitting_procedure(x_data, y_data, y_uncertainties):
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


def super_gaussian(w, w0, a, sgm, n):
    return (a/sgm) * np.exp(-(0.5 * ((w - w0)/sgm)**2)**n)


def super_gaussian_with_background_noise(w, w0, a, sgm, n, background):
    return (a/sgm) * np.exp(-(0.5 * ((w - w0)/sgm)**2)**n) + background



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
        
    first_lower_bounds = [-np.inf,  # No lower bound for the 1st parameter (center)
                    -np.inf,  # No lower bound for the 2nd parameter (scale)
                    -np.inf,  # No lower bound for the 3rd parameter (sigma)
                    1]      # lower bound for n

    first_upper_bounds = [np.inf,   # No upper bound for the 1st parameter (center)
                    np.inf,   # No upper bound for the 2nd parameter (scale)
                    np.inf,   # No upper bound for the 3rd parameter (sigma)
                    np.inf]  # upper bound for n (sub Gaussian or Gaussian only!)
    
    second_lower_bounds = [-np.inf,  # No lower bound for the 1st parameter (center)
                    -np.inf,  # No lower bound for the 2nd parameter (scale)
                    -np.inf,  # No lower bound for the 3rd parameter (sigma)
                    1, # lower bound for n
                    -np.inf] # No lower bound for the 5th parameter (background)

    second_upper_bounds = [np.inf,   # No upper bound for the 1st parameter (center)
                    np.inf,   # No upper bound for the 2nd parameter (scale)
                    np.inf,   # No upper bound for the 3rd parameter (sigma)
                    np.inf,  # upper bound for n (sub Gaussian or Gaussian only!)
                    np.inf]  # No upper bound for the 5th parameter (background)

    try:
        super_gauss_paramters, parameter_cov = curve_fit(super_gaussian, pixel_vertical_coords, column_of_brightness_vals,
                                            p0 = (gaussian_center_estimate,
                                                    gaussian_scale_estimate,
                                                    gaussian_sigma_estimate,
                                                    1),
                                            sigma=column_of_brightness_errors,
                                            absolute_sigma=True,
                                            bounds=(first_lower_bounds, first_upper_bounds))
        
        column_of_brightness_vals += background_estimate
        super_gauss_paramters, parameter_cov = curve_fit(super_gaussian_with_background_noise, pixel_vertical_coords, column_of_brightness_vals,
                                            p0 = (super_gauss_paramters[0],
                                                    super_gauss_paramters[1],
                                                    super_gauss_paramters[2],
                                                    super_gauss_paramters[3],
                                                    background_estimate),
                                            sigma=column_of_brightness_errors,
                                            absolute_sigma=True,
                                            bounds=(second_lower_bounds, second_upper_bounds))
        
        error_on_super_gaussian_center = np.sqrt(parameter_cov[0, 0])
        
        num_of_dof = len(pixel_vertical_coords) - 5 # 5 fit params
        fitted_pixel_values = super_gaussian_with_background_noise(pixel_vertical_coords, *super_gauss_paramters)
        reduced_chi_squared = chi_squared_function(column_of_brightness_vals, column_of_brightness_errors, fitted_pixel_values) / num_of_dof
        
        successful_fit = True
        return super_gauss_paramters, error_on_super_gaussian_center, reduced_chi_squared, successful_fit

    except RuntimeError as e:
        successful_fit = False
        return float("nan"), float("nan"), float("nan"),  successful_fit
    

def fit_beam_profile_along_full_roi(channel, channel_std, h_bounds, v_bounds, show_fit_qualities: bool=False,
                                    save_best_fit_data: bool=False):
    try:
        (background_brightness, _, _, _) = cv.minMaxLoc(channel[v_bounds[0]: v_bounds[1] + 1, h_bounds[0]: h_bounds[1] + 1])
        
        roi_horizontal_coords = np.arange(h_bounds[0], h_bounds[1], 1)
        total_profile_brightness, unc_total_profile_brightness = [], []

        fitted_parameters_array = np.empty((0, 5), float) # FOR SUPER GAUSSIAN FITTING
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

    gaussian_center, scale_factor, sigma, n, background_noise = fitted_parameters # FOR SUPER GAUSSIAN FITTING
    
    pixel_height_linspace = np.linspace(pixel_vertical_coords[0], pixel_vertical_coords[-1] + 1, 1000)
    fitted_pixel_values = super_gaussian_with_background_noise(pixel_height_linspace, gaussian_center, scale_factor, sigma, n, background_noise) # FOR SUPER GAUSSIAN FITTING
    
    # Compute residuals
    residuals = column_of_brightness_vals - super_gaussian_with_background_noise(pixel_vertical_coords, gaussian_center, scale_factor, sigma, n, background_noise)
    
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

    fitted_line_parameters, fitted_parameter_uncertainties = least_squares_fitting_procedure(horizontal_coords, beam_center_vertical_coords, beam_center_errors)
    predicted_beam_centers = linear_function(horizontal_coords, fitted_line_parameters)  
    chi_squared_reduced = chi_squared_function(beam_center_vertical_coords, beam_center_errors, predicted_beam_centers) / (len(horizontal_coords) - 2)
    
    print("\n\ntan alpha = {}".format(fitted_line_parameters[0]))
    print("\n\nuncertainty in tan alpha = {}".format(fitted_parameter_uncertainties[0]))
    
    # TODO - edit legend label to specify if error bars are renormalised or not
    if chi_squared_reduced > 10:
        beam_center_errors *= np.sqrt(chi_squared_reduced) # renormalisation of error bars! - clearly underestimated uncertainties
        # REPEAT CHI SQUARED MINIMISATION
        fitted_line_parameters, fitted_parameter_uncertainties = least_squares_fitting_procedure(horizontal_coords, beam_center_vertical_coords, beam_center_errors)
        predicted_beam_centers = linear_function(horizontal_coords, fitted_line_parameters)
        chi_squared_reduced = chi_squared_function(beam_center_vertical_coords, beam_center_errors, predicted_beam_centers) / (len(horizontal_coords) - 2)
        
        print("\n\nUpdated tan alpha = {}".format(fitted_line_parameters[0]))
        print("\n\nUpdated uncertainty in tan alpha = {}".format(fitted_parameter_uncertainties[0]))
    
    fitted_angle = np.arctan(fitted_line_parameters[0])
    fitted_tan_angle_uncertainty = fitted_parameter_uncertainties[0]
    unc_fitted_angle = fitted_tan_angle_uncertainty * np.cos(fitted_angle)**2
    
    print("\n\nuncertainty in angle = {}".format(unc_fitted_angle))

    fitted_angle, unc_fitted_angle = np.rad2deg(fitted_angle), np.rad2deg(unc_fitted_angle)
    
    fitted_label = r"$\alpha = $" + f"{fitted_angle:.3g}" + " \u00B1 " + f"{unc_fitted_angle:.3g}" + \
    "\u00B0" + "\n" + r"Reduced $\chi^2$ = " + str(round(chi_squared_reduced, 2))
    
    
    fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]}, figsize=(8, 6), sharex=True)
    axs[0].plot(horizontal_coords, predicted_beam_centers, color="red", label=fitted_label)
    
    axs[0].errorbar(horizontal_coords, beam_center_vertical_coords, beam_center_errors, color="black", marker="x", label="Experimental Data",
                    ecolor="blue", ls="none")
    axs[0].set_xlabel("Pixel's Horizonal Image Coordinate")
    axs[0].set_ylabel("Vertical Coordinate of Beam Center Pixels")
    axs[0].legend(**LEGEND_CONFIG)
    plt.grid()
    
    residuals = beam_center_vertical_coords - predicted_beam_centers
    axs[1].scatter(horizontal_coords, residuals, color="black", s=8, label="Residuals")
    axs[1].axhline(0, color='red', linestyle='dashed')
    axs[1].set_xlabel("Pixel's Horizonal Image Coordinate")
    axs[1].set_ylabel("Residuals")
    axs[1].grid()
    
    fig.tight_layout()
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


def locate_bragg_peak_in_image(x_positions, beam_center_positions, beam_center_errors, fit_parameters,
                               total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi,
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
    
    bortfeld_fit = fitBP(x_positions_slice, total_brightness_slice, unc_brightness_slice)
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
    peak_bounds = find_peak_position_uncertainty(x_positions, bortfeld_fit['bortfeld_fit_p'], bortfeld_fit_uncertainties, points_per_bin=100, number_of_stds=1)
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


def plot_physical_units_ODR_bortfeld(bragg_peak_depth, distances, distance_uncertainties, brightnesses, brightness_uncertainties,
                                     left_fit_window: int, right_fit_window: int):
    """
    Fit window is used to specify how tightly around the peak the ODR fit should be
    """
    
    print("\n\nMinimum distance travelled through scintillator is {}".format(np.min(distances)))
    print("\n\nMaximum distance travelled through scintillator is {}".format(np.max(distances)))
    
    if len(distances) != len(np.unique(distances)):
        unique_distances, unique_indices = np.unique(distances, return_index=True)
        distances = np.array(distances)[unique_indices]
        distance_uncertainties = np.array(distance_uncertainties)[unique_indices]    
        brightnesses = np.array(brightnesses)[unique_indices]    
        brightness_uncertainties = np.array(brightness_uncertainties)[unique_indices]
        
    print("\n\nLength of distances array is {}".format(len(distances)))
    print("\n\nLength of brightnesses array is {}".format(len(brightnesses)))
    print("\n\nLength of distance uncertainties array is {}".format(len(distance_uncertainties)))
    print("\n\nLength of brightness uncertainties array is {}".format(len(brightness_uncertainties)))
    
    # Find index of where distances array element is closest to the bragg peak depth
    bragg_peak_index = np.argmin(np.abs(distances - bragg_peak_depth))
    # Apply plot_window around this index to fit around the peak
    
    start_index = max(0, bragg_peak_index - left_fit_window)
    end_index = min(len(distances), bragg_peak_index + right_fit_window + 1)
    
    distances = distances[start_index:end_index]
    distance_uncertainties = distance_uncertainties[start_index:end_index]
    brightnesses = brightnesses[start_index:end_index]
    brightness_uncertainties = brightness_uncertainties[start_index:end_index]
    
    # Fit the Bortfeld function using ODR
    fit_parameters, fit_parameters_uncertainties, true_uncertainties = fit_bortfeld_odr(
        distances, brightnesses, distance_uncertainties, brightness_uncertainties
    )

    # Find the Bragg peak position and uncertainties
    bragg_peak_position_arguement, bragg_peak_position = find_peak_of_bortfeld(distances, fit_parameters)
    lower_uncertainty_peak_position, upper_uncertainty_peak_position = find_peak_position_uncertainty(
        distances, fit_parameters, fit_parameters_uncertainties, points_per_bin=100
    )
    print(f"Bragg peak position {bragg_peak_position} + {upper_uncertainty_peak_position} - {lower_uncertainty_peak_position}")

    # Find the range and uncertainties
    range_argument, range = find_range(distances, fit_parameters, points_per_bin=100)
    lower_uncertainty, upper_uncertainty = (0, 0)  # Placeholder for range uncertainty calculation
    print(f"Range {range} + {upper_uncertainty} - {lower_uncertainty}")

    # Generate fitted curve
    fitted_distances = np.linspace(min(distances), max(distances), 1000)
    fitted_brightnesses = bortfeld(fitted_distances, *fit_parameters)

    # Plot the data with error bars and the fitted curve
    plt.plot(fitted_distances, fitted_brightnesses, color='red', label='Fitted Bortfeld Function')
    
    plt.step(distances, brightnesses, where='mid')
    # Suppress markers for error bars only
    plt.errorbar(
        distances, brightnesses, 
        xerr=distance_uncertainties, yerr=brightness_uncertainties, 
        fmt='', color='black', ecolor='blue', label='Experimental Data', ms=3
    )
    
    # Add labels, legend, and grid
    plt.xlabel("Distance travelled through Scintillator (mm)")
    plt.ylabel("Total Profile Intensity")
    plt.legend(**LEGEND_CONFIG)
    plt.grid()

    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    plot_byte_string = base64.b64encode(buf.read()).decode('utf-8')
    return plot_byte_string
    
    
    