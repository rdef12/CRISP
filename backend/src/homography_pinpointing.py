# -*- coding: utf-8 -*-
"""
TODO: Need to propagate uncertainty in calibration board thickness at the physical position uncertainty stage.
(Already done in the unc_tangent_of_angle functions)

TODO: Instead of just using the mid point of closest points as the intersection point, could this be a
weighted average of the two closest points?
 """
from src.calibration_functions import *
from src.uncertainty_functions import *
from src.viewing_functions import *
from src.homography_errors import generate_world_point_uncertainty
from src.database.CRUD import CRISP_database_interaction as cdi

from typing import List, Literal
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import itertools

SCINTILLATOR_REFRACTIVE_INDEX = 1.66
UNC_SCINTILLATOR_REFRACTIVE_INDEX = 0

TOP_CAM_ID = "A"
SIDE_CAM_ID = "B"

CAM_OPTICAL_AXIS = {"A": "y", "B": "x"}

SCINTILLATOR_DEPTH = {"x": 38.8, "y": 99.8} # mm
SCINTILLATOR_DEPTH_UNC = {"x": 0.1, "y": 0.1} # mm

# These start out as 2D pixel coordinates, but are converted to 3D physical positions in Camera class
ORIGIN_SHIFT = {"A": [1, 1], "B": [1, 1]} # mm # NEED TO EDIT
ORIGIN_SHIFT_UNC = {"A": [0.5, 0.5], "B": [0.1, 0.1]} # mm

CALIBRATION_BOARD_THICKNESS = {"A": 0.8, "B": 2.8} # mm
CALIBRATION_BOARD_THICKNESS_UNC  = {"A": 0.1, "B": 0.1} # mm

DEPTH_DIRECTION = {"A": 1, "B": 1}

class BoxCoordinate(Enum):
    X = 0
    Y = 1
    Z = 2

@dataclass
class AxesMapping:
    horizontal_img_axis: Literal["x", "y", "z"]
    vertical_img_axis: Literal["x", "y", "z"]
    optical_axis: Literal["x", "y", "z"]
    depth_direction: Literal[-1, 1]  # Specifies which side of optical axis the camera is
    
    # Called automatically after AxesMapping object is created
    def __post_init__(self):
        # Check if the axes are unique
        axes = [self.horizontal_img_axis, self.vertical_img_axis, self.optical_axis]
        if len(set(axes)) != len(axes):
            raise ValueError("Axes values must be unique: no two axes can have the same direction.")


