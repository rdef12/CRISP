import cv2
import numpy as np
from src.calibration_functions import *
from src.distortion_correction import *
from src.viewing_functions import *
from src.homography_errors import generate_homography_covariance_matrix
from typing import Literal
from src.database.CRUD import CRISP_database_interaction as cdi
import base64
from pydantic import BaseModel
import pickle

class ImagePointTransforms(BaseModel):
    horizontal_flip: bool
    vertical_flip: bool
    swap_axes: bool
    
def convert_array_to_opencv_form(array):
    return array.reshape(-1, 1, 2)

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


def save_homography_calibration_to_database(camera_id, setup_id, plane_type, homography_matrix, homography_covariance):
    
    homography_matrix = pickle.dumps(homography_matrix)
    homography_covariance = pickle.dumps(homography_covariance)
    match plane_type:
        case "far":
            cdi.update_far_face_homography_matrix(camera_id, setup_id, homography_matrix)
            cdi.update_far_face_homography_covariance_matrix(camera_id, setup_id, homography_covariance)
        case "near":
            cdi.update_near_face_homography_matrix(camera_id, setup_id,homography_matrix)
            cdi.update_near_face_homography_covariance_matrix(camera_id, setup_id, homography_covariance)
        case _:
            raise Exception(f"Plane type must be near or far, not {plane_type}")
    return None


def add_origin_to_image(image, image_grid_positions, calibration_grid_size):
    cv2.drawChessboardCorners(image, calibration_grid_size, image_grid_positions, True)
    for img_point in image_grid_positions:
        point_tuple = tuple(map(int, img_point.ravel()))  # Convert to tuple (x, y)
        cv2.circle(image, point_tuple, radius=20, color=(255, 0, 0), thickness=-1)  # Blue dots
        
    origin = tuple(map(int, image_grid_positions[0].ravel()))  # Convert to tuple (x, y)
    cv2.circle(image, origin, radius=50, color=(0, 0, 255), thickness=-1)  # Red dot
    
    # Calculate direction vector from first to second point
    direction_vector = image_grid_positions[1] - image_grid_positions[0]
    direction_vector = tuple(map(int, direction_vector.ravel()))  # Convert to tuple (x, y)
    arrow_end_point = (origin[0] + direction_vector[0], origin[1] + direction_vector[1])
    cv2.arrowedLine(image, origin, arrow_end_point, color=(0, 255, 255), thickness=20, tipLength=0.5)  # Yellow arrow

# For output to the GUI
def test_homography_grid_identified(image: np.ndarray, calibration_pattern: str, 
                                    calibration_grid_size: tuple[int, int], 
                                    image_point_transforms: ImagePointTransforms,
                                    camera_id: int, setup_id: int,
                                    correct_for_distortion: bool=False):
    """
    Return the image bytestring and status of test
    """
    if correct_for_distortion:
        camera_matrix = cdi.get_camera_matrix(camera_id, setup_id)
        distortion_coefficients = cdi.get_distortion_coefficients(camera_id, setup_id)
        frame_size = determine_frame_size(image=image)
        image = undistort_image(camera_matrix, distortion_coefficients, frame_size, image=image)
        
    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    match calibration_pattern:
        case "chessboard":
            image_grid_positions, ret = find_image_grid_positions_chessboard(grey_image, calibration_grid_size)
        case "symmetric_circles":
            image_grid_positions, ret = find_image_grid_positions_circles(grey_image, calibration_grid_size)
        case _:
            raise Exception("No calibration pattern called {} defined".format(calibration_pattern))
        
    if not ret:
        _, buffer = cv2.imencode('.jpg', image) # Circle should not be present if ret false
        return {
            "status": False,
            "message": "Calibration pattern could not be recognised in the image",
            "image_bytes": base64.b64encode(buffer).decode("utf-8")
    }
    
    if image_point_transforms.horizontal_flip:
            image_grid_positions_reshaped = image_grid_positions.reshape((calibration_grid_size[1], calibration_grid_size[0], 2))[:, ::-1] # Reverse the order of columns
            image_grid_positions = convert_array_to_opencv_form(image_grid_positions_reshaped)
    if image_point_transforms.vertical_flip:
        image_grid_positions_reshaped = image_grid_positions.reshape((calibration_grid_size[1], calibration_grid_size[0], 2))[::-1,:]  # Reverse the order of rows
        image_grid_positions = convert_array_to_opencv_form(image_grid_positions_reshaped)
    if image_point_transforms.swap_axes:
        image_grid_positions_reshaped = image_grid_positions.reshape((calibration_grid_size[1], calibration_grid_size[0], 2)).transpose(1, 0, 2)  # Transpose array
        image_grid_positions = convert_array_to_opencv_form(image_grid_positions_reshaped)
    
    add_origin_to_image(image, image_grid_positions, calibration_grid_size)
    
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = base64.b64encode(buffer).decode("utf-8")
    return {
        "status": True,
        "message": "Calibration pattern succesfully recognised. Origin of coordinate system overlayed as a red circle.",
        "image_bytes": image_bytes
    }


