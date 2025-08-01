"""
To test this well, will need distortion correction applied to top HQ cam images when
producing homographies!

I also think the beam edge detection should be applied to undistorted images only
"""
from src.homography_pinpointing import AbstractCamera, extract_weighted_average_3d_physical_position, calculate_3d_euclidian_distance, extract_beam_center_position
from src.database.CRUD import CRISP_database_interaction as cdi
from src.uncertainty_functions import *
from itertools import product
import matplotlib.pyplot as plt
import cv2 as cv

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
        weighted_bragg_peak_position, unc_weighted_bragg_peak_position = (
            extract_weighted_average_3d_physical_position(cameras, bragg_peak_pixel_list, bragg_peak_pixel_error_list, scintillator_present=True))
        
        print(f"3D Bragg peak position: {weighted_bragg_peak_position} +/- {unc_weighted_bragg_peak_position}")
        cdi.update_bragg_peak_3d_position(beam_run_id, [float(x) for x in weighted_bragg_peak_position.flatten()])
        cdi.update_unc_bragg_peak_3d_position(beam_run_id, [float(x) for x in unc_weighted_bragg_peak_position.flatten()])
        return {"message": "Successfully pinpointed bragg peak"}
        
    except Exception as e:
        print(f"Error when pinpointing bragg peak: {e}")


def calculate_beam_incidence_and_directional_vector(
    physical_bragg_peak_position, bragg_peak_error, top_cam_beam_angle, unc_top_cam_beam_angle,
    side_cam_beam_angle, unc_side_cam_beam_angle):

    x_b, y_b, z_b = physical_bragg_peak_position
    unc_x_b, unc_y_b, unc_z_b = bragg_peak_error
    
    # # HACK - to account for scintillator edge angle (i.e. "angle due to camera rotation")
    # side_cam_beam_angle = side_cam_beam_angle - (-0.71) # degrees - hardcoded from scintillator edge angle in raspi4b3 images (varies between cameras)

    theta_xz, theta_yz = np.deg2rad(top_cam_beam_angle), np.deg2rad(side_cam_beam_angle)
    unc_theta_xz, unc_theta_yz = np.deg2rad(unc_top_cam_beam_angle), np.deg2rad(unc_side_cam_beam_angle)

    # Calculate beam center incident position
    beam_center_incident_position = np.array([
        x_b + z_b * np.tan(theta_xz),
        y_b - z_b * np.tan(theta_yz),
        0
    ])

    # Calculate directional vector
    directional_vector_x = z_b * np.tan(theta_xz)
    directional_vector_y = -z_b * np.tan(theta_yz)
    directional_vector_z = -z_b
    beam_direction_vector = np.array([directional_vector_x, directional_vector_y, directional_vector_z])

    # Calculate uncertainties
    x_component_fractional_quadrature = fractional_addition_in_quadrature(
        [z_b, theta_xz], [unc_z_b, unc_theta_xz], z_b * theta_xz
    )
    y_component_fractional_quadrature = fractional_addition_in_quadrature(
        [z_b, theta_yz], [unc_z_b, unc_theta_yz], z_b * theta_yz
    )
    unc_beam_directional_vector = np.array([
        x_component_fractional_quadrature,
        y_component_fractional_quadrature,
        unc_z_b
    ])

    unc_beam_center_incident_position_x = normal_addition_in_quadrature([x_component_fractional_quadrature, unc_x_b])
    unc_beam_center_incident_position_y = normal_addition_in_quadrature([y_component_fractional_quadrature, unc_y_b])
    unc_beam_center_incident_position = np.array([
        unc_beam_center_incident_position_x,
        unc_beam_center_incident_position_y,
        0
    ])
    
    # ############# HACK - ADDED TO CHECK IMPACT OF NORMAL INCIDENCE ASSUMPTION ON DEPTH COMPUTED (AND PINPOINTING FAILURE IN RANGE ANALYSIS) #########
    # beam_center_incident_position = np.array([
    #     beam_center_incident_position[0],
    #     beam_center_incident_position[1],
    #     0
    # ])
    # unc_beam_center_incident_position = np.array([
    #     unc_beam_center_incident_position_x,
    #     unc_beam_center_incident_position_y,
    #     0
    # ])
    # beam_direction_vector = np.array([0,0,1])  
    # unc_beam_directional_vector = np.array([0,0,0])
    # ################################################################################################################################

    return beam_center_incident_position, unc_beam_center_incident_position, beam_direction_vector, unc_beam_directional_vector


