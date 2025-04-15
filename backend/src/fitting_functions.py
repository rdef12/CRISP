import numpy as np
import cv2 as cv
from scipy.optimize import curve_fit, OptimizeWarning
import warnings
import matplotlib.pyplot as plt
from itertools import product
import math
import io
import base64
import ruptures as rpt

from src.modified_pybragg import *
from src.uncertainty_functions import *
from src.database.CRUD import CRISP_database_interaction as cdi

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
        
        super_gauss_paramters_uncertainties = np.sqrt(np.diag(parameter_cov))
        
        num_of_dof = len(pixel_vertical_coords) - 5 # 5 fit params
        fitted_pixel_values = super_gaussian_with_background_noise(pixel_vertical_coords, *super_gauss_paramters)
        reduced_chi_squared = chi_squared_function(column_of_brightness_vals, column_of_brightness_errors, fitted_pixel_values) / num_of_dof
        
        successful_fit = True
        return super_gauss_paramters, super_gauss_paramters_uncertainties, reduced_chi_squared, successful_fit

    except RuntimeError as e:
        successful_fit = False
        return float("nan"), float("nan"), float("nan"),  successful_fit
    

def fit_beam_profile_along_full_roi(camera_analysis_id: int, fit_context: str, channel, channel_std, h_bounds, v_bounds, show_fit_qualities: bool=False,
                                    save_plots_to_database: bool=False):
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
            
            fitted_parameters, unc_fitted_parameters, reduced_chi_squared, success = fit_gaussian_to_beam_profile(pixel_vertical_coords, column_of_brightness_vals,
                                                                                                                    column_of_brightness_errors, background_brightness)
            if not success:
                failed_fits.append(index)
                continue # Should start from next index of for loop, not appending these beam center positions
            
            reduced_chi_squared_array.append(reduced_chi_squared)
            fitted_parameters_array = np.vstack((fitted_parameters_array, fitted_parameters))
            error_on_beam_center = unc_fitted_parameters[0]
            beam_center_error_array = np.append(beam_center_error_array, error_on_beam_center)
            total_profile_brightness.append(np.sum(column_of_brightness_vals))
            unc_total_profile_brightness.append(normal_addition_in_quadrature(column_of_brightness_errors))
            
        roi_horizontal_coords = np.delete(roi_horizontal_coords, failed_fits) # Failed fits deleted from array - no data added when the fit failed (so would be differences in array lengths without this fix)
        print("\n\n\nThe number of Gaussian fits which failed is {}\n\n\n".format(len(failed_fits)))
        
        if save_plots_to_database:
            plot_reduced_chi_squared_values(camera_analysis_id, fit_context, roi_horizontal_coords,
                                            reduced_chi_squared_array, show_plot=show_fit_qualities)
            
            index_of_worst_accepted_fit = np.argmax(reduced_chi_squared_array)
            index_of_best_accepted_fit = np.argmin(reduced_chi_squared_array)
            
            plot_beam_profile(camera_analysis_id, fit_context, channel, channel_std, roi_horizontal_coords[index_of_best_accepted_fit], v_bounds, background_brightness, np.min(reduced_chi_squared_array),
                                                            profile_type="best_fit", show_plot=show_fit_qualities)
            plot_beam_profile(camera_analysis_id, fit_context, channel, channel_std, roi_horizontal_coords[index_of_worst_accepted_fit], v_bounds, background_brightness, np.max(reduced_chi_squared_array),
                                                            profile_type="worst_fit", show_plot=show_fit_qualities)
            
            # best_fit_horizontal_coord = roi_horizontal_coords[index_of_best_accepted_fit]
            # worst_fit_horizontal_coord = roi_horizontal_coords[index_of_worst_accepted_fit]
            # overlayed_average_image_bytes = render_best_worst_fit_locations(channel, best_fit_horizontal_coord, worst_fit_horizontal_coord, v_bounds)
            # plot_byte_strings = [rcs_plot_bytes, best_fit_gaussian_plot_bytes, worst_fit_gaussian_plot_bytes, overlayed_average_image_bytes]
        
        return roi_horizontal_coords, fitted_parameters_array, beam_center_error_array, reduced_chi_squared_array, total_profile_brightness, unc_total_profile_brightness
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