# Abstract base class
class AbstractCamera(ABC):
    # Factory for producing cameras
    @staticmethod
    def setup(camera_id, setup_id):
            camera_optical_axis = CAM_OPTICAL_AXIS.get(camera_id)
            match camera_optical_axis:
                case "y":
                    return TopCamera(camera_id, setup_id)
                case "x":
                    return SideCamera(camera_id, setup_id)
                case _:
                    raise ValueError("Unknown camera axis: {} \Valid types are {'x', 'y'}".format(camera_optical_axis))
            
    def __init__(self, camera_id, setup_id):
        
        if type(self) is AbstractCamera:
            raise NotImplementedError("AbstractCamera class is abstract, use AbstractCamera.setup(camera_id, setup_id) to intialise a camera object.")
        
        self.front_homography_matrix= cdi.get_near_face_homography_matrix(camera_id, setup_id)
        self.front_homography_covariance = cdi.get_near_face_homography_covariance_matrix(camera_id, setup_id)
        self.back_homography_matrix = cdi.get_far_face_homography_matrix(camera_id, setup_id)
        self.back_homography_covariance = cdi.get_far_face_homography_covariance_matrix(camera_id, setup_id)
        
        self.seen_scintillator_depth = SCINTILLATOR_DEPTH.get(CAM_OPTICAL_AXIS.get(camera_id))
        self.seen_scintillator_depth_uncertainty = SCINTILLATOR_DEPTH_UNC.get(CAM_OPTICAL_AXIS.get(camera_id))
        
        self.origin_shift = ORIGIN_SHIFT.get(camera_id) # shift from origin of calibration pattern to the nearest corner of the calibration board (for shifting coordinate systems)
        self.origin_shift_uncertainty = ORIGIN_SHIFT_UNC.get(camera_id)
        self.calibration_board_thickness = CALIBRATION_BOARD_THICKNESS.get(camera_id)
        self.calibration_board_thickness_unc = CALIBRATION_BOARD_THICKNESS_UNC.get(camera_id)
        
        # New private method implemented in the subclasses
        self.axes_mapping = self._map_axes(DEPTH_DIRECTION.get(camera_id))
        
    def map_image_coord_to_3d_point(self, horizontal_in_calibration_plane: float, 
                        vertical_in_calibration_plane: float, 
                        depth: float) -> np.ndarray:
        """
        depth is inputted and depends on which plane the user is looking at (far or near)
        """
        # Create a dictionary to map the axes to corresponding values
        three_dimenisional_coords = {'x': None, 'y': None, 'z': None}
        
        # Map horizontal, vertical, and optical axes to their respective values
        three_dimenisional_coords[self.axes_mapping.horizontal_img_axis] = horizontal_in_calibration_plane
        three_dimenisional_coords[self.axes_mapping.vertical_img_axis] = vertical_in_calibration_plane
        three_dimenisional_coords[self.axes_mapping.optical_axis] = depth

        # Check if any axis is None
        if None in three_dimenisional_coords.values():
            raise ValueError("Mapping is incomplete, one or more axes are missing.")
    
        return np.array([three_dimenisional_coords['x'], three_dimenisional_coords['y'], three_dimenisional_coords['z']])
    
    
    def _calculate_two_dimensional_homography_errors(self, pixel_coords: tuple[float, float], unc_pixel_coords: tuple[float, float]):
        """
        Pixel coords given type float because we believe sub pixel uncertainty is feasible for the scintillation light analysis
        """
        near_plane_two_dimensional_homography_error = generate_world_point_uncertainty([[pixel_coords]], unc_pixel_coords[0], unc_pixel_coords[1], self.front_homography_matrix, self.front_homography_covariance)
        far_plane_two_dimensional_position_homography_error = generate_world_point_uncertainty([[pixel_coords]], unc_pixel_coords[0], unc_pixel_coords[1], self.back_homography_matrix, self.back_homography_covariance)
        return near_plane_two_dimensional_homography_error, far_plane_two_dimensional_position_homography_error
        
    def _calculate_calibration_plane_physical_position_error(two_dimensional_homography_errors: List[float], two_dimensional_origin_shift_errors: List[float]):
        """
        Includes error introduced by homography and origin shift. Does not include the depth uncertainty due to scintillator dimensions/calibration board thickness.
        """
        horizontal_errror = normal_addition_in_quadrature([two_dimensional_homography_errors[0], two_dimensional_origin_shift_errors[0]])
        vertical_error = normal_addition_in_quadrature([two_dimensional_homography_errors[1], two_dimensional_origin_shift_errors[1]])
        return [horizontal_errror, vertical_error]
    
    
    def _calculate_uncertainty_in_tangent_of_angles(self, in_plane_displacement: float, near_plane_position_unc: float, far_plane_position_unc: float,
                                                  tan_phi: float, tan_theta: float):
        """
        Note: the origin shift translation cancels out when taking the difference between the two planes. Therefore, it is not included in the position
        uncertainties when propagating in quadrature because it does not influence the calculated in-plane displacement.
        """

        uncertainty_in_horizontal_position_difference = normal_addition_in_quadrature([near_plane_position_unc[0],
                                                                                       far_plane_position_unc[0]])
        uncertainty_in_vertical_position_difference = normal_addition_in_quadrature([near_plane_position_unc[1],
                                                                                     far_plane_position_unc[1]])
        
        denominator = self.seen_scintillator_depth + self.calibration_board_thickness
        unc_denominator = normal_addition_in_quadrature([self.scintillator_depth_uncertainty, self.calibration_board_thickness_unc])
        
        # Looking at horizontal displacement
        unc_tan_phi = fractional_addition_in_quadrature([in_plane_displacement[0], denominator], 
                                                        [uncertainty_in_horizontal_position_difference, unc_denominator],
                                                        tan_phi)
        # Looing at vertical displacement
        unc_tan_theta = fractional_addition_in_quadrature([in_plane_displacement[1], denominator], 
                                                          [uncertainty_in_vertical_position_difference, unc_denominator],
                                                          tan_theta)
        return unc_tan_phi, unc_tan_theta
     
       
    def _transform_to_box_coords(self, physical_position_on_calibration_plane: tuple[float, float], two_dimensional_homography_errors: List[float], plane_type: Literal["far", "near"]) -> np.ndarray:

        # 4 cases for appropriate depths depending on plane_type and depth_direction
        match (plane_type, self.axes_mapping.depth_direction):
            case ("far", 1):
                depth = 0
                unc_depth = 0
            case ("far", -1):
                depth = self.seen_scintillator_depth # no calibration board shift
                unc_depth = self.seen_scintillator_depth_uncertainty
            case ("near", 1):
                depth = self.seen_scintillator_depth + self.calibration_board_thickness
                unc_depth = normal_addition_in_quadrature([self.seen_scintillator_depth_uncertainty, self.calibration_board_thickness_unc])
            case ("near", -1):
                depth = -1 * self.calibration_board_thickness 
                unc_depth = self.calibration_board_thickness_unc

        # Below is the origin transformation! For this to work, the user-inputted origin shifts need to be signed correctly (although should always be positive)?
        two_dimensional_position_relative_to_calibration_board_corner = np.array(physical_position_on_calibration_plane) + np.array(self.origin_shift) # mm units
        two_dimensional_position_relative_to_calibration_board_corner_unc = self._calculate_calibration_plane_physical_position_error(two_dimensional_homography_errors, self.origin_shift_uncertainty)
        
        physical_position_in_box_coords = self.map_image_coord_to_3d_point(two_dimensional_position_relative_to_calibration_board_corner[0],
                                                                two_dimensional_position_relative_to_calibration_board_corner[1], depth)
        physical_position_in_box_coords_uncertainty = self.map_image_coord_to_3d_point(two_dimensional_position_relative_to_calibration_board_corner_unc[0],
                                                                           two_dimensional_position_relative_to_calibration_board_corner_unc[1],
                                                                           unc_depth)
        
        return physical_position_in_box_coords, physical_position_in_box_coords_uncertainty
    
    
    def determine_in_plane_positions_and_angles_of_event(self, pixel_coords: tuple[float, float], unc_pixel_coords: tuple[float, float]):
        """
        phi: horizontal angle as seen through image looking down optical axis.
        theta: vertical angle as seen through image looking down optical axis.
        """
        physical_position_on_near_calibration_plane = get_projected_position_of_pixel(self.front_homography_matrix,
                                                                                  pixel_coords=pixel_coords)
        physical_position_on_far_calibration_plane = get_projected_position_of_pixel(self.back_homography_matrix,
                                                                                  pixel_coords=pixel_coords)
        
        near_plane_two_dimensional_homography_error, far_plane_two_dimensional_position_homography_error = self._calculate_two_dimensional_homography_errors(pixel_coords, unc_pixel_coords)
        
        physical_displacement_in_plane_coords = physical_position_on_far_calibration_plane - physical_position_on_near_calibration_plane
        tan_phi, tan_theta = physical_displacement_in_plane_coords / (self.seen_scintillator_depth + self.calibration_board_thickness)
        unc_tan_phi, unc_tan_theta = self._calculate_uncertainty_in_tangent_of_angles(physical_displacement_in_plane_coords, near_plane_two_dimensional_homography_error,
                                                                                     far_plane_two_dimensional_position_homography_error, tan_phi, tan_theta)
        
        near_physical_position_in_box_coords, unc_near_physical_position_in_box_coords = self._transform_to_box_coords(physical_position_on_near_calibration_plane.copy(), 
                                                                                                                       near_plane_two_dimensional_homography_error, "near")
        far_physical_position_in_box_coords, unc_far_physical_position_in_box_coords = self._transform_to_box_coords(physical_position_on_far_calibration_plane.copy(), 
                                                                                                                     far_plane_two_dimensional_position_homography_error, "far")

        return ([tan_phi, tan_theta], 
                [unc_tan_phi, unc_tan_theta], 
                [near_physical_position_in_box_coords, far_physical_position_in_box_coords], 
                [unc_near_physical_position_in_box_coords, unc_far_physical_position_in_box_coords]
            )
    
    @abstractmethod
    def _map_axes(self, depth_direction: int):
        """Virtual function which must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def build_line_vectors(self, physical_position_on_back_calibration_plane: float, tan_phi: float, tan_theta: float):
        """Virtual function which must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def add_shift_in_parameterising_position_due_to_refraction(self, physical_position_on_front_plane: float, physical_position_on_front_plane_uncertainty: float,
                                                                unrefracted_tan_phi: float, unrefracted_tan_theta: float,
                                                                unc_unrefracted_tan_phi: float, unc_unrefracted_tan_theta: float):
        """Virtual function which must be implemented by subclasses."""
        pass