def build_directional_vector_of_beam_center_for_beam_run(beam_run_id: int, side_cam_beam_angle, unc_side_cam_beam_angle,
                                                         top_cam_beam_angle, unc_top_cam_beam_angle):
    """
    Physical Bragg position must be 3D.
    """
    physical_bragg_peak_position = cdi.get_bragg_peak_3d_position(beam_run_id)
    bragg_peak_error = cdi.get_unc_bragg_peak_3d_position(beam_run_id)

    return calculate_beam_incidence_and_directional_vector(
        physical_bragg_peak_position, bragg_peak_error, top_cam_beam_angle, unc_top_cam_beam_angle,
        side_cam_beam_angle, unc_side_cam_beam_angle
    )


def build_directional_vector_of_beam_center_for_camera_pair(side_camera_analysis_id: int, top_camera_analysis_id: int):
    """
    Physical Bragg position must be 3D.
    """
    side_camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(side_camera_analysis_id)
    top_camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(top_camera_analysis_id)
    side_camera_id = cdi.get_camera_and_settings_ids(side_camera_settings_link_id)["camera_id"]
    top_camera_id = cdi.get_camera_and_settings_ids(top_camera_settings_link_id)["camera_id"]
    beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(side_camera_settings_link_id)
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

    return calculate_beam_incidence_and_directional_vector(
        physical_bragg_peak_position, bragg_peak_error, top_cam_beam_angle, unc_top_cam_beam_angle,
        side_cam_beam_angle, unc_side_cam_beam_angle
    )
    
def compute_weighted_mean_of_array(array: np.ndarray, unc_array: np.ndarray):
    numerator_array = np.sum(array / unc_array**2, axis=0)
    denominator_array = np.sum(1 / unc_array**2, axis=0)
    weighted_mean = numerator_array / denominator_array
    unc_weighted_mean = np.sqrt(1 /denominator_array)
    return weighted_mean, unc_weighted_mean

def build_weighted_directional_vector_of_beam_center(side_camera_analysis_id_list: list[int], top_camera_analysis_id_list: list[int]):
    
    camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(side_camera_analysis_id_list[0])
    beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id)
    
    side_top_pairings = list(product(side_camera_analysis_id_list, top_camera_analysis_id_list))
    num_pairings = len(side_top_pairings)
    
    top_cam_beam_angle_array = np.zeros(num_pairings)
    side_cam_beam_angle_array = np.zeros(num_pairings)
    unc_top_cam_beam_angle_array = np.zeros(num_pairings)
    unc_side_cam_beam_angle_array = np.zeros(num_pairings)
    
    for i, (side_camera_analysis_id, top_camera_analysis_id) in enumerate(side_top_pairings):
        try:
            top_cam_beam_angle_array[i] = cdi.get_beam_angle(top_camera_analysis_id)
            unc_top_cam_beam_angle_array[i] = cdi.get_unc_beam_angle(top_camera_analysis_id)
            side_cam_beam_angle_array[i] = cdi.get_beam_angle(side_camera_analysis_id)
            unc_side_cam_beam_angle_array[i] = cdi.get_unc_beam_angle(side_camera_analysis_id)
        except Exception as e:
            print(f"Error when retrieving beam angles for side camera {side_camera_analysis_id} and top camera {top_camera_analysis_id}: {e}")
    
    # if num_pairings == 1:
    #     beam_center_incident_position, unc_beam_center_incident_position, \
    #     beam_direction_vector, unc_beam_directional_vector = build_directional_vector_of_beam_center_for_beam_run(beam_run_id, weighted_side_cam_beam_angle, unc_weighted_side_cam_beam_angle,
    #                                                                                                               weighted_top_cam_beam_angle, unc_weighted_top_cam_beam_angle)
    # else:
    weighted_side_cam_beam_angle, unc_weighted_side_cam_beam_angle = compute_weighted_mean_of_array(side_cam_beam_angle_array, unc_side_cam_beam_angle_array)
    weighted_top_cam_beam_angle, unc_weighted_top_cam_beam_angle = compute_weighted_mean_of_array(top_cam_beam_angle_array, unc_top_cam_beam_angle_array)
    
    # Beam vector constructed using weighted angles seen by side and top cameras
    beam_center_incident_position, unc_beam_center_incident_position, \
        beam_direction_vector, unc_beam_directional_vector = build_directional_vector_of_beam_center_for_beam_run(beam_run_id, weighted_side_cam_beam_angle, unc_weighted_side_cam_beam_angle,
                                                                                                                    weighted_top_cam_beam_angle, unc_weighted_top_cam_beam_angle)
    
    cdi.update_beam_incident_3d_position(beam_run_id, [float(x) for x in beam_center_incident_position.flatten()])
    cdi.update_unc_beam_incident_3d_position(beam_run_id, [float(x) for x in unc_beam_center_incident_position.flatten()])
    cdi.update_beam_path_vector(beam_run_id, [float(x) for x in beam_direction_vector.flatten()])
    cdi.update_unc_beam_path_vector(beam_run_id, [float(x) for x in unc_beam_directional_vector.flatten()])
    return None
    

