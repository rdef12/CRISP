# -*- coding: utf-8 -*-
"""
Test with my Ipad first of all. Must use a calibration image
as a test for undistortion efficacy because the images must
have the same focal plane.

Eventhough the chessboard can be a different size from that used for the two homography
calibration planes, the focus must me set the same. Therefore, need to think of a directory
hierarchy which makes it clear which distortion mapping is associated with a given image set.

--------------------------------------------------------------------------------------------

calibrateCamera documentation:
https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html#ga687a1ab946686f0d85ae0363b5af1d7b

NOTE: DISTORTION CORRECTION DEPENDS ON FOCUS - THIS DOES NOT MATCH THE FOCUS USED IN
CALIBRATION IMAGES FOR HOMOGRAPHY!
"""

import numpy as np
import cv2 as cv
import glob
import pickle

import matplotlib.pyplot as plt

from src.calibration_functions import *
from arc.viewing_functions import show_image_in_window

# Ipad Chessboard has its own spacing/grid size
CHESSBOARD_GRID_SIZE = (15, 11)
CHESSBOARD_TILE_SPACING = 10 # In millimetres

DISTORTED_IMAGE_DIRECTORY = r'final_distortion_images\side_HQ'
DISTORTED_IMAGE_PATHS = glob.glob(DISTORTED_IMAGE_DIRECTORY + r'\*.jpeg')
TEST_IMAGE = r'final_distortion_images\side_hq_control.jpeg'
UNDISTORTED_IMAGE_DIRECTORY =  r'final_distortion_images\side_hq_corrected_images'

CAM_TYPE = "side"
CAM_MODEL = "hq"

# Termination criteria
CRITERIA = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

################ FIND CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS #############################

def plot_chessboard_corners(obj_points):
    
    plt.scatter(obj_points[:, 0], obj_points[:, 1])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show(block=False)


def build_real_world_corner_positions(chessboard_grid_size=CHESSBOARD_GRID_SIZE,
                                      chessboard_tile_spacing=CHESSBOARD_TILE_SPACING,
                                      PLOT_CORNERS=False, PRINT_POINTS=False):
    """
    Same as generate_object_points in claibration_functions.py, but with more
    printing info
    """
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    obj_points = np.zeros((chessboard_grid_size[0] * chessboard_grid_size[1], 3), np.float32)
    obj_points[:,:2] = np.mgrid[0:chessboard_grid_size[0],0:chessboard_grid_size[1]].T.reshape(-1,2)
    scaled_obj_points = obj_points * chessboard_tile_spacing
    
    if PRINT_POINTS:
        print("Original points {}".format(obj_points))
        print("Scaled points {}".format(scaled_obj_points))
        print("Number of valid chessboard corners: {}".format(len(scaled_obj_points)))
    
    if PLOT_CORNERS:
        plot_chessboard_corners(scaled_obj_points)
    
    return obj_points


def extract_corners_from_distorted_images(obj_points, image_paths=DISTORTED_IMAGE_PATHS,
                                          criteria=CRITERIA, SHOW_IMAGES=False,
                                          chessboard_grid_size=CHESSBOARD_GRID_SIZE):
    """
    Should test if adaptive thresholding the images removes the light reflections,
    and thus increases the amount of usable images.
    """
    
    # Two sets of points for all usable images
    obj_points_array = [] # 3d point in real world space - how if the tilting is not encoded and z set to zero throughout?
    img_points_array = [] # 2d points in image plane.

    for count, image in enumerate(image_paths):

        img = cv.imread(image)
        grey_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        # Find the chess board corners
        ret, corners = cv2.findChessboardCornersSB(grey_image, chessboard_grid_size, flags=cv2.CALIB_CB_EXHAUSTIVE)

        # If corners found, add object points, image points (after refining them)
        if ret:

            obj_points_array.append(obj_points)
            optimised_corners = cv.cornerSubPix(grey_image, corners, (11,11), (-1,-1), criteria)
            img_points_array.append(optimised_corners)

            if SHOW_IMAGES:
                cv.drawChessboardCorners(img, chessboard_grid_size, optimised_corners, ret)
                cv.namedWindow("Distortion Image", cv.WINDOW_NORMAL)
                cv.imshow("Distortion Image", img)
                cv.waitKey(1000)
            
        else:
            print("Image {} could not be used...".format(count))
    
    cv.destroyAllWindows()
    return obj_points_array, img_points_array


############## CALIBRATION #######################################################

def save_camera_calibration(camera_matrix, dist, camera_type=CAM_TYPE, camera_model=CAM_MODEL):
    pickle.dump((camera_matrix, dist), open("distortion_calibration_data\{}_{}_camera_calibration.pkl".format(camera_type, camera_model), "wb" ))

def load_camera_calibration(calibration_data_path):
    
    with open(calibration_data_path, "rb") as data:
        camera_matrix, dist = pickle.load(data)
    return camera_matrix, dist


############## UNDISTORTION #####################################################

def undistort_image(camera_matrix, dist, frame_size, image_path=TEST_IMAGE, save_image=False,
                    output_directory=UNDISTORTED_IMAGE_DIRECTORY, SHOW_IMAGE=False):
    """
    Currently, I interpret the cali.png used by Robin as a test image to see
    the distortion corrction. The chessboard images are used specifically
    to build the undistortion map.
    
    roi: rectangle specifying area of undistorted image with valid image data
    dist: distortion coefficients
    alpha: set to 1 in cv.undistort (sets scale of new camera matrix)
    """
    
    img = cv.imread(image_path)
    
    if SHOW_IMAGE:
        cv.namedWindow("Test Image", cv.WINDOW_NORMAL)
        cv.imshow("Test Image", img)
        cv.waitKey(2000)

    h, w = frame_size
    
    newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist, (w,h), 1, (w,h))

    undistorted_image = cv.undistort(img, camera_matrix, dist, None, newCameraMatrix)
    
    # crop the image
    x, y, w, h = roi
    cropped_undistorted_image = undistorted_image[y:y+h, x:x+w]
    if save_image:
        cv.imwrite(output_directory + r'\undistorted_test_1.jpeg', cropped_undistorted_image)
    
    return cropped_undistorted_image # First method being returned


def calculate_reprojection_error(obj_points_array, img_points_array,
                                 camera_matrix, dist, rvecs, tvecs):
    """
    Need to check what this is doing...
    """
    
    mean_error = 0
    for i in range(len(obj_points_array)):
        imgpoints_2, _ = cv.projectPoints(obj_points_array[i], rvecs[i], tvecs[i], camera_matrix, dist)
        error = cv.norm(img_points_array[i], imgpoints_2, cv.NORM_L2)/len(imgpoints_2)
        mean_error += error
    
    total_error = mean_error/len(obj_points_array)
    return total_error
    

def main(test_image_path=TEST_IMAGE):
    
    obj_points = build_real_world_corner_positions(PLOT_CORNERS=False)
    obj_points_array, img_points_array = extract_corners_from_distorted_images(obj_points, SHOW_IMAGES=False)

    frame_size = determine_frame_size(image_path=test_image_path)
    ret, camera_matrix, dist, rvecs, tvecs = cv.calibrateCamera(obj_points_array, img_points_array, frame_size,
                                                                None, None)
    
    print("Original camera matrix: \n {}".format(camera_matrix))
    
    save_camera_calibration(camera_matrix, dist)
    undistort_image(camera_matrix, dist, frame_size, save_image=True)
    print( "Total error: {}".format(calculate_reprojection_error(obj_points_array, img_points_array,
                                                                 camera_matrix, dist, rvecs, tvecs)))


if __name__ == "__main__":
    main()
