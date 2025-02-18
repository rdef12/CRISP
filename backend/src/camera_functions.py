from src.classes.Pi import Pi
from src.classes.Camera import ImageSettings
import cv2 # Need to add as a poetry dependency
import os

def take_single_picture(username: str, imageSettings: ImageSettings):
    
    try:
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi instantiated with the username {username}")
        
        # NOTE - Do I need to use async/await to make sure the image taking has finished before transferring?
        pi.camera.capture_image(imageSettings)
        pi.camera.transfer_image(imageSettings)
        return (f"{pi.camera.local_image_directory}/{imageSettings.filename}.{imageSettings.format}") # return filepath for convenience - acts like a bool
            
    except Exception as e:
        print(f"Error trying to take a picture: {e}")
        return 0
    
    
def stream_video_feed(username: str):
    try:
        print("Before A")
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No Pi instantiated with the username {username}")
        
        # Check if UDP streaming is established
        print("before A 2")
        
        success = pi.camera.stream_to_local_device()
        print(success)
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

