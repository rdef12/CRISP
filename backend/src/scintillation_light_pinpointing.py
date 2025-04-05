"""
To test this well, will need distortion correction applied to top HQ cam images when
producing homographies!

I also think the beam edge detection should be applied to undistorted images only
"""
from src.homography_pinpointing import AbstractCamera, extract_weighted_average_3d_physical_position, calculate_3d_euclidian_distance
from src.database.CRUD import CRISP_database_interaction as cdi
from src.uncertainty_functions import *
from itertools import product

def pinpoint_bragg_peak(camera_analysis_id_list):
    try:
        camera_id_list = []
        # TODO - could make new function which gets setup_id and camera_id from camera_analysis_id
        # TODO - add validation to check cam analyses from same beam run
        for camera_analysis_id in camera_analysis_id_list:
            camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(camera_analysis_id)
            camera_id_list.append(cdi.get_camera_and_settings_ids(camera_settings_link_id)["camera_id"])
        beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id)
        experiment_id = cdi.get_experiment_id_from_beam_run_id(beam_run_id)
        setup_id = cdi.get_setup_id_from_experiment_id(experiment_id)
        
        bragg_peak_pixel_list = [cdi.get_bragg_peak_pixel(camera_analysis_id) for camera_analysis_id in camera_analysis_id_list]
        bragg_peak_pixel_error_list = [cdi.get_unc_bragg_peak_pixel(camera_analysis_id) for camera_analysis_id in camera_analysis_id_list]
        
        cameras = [AbstractCamera.setup(camera_id, setup_id) for camera_id in camera_id_list]
        weighted_intersection_point, unc_weighted_intersection_point = (
            extract_weighted_average_3d_physical_position(cameras, bragg_peak_pixel_list, bragg_peak_pixel_error_list, scintillator_present=True))
        
        print(f"3D Bragg peak position: {weighted_intersection_point} +/- {unc_weighted_intersection_point}")
        return {"bragg_peak_position": weighted_intersection_point, "bragg_peak_position_error": unc_weighted_intersection_point}
        
    except Exception as e:
        print(f"Error when pinpointing bragg peak: {e}")


def build_directional_vector_of_beam_center(beam_run_id: int, side_camera_analysis_id: int, top_camera_analysis_id: int):
    """
    Physical Bragg position must be 3D
    
    The vector eqn should be understood as (3d_bragg_peak_position) + mu * (directional_vector)
    0 <= mu <= 1. With the directional vector pointing from the Bragg peak to the incident beam position.
    
    Using unc_theta rather than unc_tan_theta by appeal to the small angle approximation
    """
    side_camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(side_camera_analysis_id)
    top_camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(top_camera_analysis_id)
    side_camera_id = cdi.get_camera_and_settings_ids(side_camera_settings_link_id)["camera_id"]
    top_camera_id = cdi.get_camera_and_settings_ids(top_camera_settings_link_id)["camera_id"]
    beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(side_camera_id)
    experiment_id = cdi.get_experiment_id_from_beam_run_id(beam_run_id)
    setup_id = cdi.get_setup_id_from_experiment_id(experiment_id)
    side_camera_optical_axis = cdi.get_camera_optical_axis(side_camera_id, setup_id)
    top_camera_optical_axis = cdi.get_camera_optical_axis(top_camera_id, setup_id)
    if side_camera_optical_axis != "x":
        raise ValueError(f"Expected side camera optical axis to be 'x', but got '{side_camera_optical_axis}'")
    if top_camera_optical_axis != "y":
        raise ValueError(f"Expected top camera optical axis to be 'y', but got '{top_camera_optical_axis}'")
    
    
    physical_bragg_peak_position = cdi.get_bragg_peak_3d_position(beam_run_id)
    bragg_peak_error = cdi.get_unc_bragg_peak_3d_position(beam_run_id)
    top_cam_beam_angle, unc_top_cam_beam_angle = cdi.get_beam_angle(top_camera_analysis_id), cdi.get_unc_beam_angle(top_camera_analysis_id)
    side_cam_beam_angle, unc_side_cam_beam_angle = cdi.get_beam_angle(side_camera_analysis_id), cdi.get_unc_beam_angle(side_camera_analysis_id)
    
    x_b, y_b, z_b = physical_bragg_peak_position
    unc_x_b, unc_y_b, unc_z_b = bragg_peak_error
    
    theta_xz, theta_yz = np.deg2rad(top_cam_beam_angle), np.deg2rad(side_cam_beam_angle)
    unc_theta_xz, unc_theta_yz = np.deg2rad(unc_top_cam_beam_angle), np.deg2rad(unc_side_cam_beam_angle)
    
    beam_center_incident_position = np.array([x_b + z_b * np.tan(theta_xz),
                                                y_b - z_b * np.tan(theta_yz), 0])
    
    directional_vector_x = z_b * np.tan(theta_xz)
    directional_vector_y = -z_b * np.tan(theta_yz)
    directional_vector_z = -z_b
    
    x_component_fractional_quadrature = fractional_addition_in_quadrature([z_b, theta_xz], [unc_z_b, unc_theta_xz], z_b * theta_xz)
    y_component_fractional_quadrature = fractional_addition_in_quadrature([z_b, theta_yz], [unc_z_b, unc_theta_yz], z_b * theta_yz)
    unc_beam_directional_vector = np.array([x_component_fractional_quadrature, y_component_fractional_quadrature, unc_z_b])
    
    unc_beam_center_incident_position_x = normal_addition_in_quadrature([x_component_fractional_quadrature, unc_x_b])
    unc_beam_center_incident_position_y = normal_addition_in_quadrature([y_component_fractional_quadrature, unc_y_b])
    unc_beam_center_incident_position = np.array([unc_beam_center_incident_position_x, unc_beam_center_incident_position_y, 0])
    
    return beam_center_incident_position, unc_beam_center_incident_position, np.array([directional_vector_x, directional_vector_y, directional_vector_z]), unc_beam_directional_vector


