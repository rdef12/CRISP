b"""
Takes camera objects as input (two at first - AR and HQ) - the general system
should be ready to use the top AR cam at the Christie.

For each camera
1) Image averaging invoked here (save to database?)
2) Automated edge detection employed
3) Bragg peak pixel identified (contained in a get_bragg_peak_pixel script)

Between pairs of camera - Bragg peak 3D pinpointing performed (function called in perform analysis does this)

fit along roi simplified for now - ability to save data removed (beam_run object and cam type removed from arguments)

Could change the order of distortion correction - could do right at the end.

I think there should be file responses accessible for debugging purposes
"""
import src.image_processing as image_processing
from src.automated_roi import get_automated_roi
from src.fitting_functions import *
from src.database.CRUD import CRISP_database_interaction as cdi
import numpy as np

def rotate_bragg_peak_into_original_coords(rotated_bragg_peak_coord, error_on_fitted_bragg_peak, inverse_rotation_matrix):
    # We need the bragg peak to be in terms of the coordinates of the original image (not the rotated one)
    homogenous_rotated_bragg_peak = np.append(rotated_bragg_peak_coord, 1)
    bragg_peak_coord = (inverse_rotation_matrix @ homogenous_rotated_bragg_peak.T)
    # error also needs rotating back to original coords! - slicing extracts rotation matrix from the affine transformation matrix
    error_on_fitted_bragg_peak = (inverse_rotation_matrix[:, :2] @ np.array(error_on_fitted_bragg_peak).T) 
    return bragg_peak_coord, error_on_fitted_bragg_peak


def round_bragg_peak_coord(bragg_peak_coord, error_on_bragg_peak_coord):
    # Bragg peak coord rounded to leading order of uncertainty
    leading_order_error = 10 ** np.floor(np.log10(np.abs(error_on_bragg_peak_coord).max())) # same OOM for both coords - ideal?
    bragg_peak_coord = np.round(bragg_peak_coord / leading_order_error) * leading_order_error
    error_on_bragg_peak_coord = np.round(error_on_bragg_peak_coord / leading_order_error) * leading_order_error
    return bragg_peak_coord, error_on_bragg_peak_coord

def apply_rotations_for_analysis(average_image, average_rounded_image, brightness_error, scintillator_edges, rotation_angle):
    
    original_scintillation_edges = scintillator_edges.copy()
    match rotation_angle:
        case 90:
            rotation_flag = cv.ROTATE_90_CLOCKWISE
            scintillator_edges[1] = original_scintillation_edges[0][::-1]
            scintillator_edges[0] = (average_rounded_image.shape[0] - 1 - original_scintillation_edges[1])[::-1]
        case 180:
            rotation_flag = cv.ROTATE_180
            scintillator_edges = [np.array(average_rounded_image.shape[i-1] - 1 - edge)[::-1] for i, edge in enumerate(scintillator_edges)]
        case 270:
            rotation_flag = cv.ROTATE_90_COUNTERCLOCKWISE
            scintillator_edges[1] = average_rounded_image.shape[1] - 1 - original_scintillation_edges[0][::-1]
            scintillator_edges[0] = original_scintillation_edges[1][::-1]
        case 0:
            return average_image, average_rounded_image, brightness_error, scintillator_edges
        
    average_image = cv.rotate(average_image, rotation_flag)
    average_rounded_image = cv.rotate(average_rounded_image, rotation_flag)
    brightness_error = cv.rotate(brightness_error, rotation_flag)
    return average_image, average_rounded_image, brightness_error, scintillator_edges


def get_beam_direction_from_the_left(image_beam_direction, average_image, average_rounded_image, brightness_error, scintillator_edges):
    match image_beam_direction:
        case "top":
            average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
                                                                                                            brightness_error, scintillator_edges, 270)
        case "right":
            average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
                                                                                                            brightness_error, scintillator_edges, 180)
        case "bottom": 
            average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
                                                                                                            brightness_error, scintillator_edges, 90)
        case "left":
            pass
        case _:
            raise Exception("Invalid image beam direction specified in the database.")
    return average_image, average_rounded_image, brightness_error, scintillator_edges