def build_calibration_plane_homography(image: np.ndarray, plane_type: str, calibration_pattern: str, 
                                        calibration_grid_size: tuple[int, int], 
                                        pattern_spacing: list[float, float], 
                                        grid_uncertainties: tuple[float, float], 
                                        image_point_transforms: ImagePointTransforms,
                                        camera_id: int, setup_id: int,
                                        correct_for_distortion: bool=False,
                                        save_file_path: str|None=None,
                                        save_to_database: bool=False,
                                        save_overlayed_grid: bool=False):

        if correct_for_distortion:
            print("\n\n\n\n DISTORTION CORRECTION APPLIED \n\n\n\n")
            camera_matrix = cdi.get_camera_matrix(camera_id, setup_id)
            distortion_coefficients = cdi.get_distortion_coefficients(camera_id, setup_id)
            frame_size = determine_frame_size(image=image)
            image = undistort_image(camera_matrix, distortion_coefficients, frame_size, image=image)
            
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        match calibration_pattern:
            case "chessboard":
                image_grid_positions, ret = find_image_grid_positions_chessboard(grey_image, calibration_grid_size)
            case "symmetric_circles":
                image_grid_positions, ret = find_image_grid_positions_circles(grey_image, calibration_grid_size)
            case _:
                raise Exception("No calibration pattern called {} defined".format(calibration_pattern))

        if image_point_transforms.horizontal_flip:
            image_grid_positions_reshaped = image_grid_positions.reshape((calibration_grid_size[1], calibration_grid_size[0], 2))[:, ::-1] # Reverse the order of columns
            image_grid_positions = convert_array_to_opencv_form(image_grid_positions_reshaped)
        if image_point_transforms.vertical_flip:
            image_grid_positions_reshaped = image_grid_positions.reshape((calibration_grid_size[1], calibration_grid_size[0], 2))[::-1,:]  # Reverse the order of rows
            image_grid_positions = convert_array_to_opencv_form(image_grid_positions_reshaped)
        if image_point_transforms.swap_axes:
            image_grid_positions_reshaped = image_grid_positions.reshape((calibration_grid_size[1], calibration_grid_size[0], 2)).transpose(1, 0, 2)  # Transpose array
            image_grid_positions = convert_array_to_opencv_form(image_grid_positions_reshaped)

        real_grid_positions = generate_real_grid_positions(calibration_grid_size, pattern_spacing, image_point_transforms.swap_axes)
        homography_matrix, _ = cv2.findHomography(image_grid_positions, real_grid_positions)
        grid_uncertainties_array = np.full((len(image_grid_positions), 2), grid_uncertainties)
        homography_covariance = generate_homography_covariance_matrix(image_grid_positions, homography_matrix, grid_uncertainties_array)
        
        if save_to_database:
            save_homography_calibration_to_database(camera_id, setup_id, plane_type, homography_matrix, 
                                                    homography_covariance)
        
        if save_overlayed_grid:
            add_origin_to_image(image, image_grid_positions, calibration_grid_size)
            filepath = f"/code/temp_images/camera_{camera_id}_homography_{plane_type}.jpeg"
            cv2.imwrite(filepath, image)
        
        if save_file_path is not None:
            save_homography_data(save_file_path, homography_matrix, homography_covariance)
            
        return homography_matrix, homography_covariance, image_grid_positions
    