class TopCamera(AbstractCamera):
    
    def __init__(self, camera_id, setup_id):
        super().__init__(camera_id, setup_id)
        
    def _map_axes(self, depth_direction: int):
        self.axes_mapping = AxesMapping(horizontal_img_axis="z",
                                        vertical_img_axis="x",
                                        optical_axis="y",
                                        depth_direction=depth_direction)
    
    def build_line_vectors(self, physical_position_on_back_calibration_plane: float, tan_phi: float, tan_theta: float,
                           unc_tan_phi: float, unc_tan_theta: float):
        
        directional_vector = np.array([tan_theta, -1, tan_phi])
        direction_vector_uncertainty = np.array([unc_tan_theta, 0, unc_tan_phi])
        return [physical_position_on_back_calibration_plane, directional_vector], direction_vector_uncertainty # returning the initial position too!
    
        
    def add_shift_in_parameterising_position_due_to_refraction(self, physical_position_on_front_plane: float, physical_position_on_front_plane_uncertainty: float,
                                                                unrefracted_tan_phi: float, unrefracted_tan_theta: float,
                                                                unc_unrefracted_tan_phi: float, unc_unrefracted_tan_theta: float):
        
        shifted_box_coord_for_horizontal_image_coord = physical_position_on_front_plane[BoxCoordinate.Z] + (self.calibration_board_thickness * unrefracted_tan_phi)
        shifted_box_coord_for_vertical_image_coord = physical_position_on_front_plane[BoxCoordinate.X] + (self.calibration_board_thickness * unrefracted_tan_theta)
        
        unc_added_horizontal_term = fractional_addition_in_quadrature([self.calibration_board_thickness, unrefracted_tan_phi],
                                                                      [self.calibration_board_thickness_unc, unc_unrefracted_tan_phi], 
                                                                       self.calibration_board_thickness * unrefracted_tan_phi)
        unc_added_vertical_term = fractional_addition_in_quadrature([self.calibration_board_thickness, unrefracted_tan_theta],
                                                                      [self.calibration_board_thickness_unc, unc_unrefracted_tan_theta], 
                                                                       self.calibration_board_thickness * unrefracted_tan_theta)
        
        # +/- calibration board thickness shift depending on which side of the optical axis the camera is relative to the box's coord system origin
        match self.axes_mapping.depth_direction:
            case 1:
                shifted_box_coord_for_optical_axis_coord = self.seen_scintillator_depth
                unc_shifted_box_coord_for_optical_axis_coord = self.seen_scintillator_depth_uncertainty
            case -1:
                shifted_box_coord_for_optical_axis_coord = 0
                unc_shifted_box_coord_for_optical_axis_coord = 0
        
        # Z Horizontal, X Vertical, Y Optical 
        # Point on near plane being returned now (point on back plane would parameterise the line if no refraction present)
        shifted_near_plane_position = np.array([shifted_box_coord_for_vertical_image_coord, shifted_box_coord_for_optical_axis_coord, shifted_box_coord_for_horizontal_image_coord])
        
        original_x_unc, original_y_unc, original_z_unc = physical_position_on_front_plane_uncertainty 
        shifted_near_plane_position_uncertainty = np.array([normal_addition_in_quadrature([original_x_unc, unc_added_vertical_term]),
                                                            normal_addition_in_quadrature([original_y_unc, unc_shifted_box_coord_for_optical_axis_coord]),
                                                            normal_addition_in_quadrature([original_z_unc, unc_added_horizontal_term])])
    
        return shifted_near_plane_position, shifted_near_plane_position_uncertainty

