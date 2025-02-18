"""
Can I add a feature for creating the directory on the Pi for storing the images if it does not yet exist. Then,
the remote directory can be made constant for all Pis. In genetal, we need images to be saved locally because we want as little
delay between consecutive images as possible. At the end of the image capturing, they can be transferred to the GUI.

RETURN METADATA AND IMAGE TO DATABASE - for now, save to folder in frontend/public/images/cam_test
"""
from pydantic import BaseModel, Field
import socket
import cv2
import os

class ImageSettings(BaseModel):
    """
    Possible extra settings:
    shutter speed/exposure time/contrast/brightness/q/ISO
    
    --raw flag will be added to libcamera command if format == "raw"
    For streaming, might want a different model.
    """
    filename: str = Field(...) # without file extension!!
    gain: int = Field(1, ge=0, example=1)
    timeDelay: int = Field(1000, ge=0, example=1000) # Given in milliseconds
    format: str = Field("raw", example="png") # Could use Literal to validate inputted formats (or just make a drop-down)
    
    
class Camera():
  
  def __init__(self, username, cameraModel, ssh_client):
    
    self.username = username
    self.cameraModel = cameraModel
    self.ssh_client = ssh_client # Hopefully, this is a reference to the Pi SSH Client?
    self.sftp_client = None # Needs to be opened with the Camera method
    self.local_image_directory = "/code/src/images" # Inside Backend container
    self.remote_image_directory = f"/home/{self.username}/created_directory_2025"
    
    self.video_capture = None # Will be the cv2 video capture (such that cap can be released from any function, without global cap).
    self.stream_source = 'udp://{}:1234'.format(os.getenv("LOCAL_IP_ADDRESS"))
    
    # HARDCODED FOR NOW - but can be GUI options in the future
    self.stream_codec = "libav"
    self.stream_framerate = 30
    self.stream_bitrate = "1k" # was 1M before
    
  def __del__(self):
        print(f"Destroying Camera object for {self.username} {self.cameraModel}")
    
  def open_sftp(self):
    self.sftp_client = self.ssh_client.open_sftp()
    self.sftp_status = True

  def close_sftp(self):
     if self.sftp_status:
        self.sftp_client.close()
        self.sftp_status = False
        
  def check_image_directory_exists(self):
    try:
        command = f"if [ ! -d '{self.remote_image_directory}' ]; then mkdir -p '{self.remote_image_directory}'; fi" # Bash if statement
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        
        if standard_error := stderr.read().decode():
                raise Exception(standard_error)
        return 1  # Directory exists or was created successfully
    
    except Exception as e:
        print(f"Error when checking remote image directory exists: {e}")
        return 0
    
  def capture_image(self, imageSettings: ImageSettings):
        
        self.check_image_directory_exists()
        # Should there be timestamping code in here?
        try:
            command = "libcamera-still -o {0}/{1}.{2} -t {3} --gain {4} {5}".format(self.remote_image_directory,
                                                                                imageSettings.filename, 
                                                                                imageSettings.format,
                                                                                imageSettings.timeDelay,
                                                                                imageSettings.gain,
                                                                                "--raw" if imageSettings.format=="raw" else "")
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            if standard_error := stderr.read().decode():
                raise Exception(standard_error)
            
        except Exception as e:
            print(f"Error capturing image: {e}")
            return 0
  
  
  def transfer_image(self, imageSettings: ImageSettings):
    """
    METADATA SHOULD BE RETURNED TOO!
    """
    try: 
      # NOTE: needed to edit write privileges of local transferred_images directory with chmod # Can do this before production
      self.check_image_directory_exists()
      remotepath = "{0}/{1}.{2}".format(self.remote_image_directory, imageSettings.filename, imageSettings.format)
      localpath = "{0}/{1}.{2}".format(self.local_image_directory, imageSettings.filename, imageSettings.format)
      
      self.open_sftp()
      self.sftp_client.get(remotepath, localpath)
      self.close_sftp()
      return 1

    except Exception as e:
      print(f"Error transferring image to local device: {e}")
      return 0
  
  
  def stream_clean_up(self):
    try: 
        # How to ensure this matches the actual camera in use for future users? - directory varies for type of cam connected to Pi.
        stdin, stdout, stderr = self.ssh_client.exec_command("lsof /dev/video0")
        if stdout.read().strip():
          self.ssh_client.exec_command("sudo killall libcamera-vid")
        
        if standard_error := stderr.read().decode():
            raise Exception(standard_error)
          
    except Exception as e:
      print(f"Error cleaning up streaming processes on {self.username} {self.cameraModel}: {e}")
    
  
  # NEXT - move the stream source location to be a attribute of the cam when instantiated - call networking function to get local_ip
  def start_stream_capture(self):
    cap = cv2.VideoCapture(self.stream_source)
    if not cap.isOpened():
        raise Exception("Unable to open stream source")
    return cap
  
  
  def stream_to_local_device(self):
    """
    NOTE - The --network host mode for Docker containers only works in native Linux environments.
    
    E.g. docker run -p 1234:1234/udp <docker_image>
    -p 1234:1234 is used to forward all traffic for port 1234 on the host device
    to port 1234 inside the container. The /udp is because the port mapping is
    for UDP traffic.
    
    I should add EXPOSE 1234/udp to the backend Dockerfile. (just metadata?)
    Then, add 1234:1234/udp to the ports section of compose.yaml.
    
    I need the Raspberry Pi to forward the UDP stream to 1234 on the host device.
    Then, the host device automatically forwards this to 1234 inside the container.
    """
    try:
        self.stream_clean_up()
        
        print(self.stream_source)
        
        print("B")
        # # Placing an & at the end of the command runs it as a background process
        stdin, stdout, stderr = self.ssh_client.exec_command(
        f"libcamera-vid -t 0 --bitrate {self.stream_bitrate} --inline --width 1920 --height 1080 --rotation 180 " +
        f"--framerate {self.stream_framerate} --codec {self.stream_codec} --libav-format mpegts -n -o {self.stream_source}") # if not streaming after 30 secs, it will timeout
        
        print("C")
        if standard_error := stderr.read().decode():
            raise Exception(standard_error)
          
        # output = stdout.read().decode()
        # print(f"Stream output: {output}")
        
        return True
    
    except Exception as e:
      print(f"Streaming error: {e}")
      return False
  
  