def test_grid_recognition_for_gui(username: str, setup_id: int, 
                                   calibration_plane_type: Literal["far", "near"],
                                   image_point_transforms: ImagePointTransforms = ImagePointTransforms(
                                        horizontal_flip=False, vertical_flip=False, swap_axes=False
                                   ),
                                   photo_id: int|None=None, photo_bytes:str|None=None):

    camera_id = cdi.get_camera_id_from_username(username)
    match calibration_plane_type:
        case "far":
            pattern_size = cdi.get_far_face_calibration_pattern_size(camera_id, setup_id)
            pattern_type = cdi.get_far_face_calibration_pattern_type(camera_id, setup_id)
        case "near":
            pattern_size = cdi.get_near_face_calibration_pattern_size(camera_id, setup_id)
            pattern_type = cdi.get_near_face_calibration_pattern_type(camera_id, setup_id)
    
    # If distortion correction fields are not completely filled, set to False
    correct_for_distortion = cdi.check_for_distortion_correction_condition(camera_id, setup_id)

    if bool(photo_bytes) == bool(photo_id):  # XNOR
        raise Exception("Only Image bytes or Photo ID must be entered")
    if photo_id:
        photo_bytes = cdi.get_photo_from_id(photo_id)
    image = load_image_byte_string_to_opencv(photo_bytes)
    
    return test_homography_grid_identified(image, pattern_type, pattern_size, 
                                           image_point_transforms, camera_id, setup_id,
                                           correct_for_distortion=correct_for_distortion)
    

def perform_homography_calibration(username: str, setup_id: int,
                                   calibration_plane_type: Literal["far", "near"],
                                   image_point_transforms: ImagePointTransforms = ImagePointTransforms(
                                        horizontal_flip=False, vertical_flip=False, swap_axes=False
                                   ),
                                   photo_id: int|None=None, photo_bytes:str|None=None,
                                   save_overlayed_grid: bool=False):
    """
    Applied to single plane - so ran twice for a given camera (from two different GUI pages)
    """
    try:
        camera_id = cdi.get_camera_id_from_username(username)
        match calibration_plane_type:
            case "far":
                pattern_size = cdi.get_far_face_calibration_pattern_size(camera_id, setup_id)
                pattern_type = cdi.get_far_face_calibration_pattern_type(camera_id, setup_id)
                pattern_spacing = cdi.get_far_face_calibration_spacing(camera_id, setup_id)
                unc_spacing = cdi.get_far_face_calibration_spacing_unc(camera_id, setup_id)
            case "near":
                pattern_size = cdi.get_near_face_calibration_pattern_size(camera_id, setup_id)
                pattern_type = cdi.get_near_face_calibration_pattern_type(camera_id, setup_id)
                pattern_spacing = cdi.get_near_face_calibration_spacing(camera_id, setup_id)
                unc_spacing = cdi.get_near_face_calibration_spacing_unc(camera_id, setup_id)
        
        # If distortion correction fields are not completely filled, set to False
        correct_for_distortion = cdi.check_for_distortion_correction_condition(camera_id, setup_id)
        
        print("\n\n pattern_size: ", pattern_size)
        print("\n\n pattern_type: ", pattern_type)

        if bool(photo_bytes) == bool(photo_id):  # XNOR
            raise Exception("Only Image bytes or Photo ID must be entered")
        if photo_id:
            photo_bytes = cdi.get_photo_from_id(photo_id)
        image = load_image_byte_string_to_opencv(photo_bytes)
        
        build_calibration_plane_homography(image, calibration_plane_type, pattern_type, pattern_size, pattern_spacing, 
                                        unc_spacing, image_point_transforms, camera_id, setup_id, correct_for_distortion=correct_for_distortion,
                                        save_to_database=True, save_overlayed_grid=save_overlayed_grid)
        
        return True # If return True, frontend knows it was successful
    except Exception as e:
        raise