class SideCamera(AbstractCamera):
    def __init__(self, camera_id, setup_id):
        super().__init__(camera_id, setup_id)
    
    def _map_axes(self, depth_direction: int):
        self.axes_mapping = AxesMapping(horizontal_img_axis="z",
                                        vertical_img_axis="y",
                                        optical_axis="x",
                                        depth_direction=depth_direction)
        
    def build_line_vectors(self, physical_position_on_back_calibration_plane: float, tan_phi: float, tan_theta: float,
                           unc_tan_phi: float, unc_tan_theta: float):
        
        directional_vector = np.array([-1, tan_theta, tan_phi])
        directional_vector_uncertainty = np.array([0, unc_tan_theta, unc_tan_phi])
        return [physical_position_on_back_calibration_plane, directional_vector], directional_vector_uncertainty
    
    def add_shift_in_parameterising_position_due_to_refraction(self, physical_position_on_front_plane: float, physical_position_on_front_plane_uncertainty: float,
                                                                unrefracted_tan_phi: float, unrefracted_tan_theta: float,
                                                                unc_unrefracted_tan_phi: float, unc_unrefracted_tan_theta: float):
        
        shifted_box_coord_for_horizontal_image_coord = physical_position_on_front_plane[BoxCoordinate.Z] + (self.calibration_board_thickness * unrefracted_tan_phi)
        shifted_box_coord_for_vertical_image_coord = physical_position_on_front_plane[BoxCoordinate.Y] + (self.calibration_board_thickness * unrefracted_tan_theta)
        
        
        unc_added_horizontal_term = fractional_addition_in_quadrature([self.calibration_board_thickness, unrefracted_tan_phi],
                                                                      [self.calibration_board_thickness_unc, unc_unrefracted_tan_phi], 
                                                                       self.calibration_board_thickness * unrefracted_tan_phi)
        unc_added_vertical_term = fractional_addition_in_quadrature([self.calibration_board_thickness, unrefracted_tan_theta],
                                                                      [self.calibration_board_thickness_unc, unc_unrefracted_tan_theta], 
                                                                       self.calibration_board_thickness * unrefracted_tan_theta)
        
        match self.axes_mapping.depth_direction:
            case 1:
                shifted_box_coord_for_optical_axis_coord = self.seen_scintillator_depth
                unc_shifted_box_coord_for_optical_axis_coord = self.seen_scintillator_depth_uncertainty
            case -1:
                shifted_box_coord_for_optical_axis_coord = 0
                unc_shifted_box_coord_for_optical_axis_coord = 0
                
        # Z Horizontal, Y Vertical, X Optical 
        # Point on near plane being returned now (point on back plane would parameterise the line if no refraction present)
        shifted_near_plane_position = np.array([shifted_box_coord_for_optical_axis_coord, shifted_box_coord_for_vertical_image_coord, shifted_box_coord_for_horizontal_image_coord])
                
        original_x_unc, original_y_unc, original_z_unc = physical_position_on_front_plane_uncertainty 
        shifted_near_plane_position_uncertainty = np.array([normal_addition_in_quadrature([original_x_unc, unc_shifted_box_coord_for_optical_axis_coord]),
                                                            normal_addition_in_quadrature([original_y_unc, unc_added_vertical_term]),
                                                            normal_addition_in_quadrature([original_z_unc, unc_added_horizontal_term])])
        
        return shifted_near_plane_position, shifted_near_plane_position_uncertainty


def get_projected_position_of_pixel(homography_matrix, pixel_coords: tuple[float, float]=None, 
                                    opencv_pixel: np.ndarray[float, float]=None):

    # Performs conversion to OpenCV form
    if pixel_coords:
        opencv_pixel = convert_iterable_to_opencv_format(pixel_coords)
    associated_real_position = convert_image_position_to_real_position(pixel=opencv_pixel, homography_matrix_input=homography_matrix)[0, 0]
    return associated_real_position


def calculate_3d_euclidian_distance(input_vector: np.ndarray[float]) -> float:

  try:
    if np.shape(input_vector) != (3, ):
      raise Exception("Incorrect vector shape. The input vector is of shape {}.".format(np.shape(input_vector)))
    return np.sqrt(input_vector[0]**2 + input_vector[1]**2 + input_vector[2]**2)
  
  except Exception as e:
    print("Error: {}".format(e))


def general_vector_line_equation(t: float, initial_position_vector: np.ndarray[float],
                                 directional_vector: np.ndarray[float]) -> np.ndarray[float]:
  """ Vector line equation parameterised by t."""
  return initial_position_vector + t * directional_vector
    

def calculate_uncertainty_on_tangent_of_refracted_angle_component(tan_angle: float, unc_tan_angle: float, n: float=SCINTILLATOR_REFRACTIVE_INDEX, unc_n: float=UNC_SCINTILLATOR_REFRACTIVE_INDEX):
    """
    n: refractive index of scintillator
    
    n.b. this works on a given tangent component. Therefore, this function is applied in various ways in the different
    camera subclasses.
    """
    # Terms 1 and 2 in derivative wrt n
    term_1 = -tan_angle / (n**2 * np.sqrt((tan_angle**2 + 1) * (1 - tan_angle**2 / (n**2 * (tan_angle**2 + 1)))))
    term_2 = -tan_angle**3 / (n**4 * ((tan_angle**2 + 1)* (1 - tan_angle**2 / ( n**2 * (tan_angle**2 + 1))))**(3/2))
    
    # Terms 3,4,5 belong to the derivative wrt tan_angle
    term_3 = -tan_angle**2 / (n * (tan_angle**2 + 1)**(3/2) * np.sqrt(1 - tan_angle**2 / (n**2 * (tan_angle**2 + 1))))
    term_4 = 1 / (n * np.sqrt(tan_angle**2 + 1) * np.sqrt(1 - tan_angle**2 / (n**2 * (tan_angle**2 + 1))))
    term_5_numerator = -2* tan_angle**2 * (tan_angle**2 / (n**2 * (tan_angle**2 + 1)**2) - 1 / (n**2 * (tan_angle**2 + 1)))
    term_5_denominator = 2 * n * np.sqrt(tan_angle**2 + 1) * (1 - tan_angle**2 / (n**2 * (tan_angle**2 + 1)))**(3/2)
    term_5 = term_5_numerator / term_5_denominator
     
    return np.sqrt(((term_3 + term_4 + term_5) * unc_tan_angle)**2 + ((term_1 + term_2) * unc_n)**2)


def build_uncertainty_in_tangent_of_refracted_angles(tan_phi, tan_theta, unc_tan_phi: float, unc_tan_theta: float,
                                                     n: float=SCINTILLATOR_REFRACTIVE_INDEX, unc_n=UNC_SCINTILLATOR_REFRACTIVE_INDEX):
        
        unc_tan_refracted_phi = calculate_uncertainty_on_tangent_of_refracted_angle_component(tan_phi, unc_tan_phi, n, unc_n)
        unc_tan_refracted_theta = calculate_uncertainty_on_tangent_of_refracted_angle_component(tan_theta, unc_tan_theta, n, unc_n)
        return unc_tan_refracted_phi, unc_tan_refracted_theta


