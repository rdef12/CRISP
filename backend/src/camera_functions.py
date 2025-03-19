from src.classes.Pi import Pi
from src.classes.Camera import ImageSettings, PhotoContext
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import base64
import numpy as np
from typing import List
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


def take_single_video(username: str, video_settings: rb.VideoSettings):
    try:
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No Pi instantiated with the username {username}")
        
        if pi.camera.check_video_script_exists():
            print("\n\n\nScript found!\n\n\n")
            pi.camera.run_pi_video_script(video_settings)
        else:
            raise Exception("Video script could not be accessed on pi")
        
    except Exception as e:
        print(f"Error taking video on {username}: {e}")