def return_to_original_beam_direction(original_image_beam_direction, average_image, average_rounded_image, brightness_error, scintillator_edges):
    match original_image_beam_direction:
        case "top":
            average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
                                                                                                            brightness_error, scintillator_edges, 90)
        case "right":
            average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
                                                                                                            brightness_error, scintillator_edges, 180)
        case "bottom": 
            average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
                                                                                                            brightness_error, scintillator_edges, 270)
        case "left":
            pass
        case _:
            raise Exception("Invalid image beam direction specified in the database.")
    return average_image, average_rounded_image, brightness_error, scintillator_edges

def rotate_pixel_back_to_original_beam_direction(original_image_beam_direction, pixel_coord, unc_pixel_coord, image):
    """
    Image passed should be the image with the beam entering from the left!!!
    """
    height, width = image.shape[:2]
    x, y = pixel_coord
    match original_image_beam_direction:
        case "top":
        # 90 degree clockwise rotation
            x_new = height - 1 - y
            y_new = x
            unc_pixel_coord = unc_pixel_coord[::-1] # transpose error bars
        case "right":
        # 180 degree rotation
            x_new = width - 1 - x
            y_new = height - 1 - y
        case "bottom":
        # 270 degree clockwise rotation
            x_new = y
            y_new = width - 1 - x
            unc_pixel_coord = unc_pixel_coord[::-1]  # transpose error bars
        case "left":
            return pixel_coord, unc_pixel_coord
            
    return np.array([x_new, y_new]), unc_pixel_coord


def source_params_from_database(camera_analysis_id: int):
    
    camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(camera_analysis_id)
    beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id)
    camera_id = cdi.get_camera_and_settings_ids(camera_settings_link_id)["camera_id"]
    experiment_id = cdi.get_experiment_id_from_beam_run_id(beam_run_id)
    setup_id = cdi.get_setup_id_from_experiment_id(experiment_id)
    
    print("Camera settings link ID: ", camera_settings_link_id)
    print("Beam run ID: ", beam_run_id)
    print("Camera ID: ", camera_id)
    print("Setup ID: ", setup_id)
    print("Experiment ID: ", experiment_id)
    
    beam_energy = cdi.get_beam_run_ESS_beam_energy(beam_run_id)
    average_image = cdi.get_average_image(camera_analysis_id)
    
    num_of_images_used_in_average = cdi.get_num_of_successfully_captured_images_by_camera_settings_link_id(camera_settings_link_id) # validate against zero images
    unc_average_image = np.sqrt(average_image / num_of_images_used_in_average) # Poissonian error on mean used here
    
    average_image, unc_average_image = average_image.astype(np.float64), unc_average_image.astype(np.float64) # TODO - fix because cv2 does not support float16
    
    image_beam_direction = cdi.get_image_beam_direction(camera_id, setup_id)
    colour_channel = cdi.get_colour_channel(camera_analysis_id)
    scintillator_edges = np.array([cdi.get_horizontal_scintillator_limits(camera_id, setup_id),
                          cdi.get_vertical_scintillator_limits(camera_id, setup_id)]) # [horizontal_roi_dimensions, vertical_roi_dimensions]
    return beam_energy, image_beam_direction, colour_channel, average_image, unc_average_image, scintillator_edges


