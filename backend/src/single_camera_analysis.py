"""
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
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ImageByteStrings:
    """
    NOTE - Images should be base64 encoded before storing
    """
    images: Dict[str, bytes] = field(default_factory=dict)

    def add_image(self, image_type: str, image_bytes: bytes):
        """Add an image byte string to the store."""
        self.images[image_type] = image_bytes

    def get_image(self, image_type: str) -> bytes:
        """Retrieve an image byte string by its type."""
        return self.images.get(image_type, None)

    def remove_image(self, image_type: str):
        """Remove an image from the store by its type."""
        if image_type in self.images:
            del self.images[image_type]


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
    
    colour_channel = cdi.get_colour_channel(camera_analysis_id)
    # [horizontal_roi_dimensions, vertical_roi_dimensions]
    scintillator_edges = [cdi.get_horizontal_scintillator_limits(camera_id, setup_id),
                          cdi.get_vertical_scintillator_limits(camera_id, setup_id)]
    return beam_energy, colour_channel, average_image, unc_average_image, scintillator_edges

def get_beam_angle_and_bragg_peak_pixel(camera_analysis_id: int):
    """
    At this point, assume camera objects have already been built and stored in system database.s
    So, this contains the user-defined scintillator edges, the homography matrix, distortion correction
    camera matrices, etc.
    """
    
    try:
        beam_energy, colour_channel, average_image, brightness_error, scintillator_edges = source_params_from_database(camera_analysis_id)
        average_rounded_image = average_image.astype(np.uint8) # could be moved inside automated roi function
        image_store = ImageByteStrings()
        
        (h_bounds, v_bounds), base64_roi_image = get_automated_roi(average_rounded_image, scintillator_edges[0], scintillator_edges[1], 
                                                                   show_images=False, fraction=0.16)
        image_store.add_image("roi_image", base64_roi_image)
        
        # Fit initial beam profile
        (horizontal_coords, fit_parameters_array, beam_center_errors, _, 
         total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi, 
         plot_byte_strings) = fit_beam_profile_along_full_roi(average_image, brightness_error,
                                                                                h_bounds, v_bounds, show_fit_qualities=False)
        image_store.add_image("original_chi_squared_values", plot_byte_strings[0])
        image_store.add_image("original_best_gaussian_fit", plot_byte_strings[1])
        image_store.add_image("original_worst_gaussian_fit", plot_byte_strings[2])
        image_store.add_image("original_overlayed_beam", plot_byte_strings[3])
        beam_center_vertical_coords = fit_parameters_array[:, 0]
        
        # Calculate incident beam angle
        incident_beam_angle, beam_angle_error, angle_plot_byte_string = extract_incident_beam_angle(horizontal_coords, beam_center_vertical_coords, beam_center_errors, show_angle_plot=False)
        image_store.add_image("incident_beam_angle", angle_plot_byte_string)

        # Rotate image for analysis
        rotated_image, _, inverse_rotation_matrix, rotation_brightness_error = image_processing.rotate_input_image(average_image, incident_beam_angle,
                                                                                                                    h_bounds, v_bounds, show_residuals=False)
        # brightness_error = np.sqrt(rotation_brightness_error**2 + brightness_error**2) # TODO - NOT WORKING ATM
        rotated_image = rotated_image.astype(np.float64) # TODO - temp fix - would need addressing in rotate function
        
        # Fit beam profile on rotated image
        (horizontal_coords, fit_parameters_array, beam_center_errors, _,  _, _,
         plot_byte_strings) = fit_beam_profile_along_full_roi(rotated_image, brightness_error,
                                                            h_bounds, v_bounds, show_fit_qualities=False)
        image_store.add_image("rotated_chi_squared_values", plot_byte_strings[0])
        image_store.add_image("rotated_best_gaussian_fit", plot_byte_strings[1])
        image_store.add_image("rotated_worst_gaussian_fit", plot_byte_strings[2])
        image_store.add_image("rotated_overlayed_beam", plot_byte_strings[3])
        
        beam_center_vertical_coords, *fit_params = fit_parameters_array[:, :4].T
        beam_scale_values, beam_sigma_values, background_noise_array = fit_params

        # Locate Bragg peak - NOTE: performed on rotated data before "unrotated" to original coords for pinpointing
        rotated_bragg_peak_coord, error_on_fitted_bragg_peak, bortfeld_byte_string = locate_bragg_peak_in_image(horizontal_coords, beam_center_vertical_coords, background_noise_array, beam_scale_values, beam_center_errors,
                                                                                        beam_sigma_values, total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi, save_data=True,
                                                                                        show_scintillation_plot=False)
        image_store.add_image("fitted_bortfeld", bortfeld_byte_string)
        
        # NOTE - uncertainties may now be too small such that pinpointing fails!
        bragg_peak_coord, error_on_bragg_peak_coord = round_bragg_peak_coord(*rotate_bragg_peak_into_original_coords(rotated_bragg_peak_coord, error_on_fitted_bragg_peak, inverse_rotation_matrix))
        print("Bragg peak via Gaussian/Bortfeld fitting is at the pixel: {0} +/- {1}".format(bragg_peak_coord, error_on_bragg_peak_coord))
        
        return {"beam_angle": incident_beam_angle, "beam_angle_error": beam_angle_error, "bragg_peak_pixel": bragg_peak_coord, "bragg_peak_pixel_error": error_on_bragg_peak_coord,
                "plot_byte_strings": image_store.images} # return results which will be written to database
    
    except Exception as e:
        print("\n\nError when getting beam angle and bragg peak pixel: ", e)
        raise
    

# TODO - decompose further so this is just a function for getting unrotated beam center coords and their errors
# def get_3d_beam_path(beam_run_id: int, first_camera_id: int, second_camera_id: int, setup_id: int):
#     """
#     At this point, assume camera objects have already been built and stored in system database.s
#     So, this contains the user-defined scintillator edges, the homography matrix, distortion correction
#     camera matrices, etc.
#     """
#     try:
#         ########## DATABASE SOURCED ##########
#         beam_energy = 150
#         scintillator_edges = CAMERA_SCINTILLATOR_EDGES.get("side_arducam") # [horizontal_roi_dimensions, vertical_roi_dimensions]
#         average_image, brightness_error = AVERAGED_IMAGE, AVERAGED_IMAGE_BRIGHTNESS_ERROR # float64 images being used here
#         average_image = average_image[:, :, 0] # Only the blue channel - TODO - fix in backend version
        
