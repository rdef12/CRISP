from src.classes.Pi import Pi
from src.classes.Camera import ImageSettings
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from typing import List
from src.database.CRUD.photo_CRUD import get_photo_from_id

def take_single_image(username: str, imageSettings: ImageSettings):
    
    try:
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi instantiated with the username {username}")
        
        camera_settings_link_id = pi.camera.capture_image(imageSettings)
        added_photo_id = pi.camera.transfer_image(imageSettings, camera_settings_link_id)
        # return (f"{pi.camera.local_image_directory}/{imageSettings.filename}.{imageSettings.format}") # return filepath for convenience - acts like a bool
        photo_bytes = get_photo_from_id(photo_id=added_photo_id)
        return photo_bytes
    except Exception as e:
        print(f"Error trying to take a picture: {e}")
        return 0 


def take_multiple_images(usernames_list: List[str], imageSettings_list: List[ImageSettings]):

    try:
        # Should have already validated the fact that Pis with these usernames are connected via SSH.
        pis_to_image_with = [Pi.get_pi_with_username(username) for username in usernames_list] 
        
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(pi.camera.capture_image, imageSettings) for pi, imageSettings in zip(pis_to_image_with , imageSettings_list)] 
            for future in as_completed(futures):
                result = future.result()
                
                if not result["success"]:
                    raise Exception(f"Error with {result['pi']}: {result['error']}")
                
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