def get_beam_angle_and_bragg_peak_pixel(camera_analysis_id: int):
    """
    At this point, assume camera objects have already been built and stored in system database.
    So, this contains the user-defined scintillator edges, the homography matrix, distortion correction
    camera matrices, etc.
    """
    try:
        # Reset database plots associated with this analysis
        cdi.delete_all_plots_by_camera_analysis_id(camera_analysis_id)
        
        beam_energy, image_beam_direction, colour_channel, average_image, brightness_error, scintillator_edges = source_params_from_database(camera_analysis_id)
        average_rounded_image = average_image.astype(np.uint8)  # could be moved inside automated roi function
        
        # ###### MOCK ROTATION #################
        # mock_rotation = 270
        # image_beam_direction = "bottom"
        # average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
        #                                                                                                   brightness_error, scintillator_edges, mock_rotation)
        # ######################################
        
        average_image, average_rounded_image, brightness_error, \
        scintillator_edges =  get_beam_direction_from_the_left(image_beam_direction, average_image, average_rounded_image, brightness_error, scintillator_edges)
        
        (h_bounds, v_bounds), roi_image_bytes = get_automated_roi(camera_analysis_id, average_rounded_image, scintillator_edges[0], scintillator_edges[1], 
                                                                   show_images=False, fraction=0.2, save_to_database=True)
        
        cdi.add_camera_analysis_plot(camera_analysis_id, "automated_roi", roi_image_bytes, "svg")
        
        # Fit initial beam profile
        (horizontal_coords, fit_parameters_array, beam_center_errors, _, 
         _, _) = fit_beam_profile_along_full_roi(camera_analysis_id, "round_1", average_image, brightness_error,
                                                                    h_bounds, v_bounds, scintillator_edges, show_fit_qualities=False, save_plots_to_database=True)
        beam_center_vertical_coords = fit_parameters_array[:, 0]
        
        # Calculate incident beam angle
        incident_beam_angle, beam_angle_error = extract_incident_beam_angle(camera_analysis_id, horizontal_coords, beam_center_vertical_coords,
                                                                                                    beam_center_errors, show_angle_plot=False)
        cdi.update_beam_angle(camera_analysis_id, float(incident_beam_angle))
        cdi.update_unc_beam_angle(camera_analysis_id, float(beam_angle_error))
        
        # Rotate image for analysis
        rotated_image, _, inverse_rotation_matrix, rotation_brightness_error = image_processing.rotate_input_image(average_image, incident_beam_angle,
                                                                                                                    h_bounds, v_bounds, show_residuals=False)
        # brightness_error = np.sqrt(rotation_brightness_error**2 + brightness_error**2) # TODO - NOT WORKING ATM
        rotated_image = rotated_image.astype(np.float64) # TODO - temp fix - would need addressing in rotate function
        
        rotated_rounded_image = rotated_image.astype(np.uint8)
        (h_bounds, v_bounds), _ = get_automated_roi(camera_analysis_id, rotated_rounded_image, scintillator_edges[0], scintillator_edges[1], 
                                                    show_images=False, fraction=0.2)

        # Fit beam profile on rotated image
        (horizontal_coords, fit_parameters_array, beam_center_errors, _,  total_brightness_along_vertical_roi,
         unc_total_brightness_along_vertical_roi) = fit_beam_profile_along_full_roi(camera_analysis_id, "round_2", rotated_image, brightness_error,
                                                                                    h_bounds, v_bounds, scintillator_edges, show_fit_qualities=False, save_plots_to_database=True)
        
        beam_center_vertical_coords, *fit_params = fit_parameters_array[:, :5].T

        # Locate Bragg peak - NOTE: performed on rotated data before "unrotated" to original coords for pinpointing
        rotated_bragg_peak_coord, error_on_fitted_bragg_peak = locate_bragg_peak_in_image(camera_analysis_id, horizontal_coords, beam_center_vertical_coords, beam_center_errors,
                                                                                                                fit_params, total_brightness_along_vertical_roi, 
                                                                                                                unc_total_brightness_along_vertical_roi)
        
        # Rotate Bragg peak back to "beam on left coords"
        bragg_peak_coord, error_on_bragg_peak_coord = round_bragg_peak_coord(*rotate_bragg_peak_into_original_coords(rotated_bragg_peak_coord, error_on_fitted_bragg_peak, inverse_rotation_matrix))
        # Rotate Bragg peak back to original beam direction
        bragg_peak_coord, error_on_bragg_peak_coord = rotate_pixel_back_to_original_beam_direction(image_beam_direction, bragg_peak_coord, error_on_bragg_peak_coord, average_rounded_image)
        
        print("Bragg peak via Gaussian/Bortfeld fitting is at the pixel: {0} +/- {1}".format(bragg_peak_coord, error_on_bragg_peak_coord))
        cdi.update_bragg_peak_pixel(camera_analysis_id, [float(x) for x in bragg_peak_coord.flatten()])
        cdi.update_unc_bragg_peak_pixel(camera_analysis_id, [float(x) for x in error_on_bragg_peak_coord.flatten()])
        
        average_image, average_rounded_image, brightness_error, \
        scintillator_edges =  return_to_original_beam_direction(image_beam_direction, average_image, average_rounded_image, brightness_error, scintillator_edges)
        overlay_bragg_peak_coord(camera_analysis_id, average_rounded_image, bragg_peak_coord)
        return {"message": "successful single camera analysis"}
    
    except Exception as e:
        print("\n\nError when getting beam angle and bragg peak pixel: ", e)
        raise
    