def calculate_refracted_angles(incident_angles: np.ndarray[float], scintillator_refracative_index: float=SCINTILLATOR_REFRACTIVE_INDEX,
                               air_refractive_index: float=1) -> float:
    
    return np.arcsin(air_refractive_index * np.sin(incident_angles) / scintillator_refracative_index)


def calculate_distance_of_closest_approach(first_equation_line_vectors, second_equation_line_vectors) -> float:
  """
  Using distance of closest approach D defined here: https://mathworld.wolfram.com/Line-LineDistance.html
  """
  
  initial_positions_1, initial_positions_2 = first_equation_line_vectors[0], second_equation_line_vectors[0]
  directional_vector_1, directional_vector_2 = first_equation_line_vectors[1], second_equation_line_vectors[1]
  
  c = initial_positions_2 - initial_positions_1
  directional_vector_cross_product = np.cross(directional_vector_1, directional_vector_2)
  
  D = np.abs(np.dot(c, directional_vector_cross_product)) / calculate_3d_euclidian_distance(directional_vector_cross_product)
  return D


def calculate_uncertainty_on_position_on_one_line_closest_to_another_line(this_equation_line_vectors: np.ndarray[float, float], 
                                                                            other_equation_line_vectors: np.ndarray[float, float],
                                                                            this_equation_line_vectors_uncertainties: np.ndarray[float, float],
                                                                            other_equation_line_vectors_uncertainties: np.ndarray[float, float]):
  """
  https://en.wikipedia.org/wiki/Skew_lines#Distance gives the equations of these
  points, as c_1 and c_2.   N.B. the order of line vector input determines which line the point will be calculated along,
  where the notation being used is that for the calculation of c_1 throughout.
  """
  initial_positions_1, initial_positions_2 = this_equation_line_vectors[0], other_equation_line_vectors[0]
  directional_vector_1, directional_vector_2 = this_equation_line_vectors[1], other_equation_line_vectors[1]
  unc_initial_positions_1, unc_initial_positions_2 = this_equation_line_vectors_uncertainties[0], other_equation_line_vectors_uncertainties[0]
  unc_directional_vector_1, unc_directional_vector_2 = this_equation_line_vectors_uncertainties[1], other_equation_line_vectors_uncertainties[1]
 
  difference_in_initial_positions = initial_positions_2 - initial_positions_1
  unc_difference_in_intial_positions = np.array([normal_addition_in_quadrature([unc_initial_positions_1[i], unc_initial_positions_2[i]]) for i in range(3)])
    
  directional_vector_cross_product = np.cross(directional_vector_1, directional_vector_2)
  unc_directional_vector_cross_product = calculate_uncertainty_on_cross_product(directional_vector_1, directional_vector_2,
                                                                                unc_directional_vector_1, unc_directional_vector_2)

  n_1 = np.cross(directional_vector_1, directional_vector_cross_product)
  unc_n_1 = calculate_uncertainty_on_cross_product(directional_vector_1, directional_vector_cross_product,
                                                   unc_directional_vector_1, unc_directional_vector_cross_product)
  n_2 = np.cross(directional_vector_2, directional_vector_cross_product)
  unc_n_2 = calculate_uncertainty_on_cross_product(directional_vector_2, directional_vector_cross_product,
                                                   unc_directional_vector_2, unc_directional_vector_cross_product)

  prefactor_denominator = np.dot(directional_vector_1, n_2)
  unc_prefactor_denominatator = calculate_uncertainty_on_dot_product(directional_vector_1, n_2, unc_directional_vector_1, unc_n_2)
  prefactor_numerator = np.dot(difference_in_initial_positions, n_2)
  unc_prefactor_numerator = calculate_uncertainty_on_dot_product(difference_in_initial_positions, n_2, unc_difference_in_intial_positions, unc_n_2)
  prefactor =  prefactor_numerator / prefactor_denominator
  unc_prefactor = fractional_addition_in_quadrature([prefactor_numerator, prefactor_denominator], [unc_prefactor_numerator, unc_prefactor_denominatator], prefactor)
  
  unc_second_term_in_final_equation = np.array([fractional_addition_in_quadrature([prefactor, directional_vector_1[i]], [unc_prefactor, unc_directional_vector_1[i]], 
                                                                                  prefactor * directional_vector_1[i]) for i in range(3)])
  
  return np.array([normal_addition_in_quadrature([unc_initial_positions_1[i], unc_second_term_in_final_equation[i]]) for i in range(3)])


