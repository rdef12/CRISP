import cv2
import numpy as np
from src.calibration_functions import *
from src.distortion_correction import *
from src.viewing_functions import *
from src.homography_errors import generate_homography_covariance_matrix
from typing import Literal
import base64

def save_homography_data(data_file_path: str, homography_matrix: np.ndarray[float, float],
                         homography_covariance: np.ndarray[float, float]):
    
        with open(data_file_path, "w") as f:
            np.savetxt(f, homography_matrix, delimiter=",", header="Homography Matrix")
            f.write("\n")
            np.savetxt(f, homography_covariance, delimiter=",", header="Homography Covariance")
            return None
        
def load_homography_data(data_file_path: str):
    
    with open(data_file_path, "r") as f:
        lines = f.readlines()
    split_indices = [i for i, line in enumerate(lines) if line.strip() == ""] # Find empty line

    homography_matrix = np.loadtxt(lines[1:split_indices[0]], delimiter=",")
    homography_position_covariance = np.loadtxt(lines[split_indices[0] + 2:], delimiter=",")

    return homography_matrix, homography_position_covariance


# For output to the GUI
def test_homography_grid_identified(image: np.ndarray, calibration_pattern: str, 
                                    calibration_grid_size: tuple[int, int], 
                                    pattern_spacing: list[float, float], 
                                    grid_uncertainties: tuple[float, float], 
                                    correct_for_distortion: bool=False):
    """
    Return the image bytestring and status of test
    """
    if correct_for_distortion:
        # NEW LOGIC FOR CORRECT FOR DISTORTION from database
        camera_matrix, dist = load_camera_calibration(distortion_calibration_path)
        frame_size = determine_frame_size(image_path=image_path)
        image = undistort_image(camera_matrix, dist, frame_size, image_path=image_path)
        
    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    real_grid_positions = generate_real_grid_positions(calibration_grid_size, pattern_spacing)
    match calibration_pattern:
        case "chessboard":
            image_grid_positions, ret = find_image_grid_positions_chessboard(grey_image, calibration_grid_size)
        case "symmetric_circles":
            image_grid_positions, ret = find_image_grid_positions_circles(grey_image, calibration_grid_size)
        case _:
            raise Exception("No calibration pattern called {} defined".format(calibration_pattern))
        
    if ret:
        cv2.drawChessboardCorners(image, grid_size, image_grid_positions, ret)
        first_point = tuple(map(int, image_grid_positions[0].ravel()))  # Convert to tuple (x, y)
        cv2.circle(image, first_point, radius=10, color=(0, 0, 255), thickness=-1)  # Red dot
        
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = base64.b64encode(buffer).decode("utf-8")
        return {
            "image_bytes": image_bytes
        }
        
    return {
        "image_bytes": None
    }


def build_calibration_plane_homography(image: np.ndarray, calibration_pattern: str, 
                                        calibration_grid_size: tuple[int, int], 
                                        pattern_spacing: list[float, float], 
                                        grid_uncertainties: tuple[float, float], 
                                        correct_for_distortion: bool=False,
                                        show_recognised_chessboard: bool=False,
                                        save_file_path: str|None=None,
                                        save_to_database: bool=False):

        if correct_for_distortion:
            # NEW LOGIC NEEDED TO LOAD IN DISTORTION DATA FROM DATABASE
            camera_matrix, dist = load_camera_calibration(distortion_calibration_path)
            frame_size = determine_frame_size(image_path=image_path)
            image = undistort_image(camera_matrix, dist, frame_size, image_path=image_path)
            
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        real_grid_positions = generate_real_grid_positions(calibration_grid_size, pattern_spacing)
        match calibration_pattern:
            case "chessboard":
                image_grid_positions, ret = find_image_grid_positions_chessboard(grey_image, calibration_grid_size)
            case "symmetric_circles":
                image_grid_positions, ret = find_image_grid_positions_circles(grey_image, calibration_grid_size)
            case _:
                raise Exception("No calibration pattern called {} defined".format(calibration_pattern))

        # RUDIMENTARY reverse of real grid points based on where first image point is.
        # Reverses image grid positions array if first x coord bigger than last x coord
        if image_grid_positions[0, 0, 0] > image_grid_positions[-1, 0, 0]:
            image_grid_positions = image_grid_positions[::-1]
            
        if show_recognised_chessboard:
            first_position = tuple(image_grid_positions[0].ravel().astype(int))
            cv2.circle(image, first_position, radius=40, color=(0, 255, 0), thickness=-1)
            print("{0} origin is at the pixel {1} (marked with a green circle)".format(real_grid_positions[0], first_position))
            overlay_identified_grid("Overlayed grid", image, image_grid_positions, calibration_grid_size, ret)

        homography_matrix, _ = cv2.findHomography(image_grid_positions, real_grid_positions)
        grid_uncertainties_array = np.full((len(image_grid_positions), 2), grid_uncertainties)
        homography_covariance = generate_homography_covariance_matrix(image_grid_positions, homography_matrix, grid_uncertainties_array)
        
        if save_to_database:
            # TODO - LOGIC
            pass
        
        if save_file_path is not None:
            save_homography_data(save_file_path, homography_matrix, homography_covariance)
            
        return homography_matrix, homography_covariance, image_grid_positions
    