def get_beam_center_coords(beam_run_id: int, camera_analysis_id: int):
    """
    At this point, assume camera objects have already been built and stored in system database.s
    So, this contains the user-defined scintillator edges, the homography matrix, distortion correction
    camera matrices, etc.
    """
    try:
        cdi.delete_overlayed_beam_centers_image_by_camera_analysis_id(camera_analysis_id)
        #### DB Reading #####
        beam_energy, image_beam_direction, colour_channel, average_image, brightness_error, scintillator_edges = source_params_from_database(camera_analysis_id)
        beam_angle = cdi.get_beam_angle(camera_analysis_id)
        ######################
        
        # ###### MOCK ROTATION #################
        # average_rounded_image = average_image.astype(np.uint8)
        # mock_rotation = 270
        # image_beam_direction = "bottom"
        # average_image, average_rounded_image, brightness_error, scintillator_edges = apply_rotations_for_analysis(average_image, average_rounded_image, 
        #                                                                                                           brightness_error, scintillator_edges,
        #                                                                                                           mock_rotation)
        # ######################################
        
        average_rounded_image = average_image.astype(np.uint8) # could be moved inside automated roi function
        
        average_image, average_rounded_image, brightness_error, \
        scintillator_edges =  get_beam_direction_from_the_left(image_beam_direction, average_image, average_rounded_image, brightness_error, scintillator_edges)
        
        (h_bounds, v_bounds), _ = get_automated_roi(camera_analysis_id, average_rounded_image, scintillator_edges[0], scintillator_edges[1], show_images=False, fraction=0.2)
        
        rotated_image, _, inverse_rotation_matrix, rotation_brightness_error = image_processing.rotate_input_image(average_image, beam_angle,
                                                                                                                   h_bounds, v_bounds, show_residuals=False)
        
        rotated_rounded_image = rotated_image.astype(np.uint8)
        (h_bounds, v_bounds), _ = get_automated_roi(camera_analysis_id, rotated_rounded_image, scintillator_edges[0], scintillator_edges[1], 
                                                    show_images=False, fraction=0.2)
        
        rotated_image = rotated_image.astype(np.float64)
        
        # Fit beam profile on rotated image
        (horizontal_coords, fit_parameters_array, beam_center_errors, _,
         total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi) = fit_beam_profile_along_full_roi(camera_analysis_id, "beam_reconstruction", rotated_image, brightness_error,
                                                                                                                         h_bounds, v_bounds, scintillator_edges)
        beam_center_vertical_coords, *fit_params = fit_parameters_array[:, :5].T
        # beam_scale_values, beam_sigma_values, sub_gauss_exponent_values, background_noise_values = fit_params
        
        beam_center_coords = np.vstack((horizontal_coords, beam_center_vertical_coords)).T
        unrotated_beam_center_coords = image_processing.inverse_rotation_of_coords(beam_center_coords, inverse_rotation_matrix)
        beam_center_error_vectors = np.vstack((np.full(len(beam_center_errors), 0), beam_center_errors)).T # vertical error in angle-corrected image
        unrotated_beam_center_error_vectors = image_processing.inverse_rotation_of_error_bars(beam_center_error_vectors, inverse_rotation_matrix) # now horizontal component to error vector also
        
        print("\n\n\n")
        print(unrotated_beam_center_coords, unrotated_beam_center_coords.shape)
        print("\n\n\n")
        print(unrotated_beam_center_error_vectors, unrotated_beam_center_error_vectors.shape)
        print("\n\n\n")
        
        result = np.array([rotate_pixel_back_to_original_beam_direction(image_beam_direction, pixel_coord, unc_pixel_coord, average_rounded_image) for pixel_coord, unc_pixel_coord in zip(unrotated_beam_center_coords, unrotated_beam_center_error_vectors)])
        original_beam_direction_beam_center_coords = result[:, 0]
        original_beam_direction_beam_center_coords_unc = result[:, 1]
        
        _, average_rounded_image, *_ =  return_to_original_beam_direction(image_beam_direction, average_image, average_rounded_image, brightness_error, scintillator_edges)
        overlay_beam_center_coords(camera_analysis_id, average_rounded_image, original_beam_direction_beam_center_coords)
        
        return original_beam_direction_beam_center_coords, original_beam_direction_beam_center_coords_unc, total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi
    
    except Exception as e:
        print("\n\nError when getting beam center coords: ", e)
        raise