def calculate_intersection_point(first_equation_line_vectors, second_equation_line_vectors,
                                 first_equation_line_vectors_uncertainties, second_equation_line_vectors_uncertainties,
                                 tolerance=5): # This corresponds to a tolerance of 5 mm
  """
  The true Bragg peak lines seen by the two perpendicular cameras would necessarily intersect, having eminated from
  the same source, but errors in Bragg Peak selection may lead to the interpolated lines being skew.
  """
  
  try:
    distance_of_closest_approach = calculate_distance_of_closest_approach(first_equation_line_vectors, second_equation_line_vectors)
    if distance_of_closest_approach <= tolerance:
      
      initial_positions_1, initial_positions_2 = first_equation_line_vectors[0], second_equation_line_vectors[0]
      directional_vector_1, directional_vector_2 = first_equation_line_vectors[1], second_equation_line_vectors[1]
      
      directional_vector_cross_product = np.cross(directional_vector_1, directional_vector_2)
      n_1 = np.cross(directional_vector_1, directional_vector_cross_product)
      n_2 = np.cross(directional_vector_2, directional_vector_cross_product)
      difference_in_initial_positions = initial_positions_2 - initial_positions_1
      
      # See https://en.wikipedia.org/wiki/Skew_lines#Distancess
      closest_point_on_first_line_to_second_line = initial_positions_1 + directional_vector_1 * (
        np.dot(difference_in_initial_positions, n_2) / np.dot(directional_vector_1, n_2))
      unc_closest_point_on_first_line_to_second_line = calculate_uncertainty_on_position_on_one_line_closest_to_another_line(first_equation_line_vectors,
                                                                                                                            second_equation_line_vectors,
                                                                                                                            first_equation_line_vectors_uncertainties,
                                                                                                                            second_equation_line_vectors_uncertainties)
      
      closest_point_on_second_line_to_first_line = initial_positions_2 + directional_vector_2 * (
        np.dot(-difference_in_initial_positions, n_1) / np.dot(directional_vector_2, n_1))
      # Notice the line vectors and their uncertainties are passed in the opposite order this time.
      unc_closest_point_on_second_line_to_first_line = calculate_uncertainty_on_position_on_one_line_closest_to_another_line(second_equation_line_vectors,
                                                                                                                               first_equation_line_vectors,
                                                                                                                               second_equation_line_vectors_uncertainties,
                                                                                                                               first_equation_line_vectors_uncertainties)

      total_closest_points_error = np.array([normal_addition_in_quadrature([unc_closest_point_on_second_line_to_first_line[i], unc_closest_point_on_first_line_to_second_line[i]]) for i in range(3)])
      print("Total error added in quadrature between two closest points on interpolated lines is {}".format(total_closest_points_error))
      print("Vector of closest approach (magnitude of components taken) is {}".format(np.abs(closest_point_on_second_line_to_first_line - closest_point_on_first_line_to_second_line)))
      
      if not np.all(np.abs(closest_point_on_second_line_to_first_line - closest_point_on_first_line_to_second_line) <= 5 * total_closest_points_error): # CURRENTLY, LESS THAN 5 COMBINED STD
         
        # 5 standard deviations because operating on a huge number of beam center coords across all image sets, it becomes quite possible that one component has an error exceeding 5 STD.
        raise Exception("The seperation of two closest points is not consistent within 5 standard deviation of each of these points.")

      midpoint_between_closest_points_of_the_lines = (closest_point_on_second_line_to_first_line + closest_point_on_first_line_to_second_line ) / 2 # this is the "intersection" point
      unc_intersection_point = 0.5 * np.array([normal_addition_in_quadrature([unc_closest_point_on_second_line_to_first_line[i], unc_closest_point_on_first_line_to_second_line[i]]) for i in range(3)])
      return midpoint_between_closest_points_of_the_lines, unc_intersection_point
    
    
    # This is a limit that refuses to give an intersection point if the distance of closest approach is too large - even if consistent due to large closest point uncertainties.
    raise Exception("Lines are more skew than the set tolerance ({} mm) allows for.".format(tolerance)) 

  except Exception as e:
    print("Error: {}".format(e))


def extract_3d_physical_position(first_camera: AbstractCamera, occupied_pixel_on_first_camera: tuple[int, int], 
                                 second_camera: AbstractCamera, occupied_pixel_on_second_camera: tuple[int, int],
                                 unc_pixel_on_first_camera: tuple[int, int], unc_pixel_on_second_camera: tuple[int, int],
                                 scintillator_present=False):
    
    ([first_tan_phi, first_tan_theta], 
     [unc_first_tan_phi, unc_first_tan_theta], 
     [first_near_physical_position_in_box_coords, first_far_physical_position_in_box_coords], 
     [first_unc_near_physical_position_in_box_coords, first_unc_far_physical_position_in_box_coords],
    ) = first_camera.determine_in_plane_positions_and_angles_of_event(occupied_pixel_on_first_camera, unc_pixel_on_first_camera)
    
    ([second_tan_phi, second_tan_theta], 
     [unc_second_tan_phi, unc_second_tan_theta], 
     [second_near_physical_position_in_box_coords, second_far_physical_position_in_box_coords], 
     [second_unc_near_physical_position_in_box_coords, second_unc_far_physical_position_in_box_coords],
    ) = second_camera.determine_in_plane_positions_and_angles_of_event(occupied_pixel_on_second_camera, unc_pixel_on_second_camera)
    
    # General terminology so they can be overwritten if the scintillator logic needs calling
    first_camera_initial_position = first_far_physical_position_in_box_coords
    second_camera_initial_position = second_far_physical_position_in_box_coords
    unc_first_camera_intitial_position = first_unc_far_physical_position_in_box_coords
    unc_second_camera_intitial_position = second_unc_far_physical_position_in_box_coords
    
    if scintillator_present:
        first_camera_initial_position, unc_first_camera_intitial_position = first_camera.add_shift_to_front_position_due_to_refraction(first_near_physical_position_in_box_coords,
                                                                                                                                       first_unc_near_physical_position_in_box_coords,
                                                                                                                                       first_tan_phi, first_tan_theta, unc_first_tan_phi, unc_first_tan_theta)
        second_camera_initial_position, unc_second_camera_intitial_position = second_camera.add_shift_to_front_position_due_to_refraction(second_near_physical_position_in_box_coords,
                                                                                                                                          second_unc_near_physical_position_in_box_coords,
                                                                                                                                          second_tan_phi, second_tan_theta, unc_second_tan_phi, unc_second_tan_theta)
    
        first_phi, first_theta = np.arctan(first_tan_phi), np.arctan(first_tan_theta)
        second_phi, second_theta = np.arctan(second_tan_phi), np.arctan(second_tan_theta)
        first_refracted_phi, first_refracted_theta = calculate_refracted_angles([first_phi, first_theta])
        second_refracted_phi, second_refracted_theta = calculate_refracted_angles([second_phi, second_theta])
        
        # original variables simply renamed with the refracted ones.
        unc_first_tan_phi, unc_first_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(first_tan_phi, first_tan_theta, unc_first_tan_phi, unc_first_tan_theta)
        unc_second_tan_phi, unc_second_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(second_tan_phi, second_tan_theta, unc_second_tan_phi, unc_second_tan_theta)
        
        # original variables simply renamed with the refracted ones.
        first_tan_phi, first_tan_theta = np.tan(first_refracted_phi), np.tan(first_refracted_theta) 
        second_tan_phi, second_tan_theta = np.tan(second_refracted_phi), np.tan(second_refracted_theta)
        
    first_camera_line_vectors = first_camera.build_line_vectors(first_camera_initial_position, first_tan_phi, first_tan_theta)
    second_camera_line_vectors = second_camera.build_line_vectors(second_camera_initial_position, second_tan_phi, second_tan_theta)
    
    # Reversing directional vector if scintillator present, because initial position used in that case begins on the shifted_front_plane_position.
    # Shouldn't change things, but this is useful if we want to use the general_line_equation function.
    if scintillator_present:
        first_camera_line_vectors[1] *= -1
        second_camera_line_vectors[1] *= -1
    
    # unc_first_camera_directional_vector = first_camera.build_uncertainty_in_directional_vector(unc_first_tan_phi, unc_first_tan_theta)
    # unc_second_camera_directional_vector = second_camera.build_uncertainty_in_directional_vector(unc_second_tan_phi, unc_second_tan_theta)
    # NOW RETURNED FROM BUILD_LINE_VECTORS!
    
    distance_of_closest_approach = calculate_distance_of_closest_approach(first_camera_line_vectors, second_camera_line_vectors)
    print("Distance of closest approach is {}".format(distance_of_closest_approach))
    
    return calculate_intersection_point(first_camera_line_vectors, second_camera_line_vectors,
                                        unc_first_camera_intitial_position, unc_first_camera_directional_vector,
                                        unc_second_camera_intitial_position, unc_second_camera_directional_vector) 
    