def plot_beam_profile(camera_analysis_id: int, fit_context: str, channel, channel_std, horizontal_coord, v_bounds,
                      global_background_estimate, reduced_chi_squared, profile_type: str=None, show_plot: bool=False):
    
    pixel_vertical_coords, column_of_brightness_vals, column_of_brightness_errors = extract_beam_profile(channel, channel_std, horizontal_coord, v_bounds)
    fitted_parameters, unc_fitted_parameters, reduced_chi_squared, _ = fit_gaussian_to_beam_profile(pixel_vertical_coords, column_of_brightness_vals, column_of_brightness_errors,
                                                                                                    global_background_estimate)
    chi_squared = reduced_chi_squared * (len(pixel_vertical_coords) - 5) # 5 fit params

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
    
    axs[0].errorbar(gaussian_center, super_gaussian_with_background_noise(gaussian_center, gaussian_center, scale_factor, sigma, n, background_noise),
                    xerr=unc_fitted_parameters[0], fmt="o", color="green", ecolor="purple", label="Beam Center", zorder=11, ms=3)
                    
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
    plot_bytes = buf.read()
    parameter_labels = ["Gaussian Center", "Scale Factor", "Sigma", "Sub-Gaussian Exponent", "Background Brightness"]
    parameter_values = [float(gaussian_center), float(scale_factor), float(sigma), float(n), float(background_noise)]
    parameter_uncertainties = [float(x) for x in unc_fitted_parameters]
    
    cdi.add_camera_analysis_plot(camera_analysis_id, f"{fit_context}_{profile_type}_gaussian", plot_bytes, "svg",
                                 description=f"Plot showing '{profile_type.lower()}' Gaussian fit in {fit_context}",
                                 parameter_labels=parameter_labels, parameter_values=parameter_values,
                                 parameter_uncertainties=parameter_uncertainties, chi_squared=float(chi_squared),
                                 number_of_data_points=len(pixel_vertical_coords))

def plot_reduced_chi_squared_values(camera_analysis_id: int, fit_context: str, roi_horizontal_coords,
                                    reduced_chi_squared_array, show_plot: bool=False):
    
    plt.xlabel("Horizontal Pixel Coordinate")
    plt.ylabel(r"Gaussian Profile $\chi^{2}_R$")
    plt.grid()
    label = r"Best $\chi^{2}_R$: " + "{:.3g} \n".format(np.min(reduced_chi_squared_array)) + r"Worst $\chi^{2}_R$: " + "{:.3g}".format(np.max(reduced_chi_squared_array))
    plt.scatter(roi_horizontal_coords, reduced_chi_squared_array, color="red", s=2, label=label)
    plt.legend(**LEGEND_CONFIG)
    if show_plot:
        plt.show()
    
    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    plot_bytes = buf.read()
    
    cdi.add_camera_analysis_plot(camera_analysis_id, f"{fit_context}_all_gaussian_rcs_values", plot_bytes, "svg",
                                 description=f"Plot showing the reduced chi squareds of all fitted {fit_context} Gaussians")


