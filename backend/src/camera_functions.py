from src.classes.Pi import Pi
from src.classes.Camera import ImageSettings, PhotoContext
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import base64
import numpy as np
from typing import List, Dict
from src.database.CRUD import CRISP_database_interaction as cdi
from src.calibration_functions import determine_frame_size
from src.classes.JSON_request_bodies import request_bodies as rb


def load_image_byte_string_to_opencv(image_byte_string: str):
    nparr = np.frombuffer(image_byte_string, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def get_image_bytestring_frame_size(image_byte_string: str):
    image = load_image_byte_string_to_opencv(image_byte_string)
    return determine_frame_size(image=image)

def take_single_image(username: str, imageSettings: ImageSettings, context: PhotoContext):
    
    try:
        # Should have already validated the fact that Pis with these usernames are connected via SSH.
        # Pi with this username will have been deleted after SSH check if it disconnected.
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi instantiated with the username {username}")
        
        camera_settings_link_id, full_file_path = pi.camera.capture_image(imageSettings, context)
        added_photo_id = pi.camera.transfer_image(imageSettings, camera_settings_link_id, full_file_path)
        photo_bytes = cdi.get_photo_from_id(photo_id=added_photo_id)
        return photo_bytes, added_photo_id
    
    except Exception as e:
        print(f"Error trying to take a picture: {e}")
        return 0 

def imaging_helper(pi, imageSettings, context):
    
        camera_settings_link_id, full_file_path = pi.camera.capture_image(imageSettings, context)
        added_photo_id = pi.camera.transfer_image(imageSettings, camera_settings_link_id, full_file_path)
        photo_bytes = cdi.get_photo_from_id(photo_id=added_photo_id)
        return [photo_bytes, added_photo_id]

def take_multiple_images(usernames_list: List[str], imageSettings_list: List[ImageSettings], context: PhotoContext):

    try:
        # Should have already validated the fact that Pis with these usernames are connected via SSH.
        pis_to_image_with = [Pi.get_pi_with_username(username) for username in usernames_list]
        if any(pi is None for pi in pis_to_image_with):
            pi_indices = [i for i, pi in enumerate(pis_to_image_with) if pi is None]
            disconnected_usernames = [usernames_list[i] for i in pi_indices]
            raise ValueError(f"The following Raspberry Pis have disconnected: {disconnected_usernames}")
        
        results_array = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(imaging_helper, pi, imageSettings, context) for pi, imageSettings in zip(pis_to_image_with , imageSettings_list)] 
            for future in as_completed(futures):
                result = future.result()
                # ERROR HANDLING HERE!
                results_array.append(result)
                
        # If done correctly, this will be an array of tuples each containing a photo bytestring and photo id
        return np.array(results_array) # ndarray so can do slicing on it
                
    except Exception as e:
        print(f"Error taking multiple images at once: {e}")
    
    
def stream_video_feed(username: str):
    try:
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No Pi instantiated with the username {username}")
        
        success = pi.camera.stream_to_local_device()
        if success:
            print("D")
            cap = pi.camera.start_stream_capture()
            
            print("E")
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    print("Error encoding frame")
                    continue

                yield (b'--frame\r\n' +
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
    
    except Exception as e:
        print(f"Error streaming video: {e}")
    
    finally:
        if 'cap' in locals():  # locals() returns a dictionary of declared variables in scope
            cap.release()
            
############# MAIN BEAM RUN #########################

def take_single_video_for_main_run(camera_settings_link_id):
    try:
        camera_id = cdi.get_camera_and_settings_ids(camera_settings_link_id)["camera_id"]
        print("\n\ncamera id:", camera_id, type(camera_id), "\n\n")
        username = cdi.get_username_from_camera_id(camera_id)
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No Pi instantiated with the username {username}")
        
        if not pi.camera.check_video_script_exists():
            raise Exception("Video script could not be accessed on pi")
        
        beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id)
        pi.camera.run_main_run_script(beam_run_id, camera_settings_link_id)
        
        photo_id_array = pi.camera.transfer_video_frames(beam_run_id, context="real",
                                                         camera_settings_link_id=camera_settings_link_id)
        return photo_id_array
        
    except Exception as e:
        print(f"Error taking video on {username}: {e}")
        raise

def take_multiple_videos_for_main_run(camera_settings_link_id_array) -> Dict[str, List[str]]:
    """
    Executes video recording for multiple users in parallel using ThreadPoolExecutor.
    Returns a dictionary where each username maps to their photo ID array.
    """
    results = {}
    with ThreadPoolExecutor() as executor:
        # The executor is the key, the username is the value in the futures dict
        futures = {executor.submit(take_single_video_for_main_run, camera_settings_link_id): camera_settings_link_id 
                   for camera_settings_link_id in camera_settings_link_id_array}
        
        for future in futures:
            camera_settings_link_id = futures[future] # way to map futures.result() to a dict with username as the key
            try:
                results[camera_settings_link_id] = future.result()  # Store result in dictionary
            except Exception as e:
                print(f"Error in test run video capture for image with camera setting link id: {camera_settings_link_id}: {e}")
                results[camera_settings_link_id] = []  # Store an empty list in case of failure
    return results

############# TEST BEAM RUN #########################

def take_single_video_for_test_run(camera_settings_link_id_array):
    try:
        camera_id = cdi.get_camera_and_settings_ids(camera_settings_link_id_array[0])["camera_id"]
        username = cdi.get_username_from_camera_id(camera_id)
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No Pi instantiated with the username {username}")
        
        if not pi.camera.check_video_script_exists():
            raise Exception("Video script could not be accessed on pi")
        
        beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id_array[0])
        pi.camera.run_test_run_script(beam_run_id, camera_settings_link_id_array)
        photo_id_array = pi.camera.transfer_video_frames(beam_run_id, context="test")
        return photo_id_array
        
    except Exception as e:
        print(f"Error taking video on {username}: {e}")
        raise


def take_multiple_videos_for_test_run(camera_settings_link_id_array) -> Dict[str, List[str]]:
    """
    Executes video recording for multiple users in parallel using ThreadPoolExecutor.
    Returns a dictionary where each username maps to their photo ID array.
    """
    results = {}
    with ThreadPoolExecutor() as executor:
        # The executor is the key, the link id is the value in the futures dict
        futures = {executor.submit(take_single_video_for_test_run, camera_settings_link_id): camera_settings_link_id 
                   for camera_settings_link_id in camera_settings_link_id_array}
        
        for future in futures:
            camera_settings_link_id = futures[future] # way to map futures.result() to a dict with username as the key
            try:
                results[camera_settings_link_id] = future.result()  # Store result in dictionary
            except Exception as e:
                print(f"Error in test run video capture for image with camera setting link id: {camera_settings_link_id}: {e}")
                results[camera_settings_link_id] = []  # Store an empty list in case of failure
    return results