def compute_bragg_peak_depth(beam_run_id: int, side_camera_analysis_id: int, top_camera_analysis_id: int):
    
    bragg_peak_3d_position = cdi.get_bragg_peak_3d_position(beam_run_id)
    unc_bragg_peak_3d_position = cdi.get_unc_bragg_peak_3d_position(beam_run_id)
    beam_center_incident_position, unc_beam_center_incident_position, _, _ = build_directional_vector_of_beam_center(beam_run_id, side_camera_analysis_id, top_camera_analysis_id)
    
    bragg_peak_distance_inside_scintillator = calculate_3d_euclidian_distance(bragg_peak_3d_position - beam_center_incident_position)
    unc_bragg_peak_distance_inside_scintillator = calculate_3d_euclidian_distance(np.array([
                                                                normal_addition_in_quadrature([unc_incident_position_component, bragg_peak_error_component])
                                                                for unc_incident_position_component, bragg_peak_error_component in zip(unc_beam_center_incident_position,
                                                                                                                                       unc_bragg_peak_3d_position)
                                                            ]))
    
    return bragg_peak_distance_inside_scintillator, unc_bragg_peak_distance_inside_scintillator


def compute_weighted_bragg_peak_depth(beam_run_id: int, side_camera_analysis_id_list: list[int], top_camera_analysis_id_list: list[int]):
    
    side_top_pairings = list(product(side_camera_analysis_id_list, top_camera_analysis_id_list))
    num_pairings = len(side_top_pairings)
    
    bragg_peak_depth_list = []
    unc_bragg_peak_depth_list = []
    for side_camera_analysis_id, top_camera_analysis_id in side_top_pairings:
        try:
            bragg_peak_depth, unc_bragg_peak_depth = compute_bragg_peak_depth(beam_run_id, side_camera_analysis_id, top_camera_analysis_id)
            bragg_peak_depth_list.append(bragg_peak_depth)
            unc_bragg_peak_depth_list.append(unc_bragg_peak_depth)
        except Exception as e:
            print(f"Error when computing bragg peak depth for side camera {side_camera_analysis_id} and top camera {top_camera_analysis_id}: {e}")
            
    if num_pairings == 1:
        return bragg_peak_depth, unc_bragg_peak_depth
    
    bragg_peak_depth_array = np.array(bragg_peak_depth_list)
    unc_bragg_peak_depth_array = np.array(unc_bragg_peak_depth_list)
    
    numerator_array = np.sum(bragg_peak_depth_array / unc_bragg_peak_depth_array**2, axis=0)
    denominator_array = np.sum(1 / unc_bragg_peak_depth_array**2, axis=0)
    
    weighted_mean_bragg_peak_depth = numerator_array / denominator_array
    unc_weighted_bragg_peak_depth = np.sqrt(1 /denominator_array)
    return weighted_mean_bragg_peak_depth, unc_weighted_bragg_peak_depth