def test_grid_recognition_for_gui(username: str, setup_id: int, 
                                   calibration_plane_type: Literal["far", "near"],
                                   photo_id: int|None=None, photo_bytes:str|None=None):

    camera_id = cdi.get_camera_id_from_username(username)
    match calibration_plane_type:
        case "far":
            pattern_size = cdi.get_far_face_calibration_pattern_size(camera_id, setup_id)
            pattern_type = cdi.get_far_face_calibration_pattern_type(camera_id, setup_id)
            pattern_spacing = cdi.get_far_face_calibration_spacing(camera_id, setup_id)
            unc_spacing = cdi.get_far_face_calibration_pattern_spacing_unc(camera_id, setup_id)
        case "near":
            pattern_size = cdi.get_near_face_calibration_pattern_size(camera_id, setup_id)
            pattern_type = cdi.get_near_face_calibration_pattern_type(camera_id, setup_id)
            pattern_spacing = cdi.get_near_face_calibration_spacing(camera_id, setup_id)
            unc_spacing = cdi.get_near_face_calibration_pattern_spacing_unc(camera_id, setup_id)
            
    if any(x is None for x in (pattern_size, pattern_type, pattern_spacing, unc_spacing)):
        correct_for_distortion = False
    else:
        correct_for_distortion = True

    if bool(photo_bytes) == bool(photo_id):  # XNOR
        raise Exception("Only Image bytes or Photo ID must be entered")
    if photo_id:
        photo_bytes = cdi.get_photo_from_id(photo_id)
    image = load_image_byte_string_to_opencv(photo_bytes)
    
    test_homography_grid_identified(image, pattern_type, pattern_size, 
                                    pattern_spacing, unc_spacing, 
                                    correct_for_distortion=correct_for_distortion)
    

def perform_homography_calibration(username: str, setup_id: int, 
                                   calibration_plane_type: Literal["far", "near"],
                                   photo_id: int|None=None, photo_bytes:str|None=None):
    """
    Applied to single plane - so ran twice for a given camera (from two different GUI pages)
    """
    camera_id = cdi.get_camera_id_from_username(username)
    match calibration_plane_type:
        case "far":
            pattern_size = cdi.get_far_face_calibration_pattern_size(camera_id, setup_id)
            pattern_type = cdi.get_far_face_calibration_pattern_type(camera_id, setup_id)
            pattern_spacing = cdi.get_far_face_calibration_spacing(camera_id, setup_id)
            unc_spacing = cdi.get_far_face_calibration_pattern_spacing_unc(camera_id, setup_id)
        case "near":
            pattern_size = cdi.get_near_face_calibration_pattern_size(camera_id, setup_id)
            pattern_type = cdi.get_near_face_calibration_pattern_type(camera_id, setup_id)
            pattern_spacing = cdi.get_near_face_calibration_spacing(camera_id, setup_id)
            unc_spacing = cdi.get_near_face_calibration_pattern_spacing_unc(camera_id, setup_id)
    
    
    if any(x is None for x in (pattern_size, pattern_type, pattern_spacing, unc_spacing)):
        correct_for_distortion = False
    else:
        correct_for_distortion = True

    if bool(photo_bytes) == bool(photo_id):  # XNOR
        raise Exception("Only Image bytes or Photo ID must be entered")
    if photo_id:
        photo_bytes = cdi.get_photo_from_id(photo_id)
    image = load_image_byte_string_to_opencv(photo_bytes)
    
    build_calibration_plane_homography(image, pattern_type, pattern_size, pattern_spacing, 
                                       unc_spacing, correct_for_distortion= correct_for_distortion,
                                       show_recognised_chessboard=False, save_to_database=True)
    return None