#         bragg_peak_position = (0, 0, 0) # pinpointing will have already been done
#         beam_angle_1 = None # first camera angle
#         beam_angle_2 = None # second camera angle
#         ######################################
        
#         average_rounded_image = average_image.astype(np.uint8) # could be moved inside automated roi function
        
#         h_bounds, v_bounds = get_automated_roi(average_rounded_image, scintillator_edges[0], scintillator_edges[1], show_images=False, fraction=0.16)
        
#         # Rotate image for analysis - NOTE: beam angle 1 assumed to be cam which the beam-axis distribution is being computed for
#         rotated_image, _, inverse_rotation_matrix, rotation_brightness_error = image_processing.rotate_input_image(average_image, beam_angle_1,
#                                                                                                                    h_bounds, v_bounds, show_residuals=False)
        
#         # brightness_error = np.sqrt(rotation_brightness_error**2 + brightness_error**2) # TODO - NOT WORKING ATM
#         rotated_image = rotated_image.astype(np.float64) # TODO - temp fix - would need addressing in rotate function
        
#         # Fit beam profile on rotated image
#         (horizontal_coords, fit_parameters_array, beam_center_errors, _,  _, _) = fit_beam_profile_along_full_roi(rotated_image, brightness_error,
#                                                                                                                   h_bounds, v_bounds, show_fit_qualities=True)
        
#         beam_center_vertical_coords, *fit_params = fit_parameters_array[:, :4].T
#         beam_scale_values, beam_sigma_values, background_noise_array = fit_params
        
#         beam_center_coords = np.vstack((horizontal_coords, beam_center_vertical_coords)).T
#         unrotated_beam_center_coords = image_processing.inverse_rotation_of_coords(beam_center_coords, inverse_rotation_matrix)
#         beam_center_error_vectors = np.vstack((np.full(len(beam_center_errors), 0), beam_center_errors)).T # vertical error in angle-corrected image
        
#         # TODO - update rotation of error vectors to that done to the bragg peak pixel error (only 2x2 rotation matrix needed)
#         unrotated_beam_center_error_vectors = image_processing.inverse_rotation_of_coords(beam_center_error_vectors, inverse_rotation_matrix) # rotated to original coords to introduce horizontal and vertical error

#         # Next I need to calculate the beam path in 3D space - allows pinpointing between these line and one camera view
#         return None
    
    except Exception as e:
        print("\n\nError when getting beam angle and bragg peak pixel: ", e)
        raise
