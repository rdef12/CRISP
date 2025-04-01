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
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

class BoxCoordinate(Enum):
    X = 0
    Y = 1
    Z = 2
    
@dataclass
class Scintillator:
    refractive_index: float
    refractive_index_unc: float = 0.0  # Default value if not provided

@dataclass
class AxesMapping:
    non_z_axis: Literal["x", "y"]
    optical_axis: Literal["x", "y"]
    depth_direction: Literal[-1, 1]  # Specifies which side of optical axis the camera is
    z_axis: str = "z"
    
    # Called automatically after AxesMapping object is created
    def __post_init__(self):
        # Check if the axes are unique
        axes = [self.non_z_axis, self.optical_axis]
        if len(set(axes)) != len(axes):
            raise ValueError("Axes values must be unique: no two axes can have the same direction.")


# Abstract base class
class AbstractCamera(ABC):
    # Factory for producing cameras
    @staticmethod
    def setup(camera_id, setup_id):
            camera_optical_axis = cdi.get_camera_optical_axis(camera_id, setup_id)
            match camera_optical_axis:
                case "y":
                    print("Creating top camera...")
                    return TopCamera(camera_id, setup_id)
                case "x":
                    print("Creating side camera...")
                    return SideCamera(camera_id, setup_id)
                case _:
                    raise ValueError("Unknown camera axis: {} \Valid types are {'x', 'y'}".format(camera_optical_axis))
            
    def __init__(self, camera_id, setup_id):
        """
        Lots of postgreSQL sessions to open, could it all be done in one session?
        """
        if type(self) is AbstractCamera:
            raise NotImplementedError("AbstractCamera class is abstract, use AbstractCamera.setup(camera_id, setup_id) to intialise a camera object.")
        
        self.scintillator = Scintillator(refractive_index=cdi.get_block_refractive_index(setup_id),
                                         refractive_index_unc=cdi.get_block_refractive_index_unc(setup_id))
        
        self.front_homography_matrix= cdi.get_near_face_homography_matrix(camera_id, setup_id)
        self.front_homography_covariance = cdi.get_near_face_homography_covariance_matrix(camera_id, setup_id)
        self.back_homography_matrix = cdi.get_far_face_homography_matrix(camera_id, setup_id)
        self.back_homography_covariance = cdi.get_far_face_homography_covariance_matrix(camera_id, setup_id)
        
        self.near_origin_shift = [cdi.get_near_face_z_shift(camera_id, setup_id),
                                  cdi.get_near_face_non_z_shift(camera_id, setup_id)
                                ]
        self.near_origin_shift_uncertainty = [cdi.get_near_face_z_shift_unc(camera_id, setup_id),
                                  cdi.get_near_face_non_z_shift_unc(camera_id, setup_id)
                                ]
        self.far_origin_shift = [cdi.get_far_face_z_shift(camera_id, setup_id),
                                  cdi.get_far_face_non_z_shift(camera_id, setup_id)
                                ]
        self.far_origin_shift_uncertainty = [cdi.get_far_face_z_shift_unc(camera_id, setup_id),
                                  cdi.get_far_face_non_z_shift_unc(camera_id, setup_id)
                                ]
        self.near_calibration_board_thickness = cdi.get_near_face_calibration_board_thickness(camera_id, setup_id)
        self.near_calibration_board_thickness_unc = cdi.get_near_face_calibration_board_thickness_unc(camera_id, setup_id)
        self.far_calibration_board_thickness = cdi.get_far_face_calibration_board_thickness(camera_id, setup_id)
        self.far_calibration_board_thickness_unc = cdi.get_far_face_calibration_board_thickness_unc(camera_id, setup_id)
        
    def map_image_coord_to_3d_point(self, physical_point_in_calibration_plane: float, depth: float) -> np.ndarray:
        """
        depth is inputted and depends on which plane the user is looking at (far or near)
        """
        # Create a dictionary to map the axes to corresponding values
        three_dimenisional_coords = {'x': None, 'y': None, 'z': None}
        
        # Map horizontal, vertical, and optical axes to their respective values
        three_dimenisional_coords[self.axes_mapping.z_axis] = physical_point_in_calibration_plane[0] # object point array constructed such that first component is the z-directed one
        three_dimenisional_coords[self.axes_mapping.non_z_axis] = physical_point_in_calibration_plane[1]
        three_dimenisional_coords[self.axes_mapping.optical_axis] = depth

        # Check if any axis is None
        if None in three_dimenisional_coords.values():
            raise ValueError("Mapping is incomplete, one or more axes are missing.")
    
        return np.array([three_dimenisional_coords['x'], three_dimenisional_coords['y'], three_dimenisional_coords['z']])
    
    
    def _calculate_two_dimensional_homography_errors(self, pixel_coords: tuple[float, float], unc_pixel_coords: tuple[float, float]):
        """
        Pixel coords given type float because we believe sub pixel uncertainty is feasible for the scintillation light analysis
        """
        print(f"Uncertainty in pixel coordinates: {unc_pixel_coords}")
        near_plane_two_dimensional_homography_error = generate_world_point_uncertainty([[pixel_coords]], unc_pixel_coords[0], unc_pixel_coords[1], self.front_homography_matrix, self.front_homography_covariance)
        print(f"Near plane 2D homography error: {near_plane_two_dimensional_homography_error}")
        far_plane_two_dimensional_position_homography_error = generate_world_point_uncertainty([[pixel_coords]], unc_pixel_coords[0], unc_pixel_coords[1], self.back_homography_matrix, self.back_homography_covariance)
        print(f"Far plane 2D homography error: {far_plane_two_dimensional_position_homography_error}")
        return near_plane_two_dimensional_homography_error, far_plane_two_dimensional_position_homography_error
    @staticmethod
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
        """

        uncertainty_in_horizontal_position_difference = normal_addition_in_quadrature([near_plane_position_unc[0],
                                                                                       far_plane_position_unc[0]])
        uncertainty_in_vertical_position_difference = normal_addition_in_quadrature([near_plane_position_unc[1],
                                                                                     far_plane_position_unc[1]])
        
        if self.axes_mapping.depth_direction == -1:
            denominator = self.seen_scintillator_depth
            unc_denominator = self.seen_scintillator_depth_uncertainty
        else:
            denominator = self.seen_scintillator_depth + self.near_calibration_board_thickness - self.far_calibration_board_thickness
            if self.far_calibration_board_thickness != self.near_calibration_board_thickness:
                unc_denominator = normal_addition_in_quadrature([self.seen_scintillator_depth_uncertainty,
                                                                self.near_calibration_board_thickness_unc,
                                                                self.far_calibration_board_thickness_unc])
            else:
                unc_denominator = self.seen_scintillator_depth_uncertainty # Board contributions cancel out if the same board is used on the top and bottom!
        
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
                depth = self.far_calibration_board_thickness # originally had said zero but with how the board is lined up, it does contribute!
                unc_depth = self.far_calibration_board_thickness_unc
            case ("far", -1):
                depth = self.seen_scintillator_depth # no calibration board shift
                unc_depth = self.seen_scintillator_depth_uncertainty
            case ("near", 1):
                depth = self.seen_scintillator_depth + self.near_calibration_board_thickness
                unc_depth = normal_addition_in_quadrature([self.seen_scintillator_depth_uncertainty, self.near_calibration_board_thickness_unc])
            case ("near", -1):
                depth = 0 # used to be negative calibration board thickness when I did not appreciate the wooden blocks restricting calibration board placement
                unc_depth = 0

        if plane_type == "far":
            # Below is the origin transformation! For this to work, the user-inputted origin shifts need to be signed correctly (although should always be positive)?
            print(f"\n\nphysical_position_on far calibration_plane: {physical_position_on_calibration_plane}",
                  f"\nfar_origin_shift: {self.far_origin_shift}")
            two_dimensional_position_relative_to_calibration_board_corner = np.array(physical_position_on_calibration_plane) + np.array(self.far_origin_shift) # mm units
            two_dimensional_position_relative_to_calibration_board_corner_unc = self._calculate_calibration_plane_physical_position_error(two_dimensional_homography_errors, self.far_origin_shift_uncertainty)
        else: # must be near
            print(f"\n\nphysical_position_on near calibration_plane: {physical_position_on_calibration_plane}",
                  f"\nnear_origin_shift: {self.near_origin_shift}")
            two_dimensional_position_relative_to_calibration_board_corner = np.array(physical_position_on_calibration_plane) + np.array(self.near_origin_shift) # mm units
            two_dimensional_position_relative_to_calibration_board_corner_unc = self._calculate_calibration_plane_physical_position_error(two_dimensional_homography_errors, self.near_origin_shift_uncertainty)
        
        physical_position_in_box_coords = self.map_image_coord_to_3d_point(two_dimensional_position_relative_to_calibration_board_corner, depth)
        physical_position_in_box_coords_uncertainty = self.map_image_coord_to_3d_point(two_dimensional_position_relative_to_calibration_board_corner_unc, unc_depth)
        
        return (physical_position_in_box_coords, 
                physical_position_in_box_coords_uncertainty, 
                two_dimensional_position_relative_to_calibration_board_corner, 
                two_dimensional_position_relative_to_calibration_board_corner_unc
        )
    
    
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
        
        # print(f"\n\nnear_plane_two_dimensional_homography_error: {near_plane_two_dimensional_homography_error}",
        #       f"far_plane_two_dimensional_position_homography_error: {far_plane_two_dimensional_position_homography_error}")
        
        near_physical_position_in_box_coords, unc_near_physical_position_in_box_coords, near_2d_position, near_2d_unc = self._transform_to_box_coords(physical_position_on_near_calibration_plane.copy(), 
                                                                                                                       near_plane_two_dimensional_homography_error, "near")
        far_physical_position_in_box_coords, unc_far_physical_position_in_box_coords, far_2d_position, far_2d_unc = self._transform_to_box_coords(physical_position_on_far_calibration_plane.copy(), 
                                                                                                                     far_plane_two_dimensional_position_homography_error, "far")
        
        # print(f"\n\near_physical_position_in_box_coords: {near_physical_position_in_box_coords}",
        #       f"unc_near_physical_position_in_box_coords: {unc_near_physical_position_in_box_coords}")
        # print(f"\n\near_2d_position: {near_2d_position}",
        #       f"near_2d_unc: {near_2d_unc}")
        
        # print(f"\n\nfar_physical_position_in_box_coords: {far_physical_position_in_box_coords}",
        #       f"unc_far_physical_position_in_box_coords: {unc_far_physical_position_in_box_coords}")
        # print(f"\n\nfar_2d_position: {far_2d_position}",
        #       f"far_2d_unc: {far_2d_unc}")
        
        
        physical_displacement_in_2d = far_2d_position - near_2d_position
        
        if self.axes_mapping.depth_direction == -1:
            tan_phi, tan_theta = physical_displacement_in_2d / self.seen_scintillator_depth
        elif self.axes_mapping.depth_direction == 1:
            tan_phi, tan_theta = physical_displacement_in_2d / (self.seen_scintillator_depth + self.near_calibration_board_thickness - self.far_calibration_board_thickness)
        else:
            raise ValueError("Somehow the depth direction has not been defined as either +/- 1")
        
        
        physical_displacement_in_plane_coords = far_physical_position_in_box_coords - near_physical_position_in_box_coords
        unc_tan_phi, unc_tan_theta = self._calculate_uncertainty_in_tangent_of_angles(physical_displacement_in_plane_coords, near_plane_two_dimensional_homography_error,
                                                                                     far_plane_two_dimensional_position_homography_error, tan_phi, tan_theta)

        return ([tan_phi, tan_theta], 
                [unc_tan_phi, unc_tan_theta], 
                [near_physical_position_in_box_coords, far_physical_position_in_box_coords], 
                [unc_near_physical_position_in_box_coords, unc_far_physical_position_in_box_coords]
            )
    
    @abstractmethod
    def build_direction_vector(self, tan_phi: float, tan_theta: float, unc_tan_phi: float, unc_tan_theta: float, scintillator_present: bool=False):
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
        self.seen_scintillator_depth = cdi.get_block_y_dimension(setup_id)
        self.seen_scintillator_depth_uncertainty = cdi.get_block_y_dimension_unc(setup_id)
        self.axes_mapping = AxesMapping(non_z_axis="x",
                                        optical_axis="y",
                                        depth_direction=cdi.get_camera_depth_direction(camera_id, setup_id))
    
    def build_direction_vector(self, tan_phi: float, tan_theta: float, unc_tan_phi: float, unc_tan_theta: float, scintillator_present: bool=False):
        directional_vector = np.array([tan_theta, -1, tan_phi])
        if scintillator_present:
            directional_vector *= -1
        direction_vector_uncertainty = np.array([unc_tan_theta, 0, unc_tan_phi])
        return directional_vector, direction_vector_uncertainty
    
        
    def add_shift_in_parameterising_position_due_to_refraction(self, physical_position_on_front_plane: float, physical_position_on_front_plane_uncertainty: float,
                                                                unrefracted_tan_phi: float, unrefracted_tan_theta: float,
                                                                unc_unrefracted_tan_phi: float, unc_unrefracted_tan_theta: float):
        
        shifted_box_coord_for_horizontal_image_coord = physical_position_on_front_plane[BoxCoordinate.Z.value] + (self.near_calibration_board_thickness * unrefracted_tan_phi)
        shifted_box_coord_for_vertical_image_coord = physical_position_on_front_plane[BoxCoordinate.X.value] + (self.near_calibration_board_thickness * unrefracted_tan_theta)
        
        unc_added_horizontal_term = fractional_addition_in_quadrature([self.near_calibration_board_thickness, unrefracted_tan_phi],
                                                                      [self.near_calibration_board_thickness_unc, unc_unrefracted_tan_phi], 
                                                                       self.near_calibration_board_thickness * unrefracted_tan_phi)
        unc_added_vertical_term = fractional_addition_in_quadrature([self.near_calibration_board_thickness, unrefracted_tan_theta],
                                                                      [self.near_calibration_board_thickness_unc, unc_unrefracted_tan_theta], 
                                                                       self.near_calibration_board_thickness * unrefracted_tan_theta)
        
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
        self.seen_scintillator_depth = cdi.get_block_x_dimension(setup_id)
        self.seen_scintillator_depth_uncertainty = cdi.get_block_x_dimension_unc(setup_id)
        self.axes_mapping = AxesMapping(non_z_axis="y",
                                        optical_axis="x",
                                        depth_direction=cdi.get_camera_depth_direction(camera_id, setup_id))
    
    def build_direction_vector(self, tan_phi: float, tan_theta: float, unc_tan_phi: float, unc_tan_theta: float, scintillator_present: bool=False):
        
        directional_vector = np.array([-1, tan_theta, tan_phi])
        if scintillator_present:
            directional_vector *= -1
        direction_vector_uncertainty = np.array([0, unc_tan_theta, unc_tan_phi])
        return directional_vector, direction_vector_uncertainty
    
    def add_shift_in_parameterising_position_due_to_refraction(self, physical_position_on_front_plane: float, physical_position_on_front_plane_uncertainty: float,
                                                                unrefracted_tan_phi: float, unrefracted_tan_theta: float,
                                                                unc_unrefracted_tan_phi: float, unc_unrefracted_tan_theta: float):
        
        shifted_box_coord_for_horizontal_image_coord = physical_position_on_front_plane[BoxCoordinate.Z.value] + (self.near_calibration_board_thickness * unrefracted_tan_phi)
        shifted_box_coord_for_vertical_image_coord = physical_position_on_front_plane[BoxCoordinate.Y.value] + (self.near_calibration_board_thickness * unrefracted_tan_theta)
        
        
        unc_added_horizontal_term = fractional_addition_in_quadrature([self.near_calibration_board_thickness, unrefracted_tan_phi],
                                                                      [self.near_calibration_board_thickness_unc, unc_unrefracted_tan_phi], 
                                                                       self.near_calibration_board_thickness * unrefracted_tan_phi)
        unc_added_vertical_term = fractional_addition_in_quadrature([self.near_calibration_board_thickness, unrefracted_tan_theta],
                                                                      [self.near_calibration_board_thickness_unc, unc_unrefracted_tan_theta], 
                                                                       self.near_calibration_board_thickness * unrefracted_tan_theta)
        
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
        # print(f"\n\n\nPIXEL COORDS: {pixel_coords}\n\n")
        opencv_pixel = convert_iterable_to_opencv_format(pixel_coords)
        # print(f"\n\n\OPENCV COORDS: {opencv_pixel}\n\n")
    associated_real_position = convert_image_position_to_real_position(pixel=opencv_pixel, homography_matrix_input=homography_matrix)[0, 0]
    # print(f"\n\nREAL POSITION: {associated_real_position}\n\n")
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
    

def calculate_uncertainty_on_tangent_of_refracted_angle_component(tan_angle: float, unc_tan_angle: float, n, unc_n: float):
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
                                                     n: float, unc_n):
        
        unc_tan_refracted_phi = calculate_uncertainty_on_tangent_of_refracted_angle_component(tan_phi, unc_tan_phi, n, unc_n)
        unc_tan_refracted_theta = calculate_uncertainty_on_tangent_of_refracted_angle_component(tan_theta, unc_tan_theta, n, unc_n)
        return unc_tan_refracted_phi, unc_tan_refracted_theta


def calculate_refracted_angles(incident_angles: np.ndarray[float], scintillator_refracative_index: float,
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
      print("\n\nTotal error added in quadrature between two closest points on interpolated lines is {}".format(total_closest_points_error))
      print("\n\nVector of closest approach (magnitude of components taken) is {}".format(np.abs(closest_point_on_second_line_to_first_line - closest_point_on_first_line_to_second_line)))
      
      if not np.all(np.abs(closest_point_on_second_line_to_first_line - closest_point_on_first_line_to_second_line) <= 5 * total_closest_points_error): # CURRENTLY, LESS THAN 5 COMBINED STD
         
        # 5 standard deviations because operating on a huge number of beam center coords across all image sets, it becomes quite possible that one component has an error exceeding 5 STD.
        raise Exception("\n\nThe seperation of two closest points is not consistent within 5 standard deviation of each of these points.")

      midpoint_between_closest_points_of_the_lines = (closest_point_on_second_line_to_first_line + closest_point_on_first_line_to_second_line ) / 2 # this is the "intersection" point
      unc_intersection_point = 0.5 * np.array([normal_addition_in_quadrature([unc_closest_point_on_second_line_to_first_line[i], unc_closest_point_on_first_line_to_second_line[i]]) for i in range(3)])
      return midpoint_between_closest_points_of_the_lines, unc_intersection_point
    
    
    # This is a limit that refuses to give an intersection point if the distance of closest approach is too large - even if consistent due to large closest point uncertainties.
    raise Exception("\n\nLines are more skew than the set tolerance ({} mm) allows for.".format(tolerance)) 

  except Exception as e:
    print("Error: {}".format(e))
    

def plot_3d_lines(line1, line2, num_points=100):
    """
    Plots two 3D lines using their initial positions and direction vectors, along with six planes,
    and saves the plot as an image.

    Parameters:
    - line1: List containing [initial_position, direction_vector] for the first line.
    - line2: List containing [initial_position, direction_vector] for the second line.
    - num_points: Number of points to generate along each line for plotting.
    - save_path: Filepath to save the plot image.
    """
    fig, axes = plt.subplots(1, 3, figsize=(12, 6), subplot_kw={'projection': '3d'})

    # ax.view_init(elev=10, azim=-80)  # Try different elevation and azimuth angles
    views = [(90, 0), (0, -90), (0,0)]  # Two different view angles

    # HARDCODED ID
    setup_id = 1
    x_block_dimension = cdi.get_block_x_dimension(setup_id)
    y_block_dimension = cdi.get_block_y_dimension(setup_id)
    z_block_dimension = cdi.get_block_z_dimension(setup_id)

    t1 = np.linspace(0, y_block_dimension, num_points)
    line1_points = np.array([general_vector_line_equation(t, line1[0], -line1[1]) for t in t1])
    t2 = np.linspace(0, x_block_dimension, num_points)
    line2_points = np.array([general_vector_line_equation(t, line2[0], -line2[1]) for t in t2])

    legend_handles = []
    for ax, view in zip(axes, views):
        ax.view_init(elev=view[0], azim=view[1])
        ax.set_box_aspect([1, 1, 1])
        
        ax.plot(line1_points[:, 0], line1_points[:, 1], line1_points[:, 2], label='Line 1', color='blue')
        ax.plot(line2_points[:, 0], line2_points[:, 1], line2_points[:, 2], label='Line 2', color='red')
        
        start1 = ax.scatter(*line1[0], color='blue', s=100, edgecolors='black')
        start2 = ax.scatter(*line2[0], color='red', s=100, edgecolors='black')
        end1 = ax.scatter(*line1_points[-1], color='purple', s=100, edgecolors='black')
        end2 = ax.scatter(*line2_points[-1], color='orange', s=100, edgecolors='black')
        
        line1_start_coords = f"Line 1 Start: ({line1[0][0]:.2f}, {line1[0][1]:.2f}, {line1[0][2]:.2f}) \n"
        line1_end_coords = f"Line 1 End: ({line1_points[-1][0]:.2f}, {line1_points[-1][1]:.2f}, {line1_points[-1][2]:.2f}) \n"
        line2_start_coords = f"Line 2 Start: ({line2[0][0]:.2f}, {line2[0][1]:.2f}, {line2[0][2]:.2f})"
        line2_end_coords = f"Line 2 End: ({line2_points[-1][0]:.2f}, {line2_points[-1][1]:.2f}, {line2_points[-1][2]:.2f})"
        
        if not legend_handles:
            legend_handles.extend([
                Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label=line1_start_coords),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label=line2_start_coords),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='purple', markersize=10, label=line1_end_coords),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label=line2_end_coords)
            ])
        
        x = np.linspace(0, x_block_dimension, num_points)
        y = np.linspace(0, y_block_dimension, num_points)
        z = np.linspace(0, z_block_dimension, num_points)
        X, Y = np.meshgrid(x, y)
        X, Z = np.meshgrid(x, z)
        Y, Z = np.meshgrid(y, z)

        ax.plot_surface(np.zeros_like(Y), Y, Z, alpha=0.3, color='purple')
        ax.plot_surface(np.full_like(Y, x_block_dimension), Y, Z, alpha=0.3, color='green')
        ax.plot_surface(X, np.zeros_like(X), Z, alpha=0.3, color='orange')
        ax.plot_surface(X, np.full_like(X, y_block_dimension), Z, alpha=0.3, color='yellow')
        ax.plot_surface(X, Y, np.zeros_like(X), alpha=0.3, color='pink')
        ax.plot_surface(X, Y, np.full_like(X, z_block_dimension), alpha=0.3, color='cyan')

        ax.quiver(0, 0, 0, 10, 0, 0, color='r')
        ax.quiver(0, 0, 0, 0, 10, 0, color='g')
        ax.quiver(0, 0, 0, 0, 0, 10, color='b')

        ax.set_xlim([50, 0])
        ax.set_ylim([0, y_block_dimension])
        ax.set_zlim([0, z_block_dimension])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

    fig.legend(handles=legend_handles, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 0.95), frameon=True)
    plt.tight_layout()
    plt.subplots_adjust(top=0.8)  # Adjust spacing to fit the legend
    # Save the plot
    plt.savefig("/code/src/plots/3d_lines_plot.png", dpi=600)
    plt.close(fig)


def extract_3d_physical_position(first_camera: AbstractCamera, occupied_pixel_on_first_camera: tuple[int, int], 
                                 second_camera: AbstractCamera, occupied_pixel_on_second_camera: tuple[int, int],
                                 unc_pixel_on_first_camera: tuple[int, int], unc_pixel_on_second_camera: tuple[int, int],
                                 scintillator_present=False):
    
    ([first_tan_phi, first_tan_theta], 
     [unc_first_tan_phi, unc_first_tan_theta], 
     [first_near_physical_position_in_box_coords, first_far_physical_position_in_box_coords], 
     [first_unc_near_physical_position_in_box_coords, first_unc_far_physical_position_in_box_coords],
    ) = first_camera.determine_in_plane_positions_and_angles_of_event(occupied_pixel_on_first_camera, unc_pixel_on_first_camera)
    
    # print("\n\nFirst camera angles (tan_phi, tan_theta):", first_tan_phi, first_tan_theta)
    # print("\n\nFirst camera near position:", first_near_physical_position_in_box_coords)
    # print("\n\nFirst camera far position:", first_far_physical_position_in_box_coords)
    
    ([second_tan_phi, second_tan_theta], 
     [unc_second_tan_phi, unc_second_tan_theta], 
     [second_near_physical_position_in_box_coords, second_far_physical_position_in_box_coords], 
     [second_unc_near_physical_position_in_box_coords, second_unc_far_physical_position_in_box_coords],
    ) = second_camera.determine_in_plane_positions_and_angles_of_event(occupied_pixel_on_second_camera, unc_pixel_on_second_camera)
    
    # print("\n\nSecond camera angles (tan_phi, tan_theta):", second_tan_phi, second_tan_theta)
    # print("\n\nSecond camera near position:", second_near_physical_position_in_box_coords)
    # print("\n\nSecond camera far position:", second_far_physical_position_in_box_coords)
    
    # General terminology so they can be overwritten if the scintillator logic needs calling
    first_camera_initial_position = first_far_physical_position_in_box_coords
    second_camera_initial_position = second_far_physical_position_in_box_coords
    unc_first_camera_initial_position = first_unc_far_physical_position_in_box_coords
    unc_second_camera_initial_position = second_unc_far_physical_position_in_box_coords
    
    if scintillator_present:
        first_camera_initial_position, unc_first_camera_initial_position = first_camera.add_shift_in_parameterising_position_due_to_refraction(first_near_physical_position_in_box_coords,
                                                                                                                                       first_unc_near_physical_position_in_box_coords,
                                                                                                                                       first_tan_phi, first_tan_theta, unc_first_tan_phi, unc_first_tan_theta)
        second_camera_initial_position, unc_second_camera_initial_position = second_camera.add_shift_in_parameterising_position_due_to_refraction(second_near_physical_position_in_box_coords,
                                                                                                                                          second_unc_near_physical_position_in_box_coords,
                                                                                                                                          second_tan_phi, second_tan_theta, unc_second_tan_phi, unc_second_tan_theta)
    
        first_phi, first_theta = np.arctan(first_tan_phi), np.arctan(first_tan_theta)
        second_phi, second_theta = np.arctan(second_tan_phi), np.arctan(second_tan_theta)
        first_refracted_phi, first_refracted_theta = calculate_refracted_angles([first_phi, first_theta], first_camera.scintillator.refractive_index)
        second_refracted_phi, second_refracted_theta = calculate_refracted_angles([second_phi, second_theta], second_camera.scintillator.refractive_index)
        
        # original variables simply renamed with the refracted ones.
        unc_first_tan_phi, unc_first_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(first_tan_phi, first_tan_theta, unc_first_tan_phi, unc_first_tan_theta, first_camera.scintillator.refractive_index, first_camera.scintillator.refractive_index_unc)
        unc_second_tan_phi, unc_second_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(second_tan_phi, second_tan_theta, unc_second_tan_phi, unc_second_tan_theta, second_camera.scintillator.refractive_index, second_camera.scintillator.refractive_index_unc)
        
        # original variables simply renamed with the refracted ones.
        first_tan_phi, first_tan_theta = np.tan(first_refracted_phi), np.tan(first_refracted_theta) 
        second_tan_phi, second_tan_theta = np.tan(second_refracted_phi), np.tan(second_refracted_theta)
        
    first_camera_direction_vector, unc_first_camera_directional_vector = first_camera.build_direction_vector(first_tan_phi, first_tan_theta, unc_first_tan_phi, unc_first_tan_theta, scintillator_present=scintillator_present)
    second_camera_direction_vector, unc_second_camera_directional_vector = second_camera.build_direction_vector(second_tan_phi, second_tan_theta, unc_second_tan_phi, unc_second_tan_theta, scintillator_present=scintillator_present)
    
    first_camera_line_vectors = [first_camera_initial_position, first_camera_direction_vector]
    second_camera_line_vectors = [second_camera_initial_position, second_camera_direction_vector]
    
    print("\n\nFirst camera line vectors:", first_camera_line_vectors)
    print("\n\nSecond camera line vectors:", second_camera_line_vectors)

    # Call the function to plot the lines
    plot_3d_lines(first_camera_line_vectors, second_camera_line_vectors)
    
    distance_of_closest_approach = calculate_distance_of_closest_approach(first_camera_line_vectors, second_camera_line_vectors)
    print("\n\nDistance of closest approach is {}".format(distance_of_closest_approach))
    
    return calculate_intersection_point(first_camera_line_vectors, second_camera_line_vectors,
                                        [unc_first_camera_initial_position, unc_first_camera_directional_vector],
                                        [unc_second_camera_initial_position, unc_second_camera_directional_vector])
    

# # Beam vector line vectors should be a 2D np array, containing the initial position vector and the directional vector.
# def extract_beam_center_position(camera: AbstractCamera, occupied_pixel_on_camera: tuple[int, int], unc_pixel_on_camera: tuple[int, int],
#                                  beam_center_line_vectors, unc_beam_center_initial_position: np.ndarray[float],
#                                  unc_beam_center_directional_vector: np.ndarray[float]):
    
#     tan_phi, tan_theta, physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane = camera.determine_angles_of_event(occupied_pixel_on_camera)
    
    
#     front_physical_position_homography_error, back_physical_position_homography_error = camera.calculate_uncertainty_on_homography(occupied_pixel_on_camera, unc_pixel_on_camera)
    
#     print("front homo/shift error: {0}/{1}".format(front_physical_position_homography_error, camera.origin_shift_uncertainty))
#     print("back homo/shift error: {0}/{1}".format(back_physical_position_homography_error, camera.origin_shift_uncertainty))
    
#     # HACK: setting NaNS to 0.2 - the round about size of homography uncertainties, needs addressing properly.
#     # front_physical_position_homography_error = np.nan_to_num(front_physical_position_homography_error, nan=0.2)
#     # back_physical_position_homography_error = np.nan_to_num(back_physical_position_homography_error, nan=0.2)
    
#     # NOTE: homography uncertainties would need converting to external coord system too!
#     physical_position_on_front_plane_uncertainty = calculate_uncertainty_in_physical_position(front_physical_position_homography_error, camera.origin_shift_uncertainty)
#     physical_position_on_back_plane_uncertainty = calculate_uncertainty_in_physical_position(back_physical_position_homography_error, camera.origin_shift_uncertainty)
    
#     unc_tan_phi, unc_tan_theta = camera.calculate_uncertainty_in_tangent_of_angles(physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane,
#                                                                                                     physical_position_on_front_plane_uncertainty, physical_position_on_back_plane_uncertainty,
#                                                                                                     tan_phi, tan_theta)
    
#     ####################### Modification to camera line because refraction is present ##################################################
#     camera_initial_position, unc_camera_intitial_position = camera.add_shift_to_front_position_due_to_refraction(physical_position_on_front_calibration_plane, physical_position_on_front_plane_uncertainty,
#                                                                                                                              tan_phi, tan_theta, unc_tan_phi, unc_tan_theta)
#     phi, theta = np.arctan(tan_phi), np.arctan(tan_theta)

#     # Refractive indices set as default arguments in the Snell's law functions below
#     refracted_phi, refracted_theta = calculate_refracted_angles([phi, theta], camera.scintillator.refractive_index)
#     # original variables simply renamed with the refracted ones.
#     tan_phi, tan_theta = np.tan(refracted_phi), np.tan(refracted_theta) 
#     # original variables simply renamed with the refracted ones.
#     unc_tan_phi, unc_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(tan_phi, tan_theta, unc_tan_phi, unc_tan_theta, camera.scintillator.refractive_index, camera.scintillator.refractive_index_unc)
#     ############################ End of refraction corrections ##############################################################
    
#     camera_line_vectors = camera.build_line_vectors(camera_initial_position, tan_phi, tan_theta) # Builds refracted line equation, starting at position on scintillator face (not calibration board)
#     camera_line_vectors[1] *= -1 # Symbolic of the change in parameterisation of the refracted line (initial position parameterising line now on front plane, not back plane, so direction change)
#     unc_camera_directional_vector = camera.build_uncertainty_in_directional_vector(unc_tan_phi, unc_tan_theta)
    
#     distance_of_closest_approach = calculate_distance_of_closest_approach(camera_line_vectors, beam_center_line_vectors)
#     print("Distance of closest approach between beamline and interpolated ray = {}".format(distance_of_closest_approach))

#     return calculate_intersection_point(camera_line_vectors, beam_center_line_vectors,
#                                         [unc_camera_intitial_position, unc_camera_directional_vector],
#                                         [unc_beam_center_initial_position, unc_beam_center_directional_vector]) 
    

# def extract_weighted_average_3d_physical_position(list_of_camera_objects, list_of_pixels_containing_point, 
#                                          list_of_pixel_uncertainties, scintillator_present: bool=False):
#     """
#     Using the weighted average stuff from the Year 1 data analysis course, find the average 3d position
#     using multiple camera perspective pairings.
#     """
    