def extract_incident_beam_angle(camera_analysis_id: int, horizontal_coords, beam_center_vertical_coords, beam_center_errors, 
                                show_angle_plot: bool=True, save_angle_plot: bool=False):
    
    # Pelt, Biseng, BottomUp, Dynp, Window alogirthms available
    signal = np.column_stack((horizontal_coords, beam_center_vertical_coords))
    # models are l1, l2, linear rbf, normal, ar 
    model = "linear"
    algo = rpt.Dynp(model=model, jump=5).fit(signal)
    change_points = algo.predict(n_bkps=1)[:-1] # Remove end point change point
    
    # plt.plot(signal[:, 0], signal[:, 1], color="black", label="Normalised Signal")
    # for change_point in change_points:
    #     plt.axvline(x=signal[:, 0][change_point-1], color="red", linestyle="--", label="Change Point")
    # plt.show()
    # plt.close()
    
    angle_fitting_range = slice(0, change_points[0])
    horizontal_coords = horizontal_coords[angle_fitting_range]
    beam_center_vertical_coords = beam_center_vertical_coords[angle_fitting_range]
    beam_center_errors = beam_center_errors[angle_fitting_range]

    fitted_line_parameters, fitted_parameter_uncertainties = least_squares_fitting_procedure(horizontal_coords, beam_center_vertical_coords, beam_center_errors)
    predicted_beam_centers = linear_function(horizontal_coords, fitted_line_parameters)  
    chi_squared = chi_squared_function(beam_center_vertical_coords, beam_center_errors, predicted_beam_centers)
    chi_squared_reduced =  chi_squared / (len(horizontal_coords) - 2)
    
    print("\n\ntan alpha = {}".format(fitted_line_parameters[0]))
    print("\n\nuncertainty in tan alpha = {}".format(fitted_parameter_uncertainties[0]))
    
    # TODO - edit legend label to specify if error bars are renormalised or not
    # if chi_squared_reduced > 10:
    #     beam_center_errors *= np.sqrt(chi_squared_reduced) # renormalisation of error bars! - clearly underestimated uncertainties
    #     # REPEAT CHI SQUARED MINIMISATION
    #     fitted_line_parameters, fitted_parameter_uncertainties = least_squares_fitting_procedure(horizontal_coords, beam_center_vertical_coords, beam_center_errors)
    #     predicted_beam_centers = linear_function(horizontal_coords, fitted_line_parameters)
    #     chi_squared_reduced = chi_squared_function(beam_center_vertical_coords, beam_center_errors, predicted_beam_centers) / (len(horizontal_coords) - 2)
        
    #     print("\n\nUpdated tan alpha = {}".format(fitted_line_parameters[0]))
    #     print("\n\nUpdated uncertainty in tan alpha = {}".format(fitted_parameter_uncertainties[0]))
    
    fitted_angle = np.arctan(fitted_line_parameters[0])
    fitted_tan_angle_uncertainty = fitted_parameter_uncertainties[0]
    unc_fitted_angle = fitted_tan_angle_uncertainty * np.cos(fitted_angle)**2
    
    print("\n\nuncertainty in angle = {}".format(unc_fitted_angle))

    fitted_angle, unc_fitted_angle = np.rad2deg(fitted_angle), np.rad2deg(unc_fitted_angle)
    
    leading_order_error = 10 ** np.floor(np.log10(np.abs(unc_fitted_angle).max())) # same OOM for both coords - ideal?
    fitted_angle = np.round(fitted_angle / leading_order_error) * leading_order_error
    unc_fitted_angle = np.round(unc_fitted_angle / leading_order_error) * leading_order_error
    
    fitted_label = r"$\alpha = $" + f"{fitted_angle}" + " \u00B1 " + f"{unc_fitted_angle}" + \
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
    plot_bytes = buf.read()
    
    parameter_labels = ["Slope", "Offset"]
    parameter_values = [float(x) for x in fitted_line_parameters]
    cdi.add_camera_analysis_plot(camera_analysis_id, f"angle_plot", plot_bytes, "svg",
                                 description=f"Plot showing beam's angle when seen in the plane of the scintillator normal to the camera optical axis",
                                 parameter_labels=parameter_labels, parameter_values=parameter_values, number_of_data_points=len(horizontal_coords),
                                 chi_squared=float(chi_squared))
    
    return fitted_angle, unc_fitted_angle