# Beam vector line vectors should be a 2D np array, containing the initial position vector and the directional vector.
def extract_beam_center_position(camera: AbstractCamera, occupied_pixel_on_camera: tuple[int, int], unc_pixel_on_camera: tuple[int, int],
                                 beam_center_line_vectors, unc_beam_center_initial_position: np.ndarray[float],
                                 unc_beam_center_directional_vector: np.ndarray[float]):
    
    tan_phi, tan_theta, physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane = camera.determine_angles_of_event(occupied_pixel_on_camera)
    
    
    front_physical_position_homography_error, back_physical_position_homography_error = camera.calculate_uncertainty_on_homography(occupied_pixel_on_camera, unc_pixel_on_camera)
    
    print("front homo/shift error: {0}/{1}".format(front_physical_position_homography_error, camera.origin_shift_uncertainty))
    print("back homo/shift error: {0}/{1}".format(back_physical_position_homography_error, camera.origin_shift_uncertainty))
    
    # HACK: setting NaNS to 0.2 - the round about size of homography uncertainties, needs addressing properly.
    # front_physical_position_homography_error = np.nan_to_num(front_physical_position_homography_error, nan=0.2)
    # back_physical_position_homography_error = np.nan_to_num(back_physical_position_homography_error, nan=0.2)
    
    # NOTE: homography uncertainties would need converting to external coord system too!
    physical_position_on_front_plane_uncertainty = calculate_uncertainty_in_physical_position(front_physical_position_homography_error, camera.origin_shift_uncertainty)
    physical_position_on_back_plane_uncertainty = calculate_uncertainty_in_physical_position(back_physical_position_homography_error, camera.origin_shift_uncertainty)
    
    unc_tan_phi, unc_tan_theta = camera.calculate_uncertainty_in_tangent_of_angles(physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane,
                                                                                                    physical_position_on_front_plane_uncertainty, physical_position_on_back_plane_uncertainty,
                                                                                                    tan_phi, tan_theta)
    
    ####################### Modification to camera line because refraction is present ##################################################
    camera_initial_position, unc_camera_intitial_position = camera.add_shift_to_front_position_due_to_refraction(physical_position_on_front_calibration_plane, physical_position_on_front_plane_uncertainty,
                                                                                                                             tan_phi, tan_theta, unc_tan_phi, unc_tan_theta)
    phi, theta = np.arctan(tan_phi), np.arctan(tan_theta)

    # Refractive indices set as default arguments in the Snell's law functions below
    refracted_phi, refracted_theta = calculate_refracted_angles([phi, theta])
    # original variables simply renamed with the refracted ones.
    tan_phi, tan_theta = np.tan(refracted_phi), np.tan(refracted_theta) 
    # original variables simply renamed with the refracted ones.
    unc_tan_phi, unc_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(tan_phi, tan_theta, unc_tan_phi, unc_tan_theta)
    ############################ End of refraction corrections ##############################################################
    
    camera_line_vectors = camera.build_line_vectors(camera_initial_position, tan_phi, tan_theta) # Builds refracted line equation, starting at position on scintillator face (not calibration board)
    camera_line_vectors[1] *= -1 # Symbolic of the change in parameterisation of the refracted line (initial position parameterising line now on front plane, not back plane, so direction change)
    unc_camera_directional_vector = camera.build_uncertainty_in_directional_vector(unc_tan_phi, unc_tan_theta)
    
    distance_of_closest_approach = calculate_distance_of_closest_approach(camera_line_vectors, beam_center_line_vectors)
    print("Distance of closest approach between beamline and interpolated ray = {}".format(distance_of_closest_approach))

    return calculate_intersection_point(camera_line_vectors, beam_center_line_vectors,
                                        [unc_camera_intitial_position, unc_camera_directional_vector],
                                        [unc_beam_center_initial_position, unc_beam_center_directional_vector]) 
    

