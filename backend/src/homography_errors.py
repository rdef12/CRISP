import numpy as np
import cv2
from src.calibration_functions import *

############################################ Remove to general calibration code START ####################################
def convert_inhomogeneous_to_homogeneous_image_points(inhomogeneous_image_points):
    ones = np.ones((inhomogeneous_image_points.shape[0], 1, 1), dtype=inhomogeneous_image_points.dtype)
    homogeneous_image_points = np.concatenate((inhomogeneous_image_points, ones), axis=2)
    return homogeneous_image_points

def convert_homogeneous_image_coordinate_to_world(homogeneous_image_coordinate, homography_matrix):
    homogeneous_world_coordinate = homography_matrix.dot(homogeneous_image_coordinate.reshape(3,))
    return homogeneous_world_coordinate

def convert_pixel_to_homogeneous_coordinates(pixel):
    homogeneous_pixel_coordinate = np.concatenate((pixel, np.ones((len(pixel), 1, 1))), axis=2)
    return homogeneous_pixel_coordinate


############################################ Remove to general calibration code END ####################################

def find_position_jacobian(homogeneous_image_position, homography_matrix):
    """2x3"""
    homogeneous_world_position = convert_homogeneous_image_coordinate_to_world(homogeneous_image_position, homography_matrix)
    x_world_position = homogeneous_world_position[0]
    y_world_position = homogeneous_world_position[1]
    w = homogeneous_world_position[2]
    position_jacobian = np.zeros((2, 3))
    position_jacobian[0] = (homography_matrix[0] / w) - (x_world_position / w**2)*homography_matrix[2]
    position_jacobian[1] = (homography_matrix[1] / w) - (y_world_position / w**2)*homography_matrix[2]
    return position_jacobian


def find_homography_jacobian(homogeneous_pixels, homogeneous_positions):
    "2N x 9"
    jacobian_new = np.zeros((2*len(homogeneous_pixels), 9))
    for count, homogeneous_pixel in enumerate(homogeneous_pixels):
        x_image_point = homogeneous_pixel[0][0]
        y_image_point = homogeneous_pixel[0][1]
        x_world_point = homogeneous_positions[count][0][0]
        y_world_point = homogeneous_positions[count][0][1]
        w = homogeneous_positions[0][0][2]
        jacobian_new[2*count] = np.array([x_image_point / w,
                                          y_image_point / w,
                                          1 / w,
                                          0,
                                          0,
                                          0,
                                          -(x_world_point / w**2)*x_image_point,
                                          -(x_world_point / w**2)*y_image_point,
                                          -(x_world_point / w**2)])
        jacobian_new[2*count + 1] = np.array([0,
                                              0,
                                              0,
                                              x_image_point / w,
                                              y_image_point / w,
                                              1 / w,
                                              -(y_world_point / w**2)*x_image_point,
                                              -(y_world_point / w**2)*y_image_point,
                                              -(y_world_point / w**2)])
    return jacobian_new


# def find_homography_jacobian(homogeneous_pixels, homogeneous_positions):
#     num_points = len(homogeneous_pixels)
#     jacobian = np.zeros((2 * num_points, 9))
    
#     w = homogeneous_positions[:, 0, 2]
#     x_img, y_img = homogeneous_pixels[:, 0, 0], homogeneous_pixels[:, 0, 1]
#     x_world, y_world = homogeneous_positions[:, 0, 0], homogeneous_positions[:, 0, 1]

#     jacobian[::2, :3] = np.column_stack((x_img / w, y_img / w, 1 / w))
#     jacobian[1::2, 3:6] = np.column_stack((x_img / w, y_img / w, 1 / w))
#     jacobian[::2, 6:] = -np.column_stack((x_world * x_img / w**2, x_world * y_img / w**2, x_world / w**2))
#     jacobian[1::2, 6:] = -np.column_stack((y_world * x_img / w**2, y_world * y_img / w**2, y_world / w**2))
    
#     return jacobian


def find_descending_order_eigen_info(square_matrix):
    eigen_values, eigen_vectors = np.linalg.eig(square_matrix)
    sorted_indices = np.argsort(eigen_values)[::-1]
    sorted_eigenvalues = eigen_values[sorted_indices]
    sorted_eigenvectors = eigen_vectors[:, sorted_indices]
    return sorted_eigenvalues, sorted_eigenvectors


def generate_householder_matrix(eigen_values, eigen_vectors, exclude_eigen_values_beyond=8): # Set to 8 to exclude only the smallest Eval and Evec
    
    temp_house_holder_matrix = np.zeros((9,9))
    for count, eigen_vector in enumerate(eigen_vectors):
        if count >= exclude_eigen_values_beyond:
            continue
        
        temp_house_holder_matrix += np.outer(eigen_vector, eigen_vector)/eigen_values[count]
        
    min_abs_value = np.min(np.abs(temp_house_holder_matrix))
    smallest_abs_order_of_magnitude = np.floor(np.log10(min_abs_value))
    print("\n\n\nOrder of Magnitude of Minimum Absolute Value in Householder Matrix:", smallest_abs_order_of_magnitude)
    
    # Repeat calculation but with this scale factor applied to elimiate precision errors for small float values.
    house_holder_matrix = np.zeros((9,9))
    for count, eigen_vector in enumerate(eigen_vectors):
        if count >= exclude_eigen_values_beyond:
            continue
    
        # Multiplying eigenvectors by huge scale factor, and this factor actually cancels out!
        # Should be no risk of going above the upper floating point precision limit (HACK)
        eigen_vector *= (-1 * smallest_abs_order_of_magnitude + 9) # factor of 1,000,000,000 overboard to be safe
        house_holder_matrix += np.outer(eigen_vector, eigen_vector)/eigen_values[count]

    return house_holder_matrix


