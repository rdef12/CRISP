# -*- coding: utf-8 -*-
"""
calibrateCamera documentation:
https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga687a1ab946686f0d85ae0363b5af1d7b

NOTE: DISTORTION CORRECTION DEPENDS ON FOCUS - THIS SHOULD MATCH THE FOCUS USED IN
CALIBRATION IMAGES FOR HOMOGRAPHY!
"""
import numpy as np
import cv2 as cv
import pickle
import matplotlib.pyplot as plt
from src.calibration_functions import *
from src.camera_functions import load_image_byte_string_to_opencv
from src.viewing_functions import show_image_in_window
from src.database.CRUD import CRISP_database_interaction as cdi

# CHESSBOARD_GRID_SIZE = (15, 11)
# CHESSBOARD_TILE_SPACING = 10 # In millimetres

CRITERIA = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

def plot_chessboard_corners(obj_points):
    
    plt.scatter(obj_points[:, 0], obj_points[:, 1])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show(block=False)


def get_feature_points_from_image(obj_points, image, chessboard_grid_size, image_count=None, 
                                  criteria=CRITERIA):
        
        # Find the chess board corners
        grey_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCornersSB(grey_image, chessboard_grid_size, flags=cv2.CALIB_CB_EXHAUSTIVE)

        # If corners found, add object points, image points (after refining them)
        if ret:
            optimised_corners = cv.cornerSubPix(grey_image, corners, (11,11), (-1,-1), criteria)
            return optimised_corners
        else:
            print(f"Image could not have its feature points identified...")
            return False


def extract_corners_from_distorted_images(obj_points, photo_id_array,
                                          chessboard_grid_size):
    """
    Should test if adaptive thresholding the images removes the light reflections,
    and thus increases the amount of usable images.
    """
    # Two sets of points for all usable images
    obj_points_array = [] # 2d point on calibration plane
    img_points_array = [] # 2d points in image plane

    for count, photo_id in enumerate(photo_id_array):
        image_byte_string = cdi.get_photo_from_id(photo_id)
        image = load_image_byte_string_to_opencv(image_byte_string)
        
        results = get_feature_points_from_image(obj_points, image, chessboard_grid_size)
        if results:
            img_points_array.append(results.optimised_corners)
            obj_points_array.append(obj_points)

    frame_size = determine_frame_size(image=image) # acts on last image
    return obj_points_array, img_points_array, frame_size

############## UNDISTORTION #####################################################

def undistort_image(camera_matrix, dist, frame_size, photo_id: int|None=None, image:np.ndarray|None=None):
    """
    roi: rectangle specifying area of undistorted image with valid image data
    dist: distortion coefficients
    alpha: set to 1 in cv.undistort (sets scale of new camera matrix)
    """
    
    if bool(image) == bool(photo_id): # XNOR
        raise Exception("Only Image or Photo ID must be entered")
    if photo_id:
        image_byte_string = cdi.get_photo_from_id(photo_id)
        image = load_image_byte_string_to_opencv(image_byte_string)
        
    h, w = frame_size
    newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist, (w,h), 1, (w,h))
    undistorted_image = cv.undistort(image, camera_matrix, dist, None, newCameraMatrix)
    
    # crop the image
    x, y, w, h = roi
    cropped_undistorted_image = undistorted_image[y:y+h, x:x+w]
    return cropped_undistorted_image # First method being returned


def calculate_reprojection_error(obj_points_array, img_points_array,
                                 camera_matrix, dist, rvecs, tvecs):
    mean_error = 0
    for i in range(len(obj_points_array)):
        imgpoints_2, _ = cv.projectPoints(obj_points_array[i], rvecs[i], tvecs[i], camera_matrix, dist)
        error = cv.norm(img_points_array[i], imgpoints_2, cv.NORM_L2)/len(imgpoints_2)
        mean_error += error
    
    total_error = mean_error/len(obj_points_array)
    return total_error


def distortion_calibration_test_for_gui(image, chessboard_grid_size, chessboard_tile_spacing, image_count=None,
                                        criteria=CRITERIA):
        
        grey_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCornersSB(grey_image, chessboard_grid_size, flags=cv2.CALIB_CB_EXHAUSTIVE)
        
        if ret:
            optimised_corners = cv.cornerSubPix(grey_image, corners, (11,11), (-1,-1), criteria)
            
            return {
            "status": True,
            "message": "Features points successfully identified in image {}.".format(image_count if image_count else ""),
        }
        else:
            print(f"Image could not have its feature points identified...")
            return {
                "status": False,
                "message": "Feature points not identifiable in image {}.".format(image_count if image_count else "")
            }

############## CALIBRATION #######################################################

def perform_distortion_calibration_from_database(setup_id, camera):
    
    camera_id = cdi.get_camera_id_from_username(username)
    pattern_size = cdi.get_distortion_calibration_pattern_size(camera_id, setup_id)
    pattern_type = cdi.get_distortion_calibration_pattern_type(camera_id, setup_id) # NOT USED YET
    pattern_spacing = cdi.get_distortion_calibration_pattern_spacing(camera_id, setup_id)
    # Use CRUD to get an array of photo IDs
    
    obj_points = generate_real_grid_positions(chessboard_grid_size, chessboard_tile_spacing)
    obj_points_array, img_points_array, frame_size = extract_corners_from_distorted_images(obj_points, photo_id_array, chessboard_grid_size)

    ret, camera_matrix, dist, rvecs, tvecs = cv.calibrateCamera(obj_points_array, img_points_array, frame_size,
                                                                None, None)
    
    # SAVE TO DATABASE AS PICKLETYPE
    cdi.update_camera_matrix(camera_id, setup_id, camera_matrix)
    cdi.update_distortion_coefficients(camera_id, setup_id, distortion_coefficients)