def extract_weighted_average_3d_physical_position(list_of_camera_objects, list_of_pixels_containing_point, 
                                         list_of_pixel_uncertainties, scintillator_present: bool=False):
    """
    Using the weighted average stuff from the Year 1 data analysis course, find the average 3d position
    using multiple camera perspective pairings.
    """
    
    possible_camera_combinations = list(itertools.combinations(list_of_camera_objects, 2))
    possible_pixel_combinations = list(itertools.combinations(list_of_pixels_containing_point, 2))
    possible_pixel_unc_combinations = list(itertools.combinations(list_of_pixel_uncertainties, 2))
    num_of_combinations = len(possible_camera_combinations)
    
    intersection_point_array = []
    unc_intersection_point_array = []
    
    for camera_combination, pixel_combination, unc_pixel_combination in zip(possible_camera_combinations, possible_pixel_combinations, possible_pixel_unc_combinations):
        
        camera_1, camera_2 = camera_combination
        pixel_coords_1, pixel_coords_2 = pixel_combination
        unc_pixel_coords_1, unc_pixel_coords_2 = unc_pixel_combination
        
        line_intersection_point, unc_line_intersection_point = extract_3d_physical_position(camera_1, pixel_coords_1, camera_2, pixel_coords_2,
                                                                                            unc_pixel_coords_1, unc_pixel_coords_2, scintillator_present=scintillator_present)
        intersection_point_array.append(line_intersection_point)
        unc_intersection_point_array.append(unc_line_intersection_point)
    
    if num_of_combinations == 1:
        return line_intersection_point, unc_line_intersection_point
    
    intersection_point_array = np.array(intersection_point_array)
    unc_intersection_point_array = np.array(unc_intersection_point_array)
    
    numerator_array = np.sum(intersection_point_array / unc_intersection_point_array**2, axis=0)
    denominator_array = np.sum(1 / unc_intersection_point_array**2, axis=0)
    
    weighted_mean_intersection_point = numerator_array / denominator_array
    unc_weighted_mean_intersection_point = np.sqrt(1 /denominator_array)
    
    return weighted_mean_intersection_point, unc_weighted_mean_intersection_point


def build_pixel_line_vectors_inside_scintillator(camera: AbstractCamera, occupied_pixel_on_camera: tuple[int, int], unc_pixel_on_camera: tuple[int, int]):
    
    tan_phi, tan_theta, physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane = camera.determine_angles_of_event(occupied_pixel_on_camera)
    front_physical_position_homography_error, back_physical_position_homography_error = camera.calculate_uncertainty_on_homography(occupied_pixel_on_camera, unc_pixel_on_camera)
    
    # HACK: setting NaNS to 0.2 - the round about size of homography uncertainties, needs addressing properly.
    front_physical_position_homography_error = np.nan_to_num(front_physical_position_homography_error, nan=0.2)
    back_physical_position_homography_error = np.nan_to_num(back_physical_position_homography_error, nan=0.2)
    
    # NOTE: homography uncertainties would need converting to external coord system too!
    physical_position_on_front_plane_uncertainty = calculate_uncertainty_in_physical_position(front_physical_position_homography_error, camera.origin_shift_uncertainty)
    physical_position_on_back_plane_uncertainty = calculate_uncertainty_in_physical_position(back_physical_position_homography_error, camera.origin_shift_uncertainty)
    
    unc_tan_phi, unc_tan_theta = camera.calculate_uncertainty_in_tangent_of_angles(physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane,
                                                                                                    physical_position_on_front_plane_uncertainty, physical_position_on_back_plane_uncertainty,
                                                                                                    tan_phi, tan_theta)
    
    ####################### Modification to camera line because refraction is present ##################################################
    camera_initial_position, unc_camera_intitial_position = camera.add_shift_to_front_position_due_to_refraction(physical_position_on_front_calibration_plane, physical_position_on_front_plane_uncertainty,
                                                                                                                             tan_phi, tan_theta, unc_tan_phi, unc_tan_theta)
    phi, theta = np.arctan(tan_phi), np.arctan(tan_theta)

    # Refractive indices set as default arguments in the Snell's law functions below
    refracted_phi, refracted_theta = calculate_refracted_angles([phi, theta])
    # original variables simply renamed with the refracted ones.
    tan_phi, tan_theta = np.tan(refracted_phi), np.tan(refracted_theta) 
    # original variables simply renamed with the refracted ones.
    unc_tan_phi, unc_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(tan_phi, tan_theta, unc_tan_phi, unc_tan_theta)
    ############################ End of refraction corrections ##############################################################
    
    camera_line_vectors = camera.build_line_vectors(camera_initial_position, tan_phi, tan_theta) # Builds refracted line equation, starting at position on scintillator face (not calibration board)
    camera_line_vectors[1] *= -1 # Symbolic of the change in parameterisation of the refracted line (initial position parameterising line now on front plane, not back plane, so direction change)
    unc_camera_directional_vector = camera.build_uncertainty_in_directional_vector(unc_tan_phi, unc_tan_theta)
    
    return camera_line_vectors, [unc_camera_intitial_position, unc_camera_directional_vector]


def main():
    
    try:
        top_cam = AbstractCamera.setup(TOP_CAM_ID, 1)
        side_cam = AbstractCamera.setup(SIDE_CAM_ID, 1)
        
        red_brick_corner_top_cam_pixel = (1837, 2204)
        unc_red_brick_corner_top_cam_pixel = (4,4)
        red_brick_corner_side_cam_pixel = (1752, 881)
        unc_red_brick_corner_side_cam_pixel = (6, 6)
        
        weighted_intersection_point, unc_weighted_intersection_point = extract_weighted_average_3d_physical_position([top_cam, side_cam], [red_brick_corner_top_cam_pixel,
                                                                                                                                  red_brick_corner_side_cam_pixel],
                                                                                                                                    [unc_red_brick_corner_top_cam_pixel,
                                                                                                                                    unc_red_brick_corner_side_cam_pixel],
                                                                                                                                    scintillator_present=False)
        
        print("Weighted Intersection Point of red brick corner is {0} +/- {1}".format(weighted_intersection_point, unc_weighted_intersection_point))
        return 0
    
    except Exception as e:
        print("Error in homography pinpointing algorithm: {}".format(e))
        return 1
    
if __name__ == "__main__":
    main()