def compute_bragg_peak_depth(beam_run_id: int, side_camera_analysis_id: int, top_camera_analysis_id: int):
    
    bragg_peak_3d_position = cdi.get_bragg_peak_3d_position(beam_run_id)
    unc_bragg_peak_3d_position = cdi.get_unc_bragg_peak_3d_position(beam_run_id)
    beam_center_incident_position, unc_beam_center_incident_position, _, _ = build_directional_vector_of_beam_center_for_camera_pair(side_camera_analysis_id, top_camera_analysis_id)
    
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

def overlay_failed_pinpoints_on_image(camera_analysis_id, failed_beam_center_coords):
    """
    Only create if failed_pinpoints > 0
    """
    image = cdi.get_average_image(camera_analysis_id).astype(np.uint8)
    image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    for coord in failed_beam_center_coords:
        print(coord)
        coord = tuple(map(int, coord))
        image = cv.circle(image, coord, 3, (128, 0, 128), -1) # purple circles
        
    text = "Overlayed pinpoint failures"
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 3
    color = (128, 0, 128)
    thickness = 2
    position = (50, 50)  # x=10, y=30 pixels from top-left
    image = cv.putText(image, text, position, font, font_scale, color, thickness, cv.LINE_AA)

    _, image_bytes = cv.imencode('.png', image)  # Encode the image as a PNG
    cdi.add_camera_analysis_plot(camera_analysis_id, f"overlayed_failed_pinpoint_coords", image_bytes, "png",
                                 description=f"Overlayed positions of beam center coords which had their pinpointing fail")
    return image_bytes

