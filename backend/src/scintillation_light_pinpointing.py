"""
To test this well, will need distortion correction applied to top HQ cam images when
producing homographies!

I also think the beam edge detection should be applied to undistorted images only
"""
from src.homography_pinpointing import AbstractCamera, extract_weighted_average_3d_physical_position

def pinpoint_bragg_peak(beam_run_id, camera_id_list, setup_id):
    try:
        ########## DATABASE SOURCED ##########
        bragg_peak_pixel_list = None
        bragg_peak_pixel_error_list = None    
        ######################################
        
        cameras = [AbstractCamera.setup(camera_id, setup_id) for camera_id in camera_id_list]
        weighted_intersection_point, unc_weighted_intersection_point = (
            extract_weighted_average_3d_physical_position(cameras, bragg_peak_pixel_list, bragg_peak_pixel_error_list, scintillator_present=True))
        
        print(f"3D Bragg peak position: {weighted_intersection_point} +/- {unc_weighted_intersection_point}")
        return {"bragg_peak_position": weighted_intersection_point, "bragg_peak_position_error": unc_weighted_intersection_point}
        
    except Exception as e:
        print(f"Error when pinpointing bragg peak: {e}")
    