def find_homography_covariance_matrix(homography_jacobian, pixel_uncertainty_covariance_matrix):
    
    matrix_to_pseudo_inverse = homography_jacobian.T @ np.linalg.inv(pixel_uncertainty_covariance_matrix) @ homography_jacobian
    # matrix_to_pseudo_inverse = homography_jacobian.T @ np.linalg.pinv(pixel_uncertainty_covariance_matrix) @ homography_jacobian
    
    eigen_values, eigen_vectors = find_descending_order_eigen_info(matrix_to_pseudo_inverse)
    house_holder_matrix = generate_householder_matrix(eigen_values, eigen_vectors)
    
    homography_covariance = house_holder_matrix @ np.linalg.inv(house_holder_matrix.T @ matrix_to_pseudo_inverse @ house_holder_matrix) @ house_holder_matrix.T
    return homography_covariance


def generate_B_3x9_position_matrix(x_position_image: float, y_position_image: float):
    B_3x9_position_matrix = np.zeros((3, 9))
    # Set x'sf
    B_3x9_position_matrix[0][0] = x_position_image
    B_3x9_position_matrix[1][3] = x_position_image
    B_3x9_position_matrix[2][6] = x_position_image
    # Set y's
    B_3x9_position_matrix[0][1] = y_position_image
    B_3x9_position_matrix[1][4] = y_position_image
    B_3x9_position_matrix[2][7] = y_position_image
    # Set w's
    B_3x9_position_matrix[0][2] = 1
    B_3x9_position_matrix[1][5] = 1
    B_3x9_position_matrix[2][8] = 1
    return B_3x9_position_matrix

def find_delta_f_matrix(homogeneous_world_point):
    world_x = homogeneous_world_point[0][0][0]
    world_y = homogeneous_world_point[0][0][1]
    w = homogeneous_world_point[0][0][2]
    delta_f_matrix = np.zeros((2, 3))
    delta_f_matrix[0] = np.array([w, 0, world_x])
    delta_f_matrix[1] = np.array([0, w, world_y])
    delta_f_matrix *= 1/(w**2)
    return delta_f_matrix


def find_measured_points_covariance_matrix(estimated_measured_points_uncertainties):
    estimated_measured_points_variances = estimated_measured_points_uncertainties**2
    flattened_variances = estimated_measured_points_variances.flatten()
    measured_point_covariance_matrix = np.diag(flattened_variances)
    return measured_point_covariance_matrix

def calculate_homography_position_covariance(pixel_of_interest, homography_matrix, homography_covariance):
    homogeneous_pixel_of_interest = convert_pixel_to_homogeneous_coordinates(pixel_of_interest)
    homogeneous_point_of_interest = convert_homogeneous_image_coordinate_to_world(homogeneous_pixel_of_interest, homography_matrix)
    homogeneous_point_of_interest = homogeneous_point_of_interest.reshape((1, 1, 3))

    B_matrix = generate_B_3x9_position_matrix(pixel_of_interest[0][0][0], pixel_of_interest[0][0][1])
    delta_f = find_delta_f_matrix(homogeneous_point_of_interest)
    point_covariance_3x3 = B_matrix @ homography_covariance @ B_matrix.T
    homography_position_covariance = delta_f @ point_covariance_3x3 @ delta_f.T
    return homography_position_covariance


def calculate_covariance_from_homography(image_point, image_grid_positions, homography_matrix, x_grid_uncertainties, y_grid_uncertainties):
    homogeneous_image_grid_positions = convert_inhomogeneous_to_homogeneous_image_points(image_grid_positions)
    homogeneous_world_grid_positions = np.zeros((len(image_grid_positions), 1, 3))

    for count, homogeneous_image_grid_position in enumerate(homogeneous_image_grid_positions):
        homogeneous_world_grid_positions[count] = convert_homogeneous_image_coordinate_to_world(homogeneous_image_grid_position, homography_matrix)

    homography_jacobian = find_homography_jacobian(homogeneous_image_grid_positions, homogeneous_world_grid_positions) 

    uncertainties = np.column_stack((x_grid_uncertainties, y_grid_uncertainties))
    grid_measurement_covariance = find_measured_points_covariance_matrix(uncertainties) 

    homography_covariance = find_homography_covariance_matrix(homography_jacobian, grid_measurement_covariance)
    covariance_from_homography = calculate_homography_position_covariance(image_point, homography_matrix, homography_covariance)
    return covariance_from_homography