#     possible_camera_combinations = list(itertools.combinations(list_of_camera_objects, 2))
#     possible_pixel_combinations = list(itertools.combinations(list_of_pixels_containing_point, 2))
#     possible_pixel_unc_combinations = list(itertools.combinations(list_of_pixel_uncertainties, 2))
#     num_of_combinations = len(possible_camera_combinations)
    
#     intersection_point_array = []
#     unc_intersection_point_array = []
    
#     for camera_combination, pixel_combination, unc_pixel_combination in zip(possible_camera_combinations, possible_pixel_combinations, possible_pixel_unc_combinations):
        
#         camera_1, camera_2 = camera_combination
#         pixel_coords_1, pixel_coords_2 = pixel_combination
#         unc_pixel_coords_1, unc_pixel_coords_2 = unc_pixel_combination
        
#         line_intersection_point, unc_line_intersection_point = extract_3d_physical_position(camera_1, pixel_coords_1, camera_2, pixel_coords_2,
#                                                                                             unc_pixel_coords_1, unc_pixel_coords_2, scintillator_present=scintillator_present)
#         intersection_point_array.append(line_intersection_point)
#         unc_intersection_point_array.append(unc_line_intersection_point)
    
#     if num_of_combinations == 1:
#         return line_intersection_point, unc_line_intersection_point
    