def locate_bragg_peak_in_image(camera_analysis_id: int, x_positions, beam_center_positions, beam_center_errors, fit_parameters,
                               total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi,
                               show_scintillation_plot: bool=False):
    
    initial_bragg_peak_horizontal_coord_index = np.argmax(total_brightness_along_vertical_roi)
    initial_bragg_peak_horizontal_coord = x_positions[initial_bragg_peak_horizontal_coord_index]
    
    threshold_fraction = 1 / 3
    initial_brightness = total_brightness_along_vertical_roi[0]
    peak_brightness = np.max(total_brightness_along_vertical_roi)
    peak_threshold_condition = initial_brightness  + (peak_brightness - initial_brightness) * threshold_fraction
    within_peak_threshold = np.where(total_brightness_along_vertical_roi >= peak_threshold_condition)[0]
    peak_range = slice(max(0, within_peak_threshold[0]), min(len(x_positions), within_peak_threshold[-1] + 1))
    
    x_positions_slice = x_positions[peak_range]
    total_brightness_slice = total_brightness_along_vertical_roi[peak_range]
    unc_brightness_slice = unc_total_brightness_along_vertical_roi[peak_range]
    
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
    plot_bytes = buf.read()
    
    parameter_labels = ["Normalisation Constant (A)", "80% Distal Range (R80)", "Sigma", "Bragg-Kleeman Exponent (p)", "Scale factor (K)"]
    parameter_values = [float(x) for x in bortfeld_fit['bortfeld_fit_p']]
    parameter_uncertainties = [float(x) for x in bortfeld_fit_uncertainties]
    
    cdi.add_camera_analysis_plot(camera_analysis_id, f"pixel_bortfeld_fit", plot_bytes, "svg",
                                 description=f"Plot showing a bortfeld function fitted to the on-axis pixel scintillation light distribution",
                                 parameter_labels=parameter_labels, parameter_values=parameter_values, parameter_uncertainties=parameter_uncertainties,
                                 number_of_data_points=len(x_positions_slice), chi_squared=float(chi_squared))
    
    bortfeld_horizontal_coord = z[np.argmax(curve)]
    # peak_bounds = find_peak_position_uncertainty(x_positions, bortfeld_fit['bortfeld_fit_p'], bortfeld_fit_uncertainties, points_per_bin=100, number_of_stds=1)
    # lower_bound, upper_bound = peak_bounds
    # For the time being, use a symmetric interval with the largest unc
    # unc_bortfeld_horizontal_coord = max(lower_bound, upper_bound)
    
    unc_bortfeld_horizontal_coord = compute_error_on_bortfeld_peak(z, bortfeld_fit['bortfeld_fit_p'], bortfeld_fit['bortfeld_fit_cov'])
    
    change_in_coord = round(bortfeld_horizontal_coord) - initial_bragg_peak_horizontal_coord
    
    bragg_peak_vertical_coord = beam_center_positions[initial_bragg_peak_horizontal_coord_index + change_in_coord]
    unc_bragg_peak_vertical_coord = beam_center_errors[initial_bragg_peak_horizontal_coord_index + change_in_coord]
    
    return (bortfeld_horizontal_coord, bragg_peak_vertical_coord), (unc_bortfeld_horizontal_coord, unc_bragg_peak_vertical_coord) # Uncertainty not rounded appropriately yet, nor has horizontal coord itself.


def overlay_bragg_peak_coord(camera_analysis_id, averaged_image, bragg_peak_coord):
    bragg_peak_coord = tuple(map(int, bragg_peak_coord))
    image_with_bragg_peak = np.copy(averaged_image)
    image_with_bragg_peak = cv.cvtColor(image_with_bragg_peak, cv.COLOR_GRAY2BGR)
    image_with_bragg_peak = cv.circle(image_with_bragg_peak, bragg_peak_coord, 10, (0, 0, 255), -1)  # args = radius, colour, thickness
    
    text = "Overlayed Bragg peak position"
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 3
    color = (0, 0, 255)
    thickness = 2
    position = (50, 50)  # x=10, y=30 pixels from top-left
    image = cv.putText(image_with_bragg_peak, text, position, font, font_scale, color, thickness, cv.LINE_AA)
    
    _, image_bytes = cv.imencode('.png', image_with_bragg_peak)  # Encode the image as a PNG
    cdi.add_camera_analysis_plot(camera_analysis_id, f"overlayed_bragg_peak_coord", image_bytes, "png",
                                 description=f"Overlayed Bragg peak coordinate identified onto averaged image")
    return image_bytes