def calculate_homogeneous_covariance_from_homography(image_point, image_grid_positions, homography_matrix, x_grid_uncertainties, y_grid_uncertainties):
    homogeneous_image_grid_positions = convert_inhomogeneous_to_homogeneous_image_points(image_grid_positions)
    homogeneous_world_grid_positions = np.zeros((len(image_grid_positions), 1, 3))

    for count, homogeneous_image_grid_position in enumerate(homogeneous_image_grid_positions):
        homogeneous_world_grid_positions[count] = convert_homogeneous_image_coordinate_to_world(homogeneous_image_grid_position, homography_matrix)

    homography_jacobian = find_homography_jacobian(homogeneous_image_grid_positions, homogeneous_world_grid_positions) 

    uncertainties = np.column_stack((x_grid_uncertainties, y_grid_uncertainties))
    grid_measurement_covariance = find_measured_points_covariance_matrix(uncertainties) 

    homography_covariance = find_homography_covariance_matrix(homography_jacobian, grid_measurement_covariance)

    B_matrix = generate_B_3x9_position_matrix(image_point[0][0][0], image_point[0][0][1])

    homogeneous_covariance_from_homography = B_matrix @ homography_covariance @ B_matrix.T
    return homogeneous_covariance_from_homography


def calculate_covariance_from_pixel_selection(image_point, homography_matrix, x_pixel_uncertainty, y_pixel_uncertainty):
    pixel_covariance = np.array([[x_pixel_uncertainty**2, 0, 0],
                                 [0, y_pixel_uncertainty**2, 0],
                                 [0, 0, 0]])
    homogeneous_image_point = np.append(image_point, 1)
    position_jacobian = find_position_jacobian(homogeneous_image_point, homography_matrix)
    covariance_from_pixel_selection = position_jacobian @ pixel_covariance @ position_jacobian.T
    # print(covariance_from_pixel_selection.shape)
    return covariance_from_pixel_selection


def calculate_world_point_uncertainty(image_point, x_pixel_uncertainty, y_pixel_uncertainty, homography_matrix, image_grid_points, x_grid_uncertainties, y_grid_uncertainties): # Should world grid points be an argument?
    covariance_from_homography = calculate_covariance_from_homography(image_point, image_grid_points, homography_matrix, x_grid_uncertainties, y_grid_uncertainties)
    covariance_from_pixel_selection = calculate_covariance_from_pixel_selection(image_point, homography_matrix, x_pixel_uncertainty, y_pixel_uncertainty)
    
    print("Covariance from Homography:", covariance_from_homography)
    print("Covariance from Pixel Selection:", covariance_from_pixel_selection)
    
    world_point_covariance = covariance_from_homography + covariance_from_pixel_selection
    print("World Point Covariance Matrix:", world_point_covariance)
    x_variance = world_point_covariance[0, 0]
    y_variance = world_point_covariance[1, 1]
    
    print("X Variance:", x_variance, "Y Variance:", y_variance)
    
    x_uncertainty = np.sqrt(x_variance)
    y_uncertainty = np.sqrt(y_variance)
    
    # print(x_uncertainty, y_uncertainty)
    return [x_uncertainty, y_uncertainty]


############################ MADE FOR IMPORTING IN SEMESTER TWO #########################

def generate_homography_covariance_matrix(image_grid_positions, homography_matrix, grid_uncertainties_array):
    
    homogeneous_image_grid_positions = convert_inhomogeneous_to_homogeneous_image_points(image_grid_positions)
    homogeneous_world_grid_positions = np.zeros((len(image_grid_positions), 1, 3))
    for count, homogeneous_image_grid_position in enumerate(homogeneous_image_grid_positions):
        homogeneous_world_grid_positions[count] = convert_homogeneous_image_coordinate_to_world(homogeneous_image_grid_position, homography_matrix)

    homography_jacobian = find_homography_jacobian(homogeneous_image_grid_positions, homogeneous_world_grid_positions) 

    grid_measurement_covariance = find_measured_points_covariance_matrix(grid_uncertainties_array) 
    
    return find_homography_covariance_matrix(homography_jacobian, grid_measurement_covariance)
    #return np.zeros((9, 9))


def generate_world_point_uncertainty(image_point, x_pixel_uncertainty, y_pixel_uncertainty, homography_matrix, homography_covariance):
    
    covariance_from_homography = calculate_homography_position_covariance(image_point, homography_matrix, homography_covariance)   
    # print("Covariance from Homography:", covariance_from_homography)
    covariance_from_pixel_selection = calculate_covariance_from_pixel_selection(image_point, homography_matrix, x_pixel_uncertainty, y_pixel_uncertainty)
    # print("Covariance from Pixel Selection:", covariance_from_pixel_selection)
    
    world_point_covariance = covariance_from_homography + covariance_from_pixel_selection
    # print("World Point Covariance Matrix:", world_point_covariance)
    x_variance, y_variance = world_point_covariance[0, 0],  world_point_covariance[1, 1]
    # print("X Variance:", x_variance, "Y Variance:", y_variance)
    x_uncertainty, y_uncertainty = np.sqrt(x_variance), np.sqrt(y_variance)
    
    return [x_uncertainty, y_uncertainty]