def convert_beam_center_coords_to_penetration_depths(camera_analysis_id: int, unrotated_beam_center_coords: np.ndarray[float],
                                                     unc_on_beam_center_coords):
    """
    The unrotated beam center coords is stressed because homography will only work when the image has the orientation
    it was calibrated to work with.
    """
    cdi.delete_failed_pinpoints_image_by_camera_analysis_id(camera_analysis_id)
    
    # Create camera object
    camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(camera_analysis_id)
    camera_id = cdi.get_camera_and_settings_ids(camera_settings_link_id)["camera_id"]
    beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id)
    experiment_id = cdi.get_experiment_id_from_beam_run_id(beam_run_id)
    setup_id = cdi.get_setup_id_from_experiment_id(experiment_id)
    camera = AbstractCamera.setup(camera_id, setup_id)
    
    beam_center_incident_position = np.array(cdi.get_beam_incident_3d_position(beam_run_id))
    unc_beam_center_initial_position = np.array(cdi.get_unc_beam_incident_3d_position(beam_run_id))
    beam_center_directional_vector = np.array(cdi.get_beam_path_vector(beam_run_id))
    unc_beam_center_directional_vector = np.array(cdi.get_unc_beam_path_vector(beam_run_id))
    beam_center_line_vectors = [beam_center_incident_position, beam_center_directional_vector]
    
    # Pinpoint beam centers
    physical_3d_beam_centers = np.array([])
    unc_physical_3d_beam_centers = np.array([])
    
    distance_of_closest_approach_list = []
    num_of_failed_pinpoints = 0
    failed_beam_center_coords = []
    
    for beam_center_pixel, unc_beam_center_pixel in zip(unrotated_beam_center_coords, unc_on_beam_center_coords):
        
        beam_center, beam_center_uncertainty, \
        distance_of_closest_approach = extract_beam_center_position(camera, tuple(beam_center_pixel), tuple(unc_beam_center_pixel), beam_center_line_vectors, 
                                                                    unc_beam_center_initial_position, unc_beam_center_directional_vector)
        
        if np.isnan(beam_center).any() or np.isnan(beam_center_uncertainty).any():
            print(f"Beam center or uncertainty is NaN for pixel {beam_center_pixel} with uncertainty {unc_beam_center_pixel}.")
            print(f"Distance of closest approach for this pixel is {distance_of_closest_approach}.")
            num_of_failed_pinpoints += 1
            failed_beam_center_coords += [beam_center_pixel]
            continue
        
        physical_3d_beam_centers = np.vstack([physical_3d_beam_centers, beam_center]) if physical_3d_beam_centers.size else np.array([beam_center])
        unc_physical_3d_beam_centers = np.vstack([unc_physical_3d_beam_centers, beam_center_uncertainty]) if unc_physical_3d_beam_centers.size else np.array([beam_center_uncertainty])
        distance_of_closest_approach_list.append(distance_of_closest_approach)
    
    print("\n\nTotal number of failed pinpoints = ", num_of_failed_pinpoints)
    if num_of_failed_pinpoints > 0:
        print("\n\nAttempting overlay...")
        overlay_failed_pinpoints_on_image(camera_analysis_id, failed_beam_center_coords)
    
    max_uncertainty_index = np.unravel_index(np.argmax(unc_physical_3d_beam_centers, axis=None), unc_physical_3d_beam_centers.shape)
    max_uncertainty_vector = unc_physical_3d_beam_centers[max_uncertainty_index[0]]
    
    print(f"\n\n3D vector with max uncertainty for beam center position: {max_uncertainty_vector} at pixel coord {unrotated_beam_center_coords[max_uncertainty_index[0]]}")
    print("\n\nMin uncertainty for beam center position", np.min(unc_physical_3d_beam_centers))
    
    beam_center_incident_position = beam_center_line_vectors[0]
    print("\n\n Minimum distance of closest approach", np.min(distance_of_closest_approach_list))
    print("\n\n Maximum distance of closest approach", np.max(distance_of_closest_approach_list))
    
    # Convert to depths
    penetration_depth_vectors = np.array([(physical_beam_center_position - beam_center_incident_position) for physical_beam_center_position in physical_3d_beam_centers])
    distances_travelled_inside_scintillator = np.array([calculate_3d_euclidian_distance(penetration_depth_vector) for penetration_depth_vector in penetration_depth_vectors])
    
    # Calculate component-wise errors for depth displacement
    penetration_depth_vector_errors = np.array([
        [
            normal_addition_in_quadrature([unc_incident_component, unc_center_component])
            for unc_incident_component, unc_center_component in zip(unc_beam_center_initial_position, unc_physical_beam_center_position)
        ]
        for unc_physical_beam_center_position in unc_physical_3d_beam_centers
    ])
    
    # plt.plot(physical_3d_beam_centers[-1], ) # Plot of z against beam center error magnitude

    # Calculate uncertainties for distances traveled inside the scintillator
    unc_distances_travelled_inside_scintillator = np.array([
            np.sqrt(np.sum((penetration_depth_vector * penetration_depth_vector_error) ** 2)) / distance_travelled
        for penetration_depth_vector, penetration_depth_vector_error, distance_travelled in zip(penetration_depth_vectors, penetration_depth_vector_errors, distances_travelled_inside_scintillator)
    ])
    
    print("\n\nMax uncertainty for distance travelled inside scintillator", np.max(unc_distances_travelled_inside_scintillator))
    print("\n\nMin uncertainty for distance travelled inside scintillator", np.min(unc_distances_travelled_inside_scintillator))
    
    return distances_travelled_inside_scintillator, unc_distances_travelled_inside_scintillator, num_of_failed_pinpoints