def overlay_beam_center_coords(camera_analysis_id, averaged_image, beam_center_coords):
    
    image_with_beam_centers_overlayed = np.copy(averaged_image)
    image_with_beam_centers_overlayed = cv.cvtColor(image_with_beam_centers_overlayed, cv.COLOR_GRAY2BGR)
    for coord in beam_center_coords:
        coord = tuple(map(int, coord))
        image_with_beam_centers_overlayed = cv.circle(image_with_beam_centers_overlayed, coord, 3, (0, 0, 255), -1)
        
    text = "Overlayed beam centers"
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 3
    color = (0, 0, 255)
    thickness = 2
    position = (50, 50)  # x=10, y=30 pixels from top-left
    image = cv.putText(image_with_beam_centers_overlayed, text, position, font, font_scale, color, thickness, cv.LINE_AA)

    _, image_bytes = cv.imencode('.png', image_with_beam_centers_overlayed)  # Encode the image as a PNG
    cdi.add_camera_analysis_plot(camera_analysis_id, f"overlayed_beam_center_coords", image_bytes, "png",
                                 description=f"Overlayed beam center coordinates on the averaged image")
    return image_bytes

def fit_physical_units_ODR_bortfeld(camera_analysis_id, distances, distance_uncertainties, brightnesses, brightness_uncertainties):
    
    cdi.delete_physical_bortfeld_plots_by_camera_analysis_id(camera_analysis_id)
    print("\n\nMinimum distance travelled through scintillator is {}".format(np.min(distances)))
    print("\n\nMaximum distance travelled through scintillator is {}".format(np.max(distances)))
    
    if len(distances) != len(np.unique(distances)):
        unique_distances, unique_indices = np.unique(distances, return_index=True)
        distances = np.array(distances)[unique_indices]
        distance_uncertainties = np.array(distance_uncertainties)[unique_indices]
        brightnesses = np.array(brightnesses)[unique_indices]    
        brightness_uncertainties = np.array(brightness_uncertainties)[unique_indices]
    
    threshold_fraction = 1 / 3
    initial_brightness = brightnesses[0]
    peak_brightness = np.max(brightnesses)
    peak_threshold_condition = initial_brightness  + (peak_brightness - initial_brightness) * threshold_fraction
    within_peak_threshold = np.where(brightnesses >= peak_threshold_condition)[0]
    peak_range = slice(max(0, within_peak_threshold[0]), min(len(distances), within_peak_threshold[-1] + 1))
    print(f"\n\nPeak range is {peak_range}")
    
    distances = distances[peak_range]
    distance_uncertainties = distance_uncertainties[peak_range]
    brightnesses = brightnesses[peak_range]
    brightness_uncertainties = brightness_uncertainties[peak_range]
    
    print("Max dist uncertainty in this range is {}".format(np.max(distance_uncertainties)))
    print("Min dist uncertainty in this range is {}".format(np.min(distance_uncertainties)))
    
    # Fit the Bortfeld function using ODR
    fit_parameters, fit_parameters_covariance, _, reduced_chi_squared = fit_bortfeld_odr(
        distances, brightnesses, distance_uncertainties, brightness_uncertainties)
    
    print(f"\n\n\n R80 = {fit_parameters[2]} +/- {np.sqrt(np.diag(fit_parameters_covariance))[2]}")

    # Find the Bragg peak position and uncertainties
    bragg_peak_position = find_peak_of_bortfeld(distances, fit_parameters)
    bragg_peak_position_error = compute_error_on_bortfeld_peak(distances, fit_parameters, fit_parameters_covariance)
    print("\n\nBragg peak position is {}".format(bragg_peak_position))
    print("\n\nBragg peak position uncertainty is {}".format(bragg_peak_position_error))
    
    # lower_uncertainty_peak_position, upper_uncertainty_peak_position = find_peak_position_uncertainty(
    #     distances, fit_parameters, fit_parameters_uncertainties, points_per_bin=100)
    
    return distances, distance_uncertainties, brightnesses, brightness_uncertainties, fit_parameters, fit_parameters_covariance, reduced_chi_squared

