import os
import numpy as np
import cv2
import math
from src.viewing_functions import *
from pydantic import BaseModel

# Decided I can implement the rounding in the frontend!
class ROI(BaseModel):
    hStart: int
    hEnd: int
    vStart: int
    vEnd: int

def convert_iterable_to_opencv_format(iterable: tuple[float, float]):
    
    if len(iterable) != 2:
        raise Exception("Iterable must be of length 2.")
    opencv_format = np.array([[iterable[0], iterable[1]]], dtype="float32")
    opencv_format = np.expand_dims(opencv_format, axis=0)
    return opencv_format


def convert_opencv_format_to_tuple(opencv_format: np.ndarray[float, float]):
    return (opencv_format[0][0][0], opencv_format[0][0][1])
    
    
def find_image_grid_positions_circles(image: np.ndarray, grid_size: tuple[int, int]): # Currently for symmetric circles
    
    grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Also a CALIB_CB_ASYMMETRIC_GRID flag if using that pattern.
    ret, initial_grid_positions = cv2.findCirclesGrid(grey_image, grid_size, cv2.CALIB_CB_SYMMETRIC_GRID + cv2.CALIB_CB_CLUSTERING)
    
    if not ret:
        raise Exception("Grid points could not be identified")
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 1000, 0.0001) #TODO: Identify what this is and optimise
    image_grid_positions = cv2.cornerSubPix(grey_image, initial_grid_positions, (11,11), (-1,-1), criteria)
    return image_grid_positions, ret


def find_image_grid_positions_chessboard(grey_image: np.ndarray, grid_size: tuple[int, int]):
    
    ret, initial_grid_positions = cv2.findChessboardCornersSB(grey_image, grid_size, flags=cv2.CALIB_CB_EXHAUSTIVE)
    
    if not ret:
        raise Exception("Grid points could not be identified")
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001) #TODO: Identify what this is and optimise
    image_grid_positions = cv2.cornerSubPix(grey_image, initial_grid_positions, (11,11), (-1,-1), criteria)
    return image_grid_positions, ret


def determine_frame_size(image: np.ndarray=None, image_path: str=None):
    
    try:
        if image is None and image_path:
            image = cv2.imread(image_path)
        if image is not None:
            return (image.shape[0], image.shape[1])
        else:
            raise ValueError("Either image or image_path must be provided.")
    except Exception as e:
        print("Error: {}".format(e))


def generate_object_points(grid_size: tuple[int, int], spacing: float):
    # Prepare object points (real-world 3D points) like (0,0,0), (1,0,0), ..., (grid_size[0]-1, grid_size[1]-1,0)
    objp = np.zeros((grid_size[0] * grid_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)
    
    # Scale the object points based on the size of the chessboard squares in mm
    objp = objp * spacing
    return objp


####################################### DISTANCE CALIBRATIONS START ############################################

def generate_real_grid_positions(grid_size: tuple[int, int], spacing: float): # Applies to square grid
    
    real_grid_positions = np.empty(grid_size)
    x_length, y_length = grid_size
    x_coords, y_coords = np.meshgrid(np.arange(x_length) * spacing, np.arange(y_length) * spacing)
    real_grid_positions = np.dstack([x_coords, y_coords])
    real_grid_positions = real_grid_positions.reshape(-1, 1, 2) # Reshape to match OpenCV standard
    return real_grid_positions


def generate_independent_real_grid_positions(grid_size: tuple[int, int], x_spacing: float, y_spacing: float):
    independent_real_grid_positions = np.empty(grid_size)
    x_length, y_length = grid_size
    x_coords, y_coords = np.meshgrid(np.arange(x_length) * x_spacing, np.arange(y_length) * y_spacing)
    independent_real_grid_positions = np.dstack([x_coords, y_coords])
    independent_real_grid_positions = independent_real_grid_positions.reshape(-1, 1, 2)
    return independent_real_grid_positions


#TODO Add warning for pixels outside of the calibration grid
#TODO Undefined behaviour when second argument given but not with associated key word
def convert_image_position_to_real_position(pixel: np.ndarray[int, int], homography_matrix_input=None, homography_matrix_path=None):
    
    homography_matrix = np.zeros((3, 3))
    if homography_matrix_input is not None:
        if np.shape(homography_matrix_input) != (3, 3):
            raise Exception("Homography matrix must be 3x3")
        homography_matrix = homography_matrix_input
    elif homography_matrix_path is not None:
        try:
            homography_matrix_file = np.genfromtxt(homography_matrix_path)
            print("homography matrix file: {}".format(homography_matrix_file))
            if np.shape(homography_matrix_file) != (3, 3):
                raise Exception("Homography matrix must be 3x3")
            homography_matrix = homography_matrix_file
        except FileNotFoundError:
            raise Exception("File at '{}' could not be found.".format(homography_matrix_path))
    else:
        raise Exception("Must input either a homography matrix or the path to one")
    real_position = cv2.perspectiveTransform(pixel, homography_matrix)
    return real_position

####################################### DISTANCE CALIBRATIONS END ############################################



def generate_pixel_pairs(pixel_min: int, pixel_max: int):
    x = np.arange(pixel_min, pixel_max, 5)
    y = np.arange(pixel_min, pixel_max, 5)
    
    # Create a grid of all (x, y) coordinate pairs
    xx, yy = np.meshgrid(x, y)
    
    # Stack and reshape to get a list of pixel pairs
    pixel_pairs = np.stack([xx.ravel(), yy.ravel()], axis=-1)
    return [tuple(pair) for pair in pixel_pairs]


####################################################################################################################