#     intersection_point_array = np.array(intersection_point_array)
#     unc_intersection_point_array = np.array(unc_intersection_point_array)
    
#     numerator_array = np.sum(intersection_point_array / unc_intersection_point_array**2, axis=0)
#     denominator_array = np.sum(1 / unc_intersection_point_array**2, axis=0)
    
#     weighted_mean_intersection_point = numerator_array / denominator_array
#     unc_weighted_mean_intersection_point = np.sqrt(1 /denominator_array)
    
#     return weighted_mean_intersection_point, unc_weighted_mean_intersection_point


# def build_pixel_line_vectors_inside_scintillator(camera: AbstractCamera, occupied_pixel_on_camera: tuple[int, int], unc_pixel_on_camera: tuple[int, int]):
    
#     tan_phi, tan_theta, physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane = camera.determine_angles_of_event(occupied_pixel_on_camera)
#     front_physical_position_homography_error, back_physical_position_homography_error = camera.calculate_uncertainty_on_homography(occupied_pixel_on_camera, unc_pixel_on_camera)
    
#     # HACK: setting NaNS to 0.2 - the round about size of homography uncertainties, needs addressing properly.
#     front_physical_position_homography_error = np.nan_to_num(front_physical_position_homography_error, nan=0.2)
#     back_physical_position_homography_error = np.nan_to_num(back_physical_position_homography_error, nan=0.2)
    