def compute_range_and_uncertainty(camera_analysis_id, distances, fit_parameters, fit_parameter_covariance):
    range = find_range(distances, fit_parameters, points_per_bin=1000)
    range_uncertainty = compute_error_on_mean_range(distances, fit_parameters, fit_parameter_covariance)
    print("\n\nRange is {}".format(range))
    print("\n\nRange uncertainty is {}".format(range_uncertainty))
    
    cdi.update_range(camera_analysis_id, float(range))
    cdi.update_range_uncertainty(camera_analysis_id, float(range_uncertainty))
    return range, range_uncertainty

def plot_physical_units_ODR_bortfeld(camera_analysis_id, distances, distance_uncertainties, brightnesses, brightness_uncertainties,
                                     num_of_failed_pinpoints):
    try:
        distances, distance_uncertainties, brightnesses, brightness_uncertainties, \
            fit_parameters, fit_parameters_covariance, reduced_chi_squared = fit_physical_units_ODR_bortfeld(camera_analysis_id, distances, distance_uncertainties, brightnesses, brightness_uncertainties)
        
        range, unc_range = compute_range_and_uncertainty(camera_analysis_id, distances, fit_parameters, fit_parameters_covariance)
        
        # Generate fitted curve
        fitted_brightnesses = bortfeld(distances, *fit_parameters)
        plt.plot(distances, fitted_brightnesses, color='red', 
             label=('Fitted Bortfeld Function \n' + fr"Reduced $\chi^2$ = {reduced_chi_squared:.3g}"))
        
        # plt.step(distances, brightnesses, where='mid')
        # Suppress markers for error bars only
        failed_points_label = f"\nNumber of failed pinpoints: {num_of_failed_pinpoints}" if num_of_failed_pinpoints > 0 else ""
        range_label = f"\n Range = {range:.3g} \u00B1 {unc_range:.3g}"
        plt.errorbar(
            distances, brightnesses, 
            xerr=distance_uncertainties, yerr=brightness_uncertainties,
            fmt='', color='black', ecolor='blue', label=f'Experimental Data {range_label} {failed_points_label}', ms=3)
        
        # Add labels, legend, and grid
        plt.xlabel("Distance travelled through Scintillator (mm)")
        plt.ylabel("Total Profile Intensity")
        plt.legend(**LEGEND_CONFIG)
        plt.grid()

        buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
        plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
        plt.close()
        buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
        plot_bytes = buf.read()
        
        parameter_labels = ["Normalisation Constant (A)", "80% Distal Range (R80)", "Sigma", "Bragg-Kleeman Exponent (p)", "Scale factor (K)"]
        parameter_values = [float(x) for x in fit_parameters]
        fit_parameters_uncertainties = np.sqrt(np.diag(fit_parameters_covariance))
        parameter_uncertainties = [float(x) for x in fit_parameters_uncertainties]
        cdi.add_camera_analysis_plot(camera_analysis_id, "physical_bortfeld_fit", plot_bytes, "svg",
                                    description=f"Plot showing a bortfeld function ODR fitting to the beam axis scintillation light distribution in physical units",
                                    parameter_labels=parameter_labels, parameter_values=parameter_values, parameter_uncertainties=parameter_uncertainties)
        return None
    except Exception as e:
        raise Exception("Error in plotting physical units ODR Bortfeld: ", e)
    
    