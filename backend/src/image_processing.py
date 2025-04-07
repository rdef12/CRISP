import cv2 as cv
import numpy as np
import pickle

from src.distortion_correction import undistort_image
from src.calibration_functions import determine_frame_size
from src.camera_functions import load_image_byte_string_to_opencv
import matplotlib.pyplot as plt
from src.database.CRUD import CRISP_database_interaction as cdi
# from fft_script import apply_fft_filtering


def select_image_colour_channel(image, input_colour: str):
    """
    valid_colours = ["red", "green", "blue", "grey", "gray"]
    """
    match input_colour:
        case "red":
            channel = image[:, :, 2]
        case "green":
            channel = image[:, :, 1]
        case "blue":
            channel = image[:, :, 0]
        case "grey" | "gray":
            # channel = cv.cvtColor(image, cv.COLOR_BGR2GRAY) # weighted based on human eye perception
            channel = np.mean(image, axis=2).astype(np.uint8) # Absolute greyscale
        case _:
            raise Exception('{} is not a valid colour channel. The options are ["red", "green", "blue", "grey", "gray"]'.format(input_colour))
    return channel

def average_pixel_over_multiple_images(camera_analysis_id: int):
    """
    In the semester one script (image_analysis_v3), there is functionality for plotting
    histograms of a given pixel's value for the three different colour channels. That code can
    be added here later if need be.
    """
    camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(camera_analysis_id)
    photo_id_array = cdi.get_successfully_captured_photo_ids_by_camera_settings_link_id(camera_settings_link_id)
    colour_channel = cdi.get_colour_channel(camera_analysis_id)
    
    num_of_images_used = len(photo_id_array)
    test_photo_bytes = cdi.get_photo_from_id(photo_id_array[0])
    test_image = load_image_byte_string_to_opencv(test_photo_bytes)
    
    if correct_for_distortion := cdi.check_for_distortion_correction_condition(camera_id, setup_id):
        camera_id = (cdi.get_camera_and_settings_ids(camera_settings_link_id)["camera_id"])
        beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id)
        experiment_id = cdi.get_experiment_id_from_beam_run_id(beam_run_id)
        setup_id = cdi.get_setup_id_from_experiment_id(experiment_id)
        
        camera_matrix = cdi.get_camera_matrix(camera_id, setup_id)
        distortion_coefficients = cdi.get_distortion_coefficients(camera_id, setup_id)
        original_frame_size = determine_frame_size(image=image)
        corrected_test_image = undistort_image(camera_matrix, distortion_coefficients, frame_size, image=image)
        frame_size = determine_frame_size(image=corrected_test_image)
    else:
        frame_size = determine_frame_size(image=test_image)
    
    shape = (frame_size[0], frame_size[1])
    cumulative_pixel_val_sum = np.zeros(shape, dtype=np.float64)
    
    for photo_id in photo_id_array:
        photo_bytes = cdi.get_photo_from_id(photo_id)
        image = load_image_byte_string_to_opencv(photo_bytes)
        if correct_for_distortion:
            image = undistort_image(camera_matrix, distortion_coefficients, original_frame_size, image=image)
        
        image_channel = select_image_colour_channel(image, colour_channel)
        cumulative_pixel_val_sum += image_channel
    
    average_image = (cumulative_pixel_val_sum / num_of_images_used)
    # poisson_standard_error_on_mean = np.sqrt(average_image / num_of_images_used)
    
    float_16_image = average_image.astype(np.float16)
    serialized_float_16_image = pickle.dumps(float_16_image, protocol=pickle.HIGHEST_PROTOCOL)
    image_memory_size = len(serialized_float_16_image)
    print(f"Memory size of the rounded serialized average image: {image_memory_size/10**6} MB")
    cdi.update_average_image(camera_analysis_id, serialized_float_16_image)
    return average_image


def rotate_input_image(image: np.ndarray[np.uint8], incident_beam_angle: float, h_bounds, v_bounds,
                       show_residuals: bool=False):
    """
    Rotation matrix is 3x2, encoding information about the rotation, as well as the translation
    needed due to the point in which we are rotating about. The first 2 columns constitute the
    traditional 2x2 rotation matrix by angle theta, and the last column [t_x, t_y] corresponds to
    a translation such that the rotation is performed about the center of the image.
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    # Compute the rotation matrix for an anticlockwise rotation
    # If pixel height of beam center increases along scintillator length, beam angled down so anticlockwise correction needed
    rotation_matrix = cv.getRotationMatrix2D(center, incident_beam_angle, 1) # final arg is the scale, and the angle is in degrees.
    inverse_rotation_matrix = cv.getRotationMatrix2D(center, -1 * incident_beam_angle, 1)
    rotated_image = cv.warpAffine(image, rotation_matrix, (w, h), flags=cv.INTER_LANCZOS4)
    
    unrotated_image = cv.warpAffine(rotated_image, inverse_rotation_matrix, (w, h), flags=cv.INTER_LANCZOS4)
    residuals = rotated_image - unrotated_image
    cropped_residuals = residuals[v_bounds[0]:v_bounds[-1], h_bounds[0]:h_bounds[-1]]
    flattened_cropped_residuals = cropped_residuals.flatten()
    
    resiudal_std = np.std(flattened_cropped_residuals)
    
    if show_residuals:
        plt.imshow(abs(cropped_residuals), cmap="grey")
        plt.colorbar(label="Residual Magnitude")
        plt.show()
        plt.close()
        
        plt.figure(figsize=(8, 5))
        bin_edges = np.linspace(-3*resiudal_std, 3*resiudal_std, 31) 
        plt.hist(flattened_cropped_residuals, bins=bin_edges, edgecolor='black', alpha=0.7)
        plt.xlabel("Residuals")
        plt.ylabel("Frequency")
        plt.title("Histogram of residuals after rotation + inverse rotation")
        plt.grid(True)
        plt.show()
        plt.close()
    
    rotation_brightness_error = resiudal_std / 2 # Not dividing by root(2) because each rotation's error not independent
    return rotated_image, rotation_matrix, inverse_rotation_matrix, rotation_brightness_error


def inverse_rotation_of_coords(array_of_coords, inverse_rotation_matrix):
    homogenous_column = np.ones((array_of_coords.shape[0], 1))
    homogenous_beam_center_coords = np.hstack((array_of_coords, homogenous_column))
    
    unrotated_coords = np.array([])
    for rotated_coordinate in homogenous_beam_center_coords:
        coordinate = (inverse_rotation_matrix @ rotated_coordinate.T).astype(int)
        unrotated_coords = np.append(unrotated_coords, coordinate)
    unrotated_coords = unrotated_coords.reshape(len(array_of_coords), 2)
    return unrotated_coords