#     # NOTE: homography uncertainties would need converting to external coord system too!
#     physical_position_on_front_plane_uncertainty = calculate_uncertainty_in_physical_position(front_physical_position_homography_error, camera.origin_shift_uncertainty)
#     physical_position_on_back_plane_uncertainty = calculate_uncertainty_in_physical_position(back_physical_position_homography_error, camera.origin_shift_uncertainty)
    
#     unc_tan_phi, unc_tan_theta = camera.calculate_uncertainty_in_tangent_of_angles(physical_position_on_front_calibration_plane, physical_position_on_back_calibration_plane,
#                                                                                                     physical_position_on_front_plane_uncertainty, physical_position_on_back_plane_uncertainty,
#                                                                                                     tan_phi, tan_theta)
    
#     ####################### Modification to camera line because refraction is present ##################################################
#     camera_initial_position, unc_camera_intitial_position = camera.add_shift_to_front_position_due_to_refraction(physical_position_on_front_calibration_plane, physical_position_on_front_plane_uncertainty,
#                                                                                                                              tan_phi, tan_theta, unc_tan_phi, unc_tan_theta)
#     phi, theta = np.arctan(tan_phi), np.arctan(tan_theta)

#     # Refractive indices set as default arguments in the Snell's law functions below
#     refracted_phi, refracted_theta = calculate_refracted_angles([phi, theta], camera.scintillator.refractive_index)
#     # original variables simply renamed with the refracted ones.
#     tan_phi, tan_theta = np.tan(refracted_phi), np.tan(refracted_theta) 
#     # original variables simply renamed with the refracted ones.
#     unc_tan_phi, unc_tan_theta = build_uncertainty_in_tangent_of_refracted_angles(tan_phi, tan_theta, unc_tan_phi, unc_tan_theta, camera.scintillator.refractive_index, camera.scintillator.refractive_index_unc))
#     ############################ End of refraction corrections ##############################################################
    
#     camera_line_vectors = camera.build_line_vectors(camera_initial_position, tan_phi, tan_theta) # Builds refracted line equation, starting at position on scintillator face (not calibration board)
#     camera_line_vectors[1] *= -1 # Symbolic of the change in parameterisation of the refracted line (initial position parameterising line now on front plane, not back plane, so direction change)
#     unc_camera_directional_vector = camera.build_uncertainty_in_directional_vector(unc_tan_phi, unc_tan_theta)
    
#     return camera_line_vectors, [unc_camera_intitial_position, unc_camera_directional_vector]


def perform_homography_pinpointing_between_camera_pair_for_GUI(setup_id, first_camera_id, second_camera_id):
    try:
        top_cam = AbstractCamera.setup(first_camera_id, setup_id)
        
        # print("\n\nTOP CAMERA", vars(top_cam), "\n\n")
        # print(f"top camera dd = {top_cam.axes_mapping.depth_direction}")
        
        # origin_position = get_projected_position_of_pixel(top_cam.back_homography_matrix,
        #                                                   pixel_coords=(1088, 2685))
        # print(f"\n\n\nORIGIN POSITION {origin_position}\n\n\n")
        
        side_cam = AbstractCamera.setup(second_camera_id, setup_id)
        
        # print("\n\nSIDE CAMERA", vars(side_cam), "\n\n")
        # print(f"side camera dd = {side_cam.axes_mapping.depth_direction}")
        
        # test_point = [1, 2]
        # print(f"\n\nTOP CAM TEST PIXEL {top_cam.map_image_coord_to_3d_point(test_point, 3)}\n\n")
        # print(f"\n\nSIDE CAM TEST PIXEL {side_cam.map_image_coord_to_3d_point(test_point, 3)}\n\n")
        
        # print(print(f"SIDE FRONT HOMOGRAPHY: {side_cam.front_homography_matrix}"))
        
        red_brick_corner_top_cam_pixel = (1837, 2204)
        unc_red_brick_corner_top_cam_pixel = (4,4)
        red_brick_corner_side_cam_pixel = (1752, 881)
        unc_red_brick_corner_side_cam_pixel = (6, 6)
        
        # TOP_CAM_NEAR_FACE_TEST_PIXEL = (890, 2877)
        # TOP_CAM_FAR_FACE_TEST_PIXEL = (2094, 2310)
        
        intersection_point, unc_intersection_point = extract_3d_physical_position(top_cam, red_brick_corner_top_cam_pixel, side_cam, red_brick_corner_side_cam_pixel,
                                                                                                    unc_red_brick_corner_top_cam_pixel, unc_red_brick_corner_side_cam_pixel,
                                                                                                    scintillator_present=False)
        # intersection_point, unc_intersection_point = extract_3d_physical_position(top_cam, TOP_CAM_FAR_FACE_TEST_PIXEL, side_cam, red_brick_corner_side_cam_pixel,
        #                                                                                     unc_red_brick_corner_top_cam_pixel, unc_red_brick_corner_side_cam_pixel,
        #                                                                                     scintillator_present=False)
        
        print("\n\nIntersection Point of red brick corner is {0} +/- {1}".format(intersection_point, unc_intersection_point))
        return 0
    
    except Exception as e:
        print("Error in homography pinpointing algorithm: {}".format(e))
        return 1
