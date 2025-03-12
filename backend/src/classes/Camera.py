"""
Can I add a feature for creating the directory on the Pi for storing the images if it does not yet exist. Then,
the remote directory can be made constant for all Pis. In genetal, we need images to be saved locally because we want as little
delay between consecutive images as possible. At the end of the image capturing, they can be transferred to the GUI.

RETURN METADATA AND IMAGE TO DATABASE - for now, save to folder in frontend/public/images/cam_test
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
import socket
import paramiko
import cv2
import os

from src.database.CRUD import CRISP_database_interaction as cdi
from enum import Enum

class PhotoContext(Enum): #TODO either set by the api calling it or is a path variable (idk)
    GENERAL = 1 # Also used for calibration images too.
    TEST_RUN = 2
    REAL_RUN = 3

def write_bytes_to_file(image_bytes: bytes, output_path: str):
    try:
        with open(output_path, "wb") as file:
            file.write(image_bytes)
        print(f"Image successfully written to {output_path}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while writing the file: {e}") from e

class ImageSettings(BaseModel):
    """
    Possible extra settings:
    shutter speed/exposure time/contrast/brightness/q/ISO
    """
    filename: str = Field(..., min_length=1, description="Filename without extension.")
    gain: int = Field(1, gt=0, example=1)
    timeDelay: int = Field(1000, ge=0, example=1000, description="Time delay in milliseconds") 
    format: Literal["png", "jpg", "raw", "jpeg"] = Field("jpeg", example="png")
    meta_data_format: str = "dng" #TODO Can be made variable if need be
    

class CalibrationImageSettings(ImageSettings):
    calibrationGridSize: List[int] = Field(..., min_items=2, max_items=2, description="Grid size as (rows, columns).")
    calibrationTileSpacing: float = Field(..., gt=0, description="Spacing between tiles in mm.")
    calibrationGridSizeErrors: Optional[List[int]] = Field(None, description="Grid Spacing Errors in mm.")
    
     # Validator to ensure grid dimensions are greater than 0
    @validator("calibrationGridSize", each_item=True)
    def check_positive_grid_dimensions(cls, v):
        if v <= 0:
            raise ValueError("Grid dimensions must be greater than 0.")
        return v

    # Validator to ensure grid size errors are greater than 0 if provided
    @validator("calibrationGridSizeErrors", each_item=True)
    def check_positive_errors(cls, v):
        if v <= 0:
            raise ValueError("Grid size errors must be greater than 0.")
        return v
    
    def to_image_settings(self) -> ImageSettings:
        return ImageSettings(
            filename=self.filename,
            gain=self.gain,
            timeDelay=self.timeDelay,
            format=self.format,
            meta_data_format=self.meta_data_format
        )
    

class Camera():
  
  def __init__(self, username, cameraModel, ssh_client):
    
    self.username = username
    self.cameraModel = cameraModel
    self.ssh_client = ssh_client # Hopefully, this is a reference to the Pi SSH Client?
    self.sftp_client = None # Needs to be opened with the Camera method
    self.local_image_directory = "/code/src/images" # Inside Backend container # Change to go directly to database in future?
    # self.remote_image_directory = f"/home/{self.username}/created_directory_2025" 
    self.remote_root_directory = f"/home/{self.username}" 
    self.general_image_directory = f"{self.remote_root_directory}/general"
    self.test_run_image_directory = f"{self.remote_root_directory}/experiment/test_beam_run_id_"
    self.real_run_image_directory = f"{self.remote_root_directory}/experiment/real_beam_run_id_"
    
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
        
  def generate_file_path(self, context: PhotoContext):
      match context:
          case PhotoContext.GENERAL:
              print("\n\n\n\n\n\n\n")
              print(self.general_image_directory)
              return f"{self.general_image_directory}"
          case PhotoContext.TEST_RUN:
              return f"{self.test_run_image_directory}"
          case PhotoContext.REAL_RUN:
              return f"{self.real_run_image_directory}"
  
  def generate_filename(self, camera_settings_link_id: int, context: PhotoContext, file_format, filename=None, length_of_index=5): #TODO Think length of index must be 1-9?
      match context:
          case PhotoContext.GENERAL:
              return f"{filename}_cslID_{camera_settings_link_id}"
          # case PhotoContext.REAL_RUN: #TODO check these later when the functionality gets built out
          #     beam_energy = cdi.get_beam_run_id_from_camera_settings_link_id(camera_settings_link_id)
          #     return f"real_beam_run_energy_{beam_energy}_cslID_{camera_settings_link_id}%0{length_of_index}d"
          # case PhotoContext.TEST_RUN:
          #     beam_energy = cdi.get_beam_run_id_from_camera_settings_link_id(camera_settings_link_id)
          #     return f"test_beam_run_energy_{beam_energy}_cslID_{camera_settings_link_id}%0{length_of_index}d"

              

  def check_image_directory_exists(self, context: PhotoContext):
    try:
        file_path = self.generate_file_path(context)
        command = f"if [ ! -d '{file_path}' ]; then mkdir -p '{file_path}'; fi" # Bash if statement
        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        
        if standard_error := stderr.read().decode():
                raise Exception(standard_error)
        return file_path  # Directory exists or was created successfully
    
    except Exception as e:
        raise Exception(f"Error when checking remote image directory exists: {e}")
    
  def capture_image(self, imageSettings: ImageSettings, context: PhotoContext):
        try:
            print("\n\n\n\n\n I've started adding all the settings")
            added_settings = cdi.add_settings(frame_rate=5, lens_position=0.5, gain=imageSettings.gain) #TODO obviously these will take variable values once model is fleshed out
            settings_id = added_settings["id"]
            camera_id = cdi.get_camera_id_from_username(self.username)
            added_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id)
            camera_settings_link_id = added_camera_settings_link["id"]
            print("\n\n\n\n\n I managed to add all the settings")
        except Exception as e:
            print(f"Error: {e} ") # TODO finish proper error handling here
            raise e
        
        try:
            print("\n\n\n\n\n I will try to check the directory")
            file_path = self.check_image_directory_exists(context)
            print("\n\n\n\n\n Directory checked")
        except Exception as e:
            raise e    
        # Should there be timestamping code in here?
        print("\n\n\n\n\n I will try to generate the file name")

        filename = self.generate_filename(camera_settings_link_id, context, imageSettings.format, filename=imageSettings.filename) # TODO maybe dont need filename as key word arg if set in imageSettings class
        full_file_path = f"{file_path}/{filename}"
        # TODO need a overwrite confirmation here for duplicate filename not sure how to do this frontend wise (or increment the filename)
        print("\n\n\n\n\n I have generated the file name")
        
        try:
            print("\n\n\n\n\n I will try to create the file")
            
            # raw = "--raw" #raw = "" #changed for testing
            if imageSettings.format == "raw":
                raw = "--raw"
            command = f"libcamera-still -o {full_file_path}.{imageSettings.format} -t {imageSettings.timeDelay} --gain {imageSettings.gain} -n {raw}"#TODO changed for testing without camera
            timeout=30 #TODO temporary
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip() # TODO maybe the warnings here can be logged
            stdin.close()
            
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:  # Only raise an error if the command failed
                raise Exception(f"Command '{command}' failed with exit status {exit_status}:\n{error}")
            
            print("\n\n\n\n\n I created the file")
            print(camera_settings_link_id)
            print(full_file_path)
            return camera_settings_link_id, full_file_path
        except Exception as e:
            raise Exception(f"Error capturing image: {e}")


  def transfer_image(self, imageSettings: ImageSettings, camera_settings_link_id: int, full_file_path: str):
    """
    Returns the image bytes and metadata instead of copying the file locally.
    Provides detailed error handling.
    """
    print("\n\n\n\n\n The transfer has begun")
    remote_image_path = f"{full_file_path}.{imageSettings.format}"
    print(f"Remote image path: {remote_image_path}")
    remote_photo_meta_data_path = f"{full_file_path}.{imageSettings.meta_data_format}"
    try:
        self.open_sftp()

    except paramiko.SSHException as e:
        print("f")
        raise Exception(f"SSH error while opening SFTP connection: {e}")
    except paramiko.AuthenticationException:
        print("g")
        raise Exception("Authentication failed, please verify your credentials.")
    except paramiko.SFTPError as e:
        print("h")
        raise Exception(f"SFTP error: {e}")
    except Exception as e:
        print("i")
        raise Exception(f"Unexpected error while establishing SFTP connection: {e}")
    
    try:
        with self.sftp_client.file(remote_image_path, "rb") as remote_file1:#, \
            #  self.sftp_client.file(remote_photo_meta_data_path, "rb") as remote_file2:
            photo_bytes = remote_file1.read()
            if not photo_bytes:
                raise ValueError(f"Failed to read image data from {remote_image_path}, photo_bytes is empty")
    
            # photo_meta_data_bytes = remote_file2.read()
            added_photo = cdi.add_photo(camera_settings_link_id=camera_settings_link_id, photo=photo_bytes)#, photo_metadata=photo_meta_data_bytes)
            # added_photo = cdi.add_photo_for_testing(camera_settings_link_id=camera_settings_link_id, photo=photo_bytes)
            added_photo_id = added_photo["id"]
            print("\n\n\n\n\n I have finished this try alright")
        return added_photo_id
    
    except FileNotFoundError as e:
        print("a")
        raise Exception(f"Error: One or more files not found on the remote server at path: {e}")
    except PermissionError as e:
        print("b")
        raise Exception(f"Error: Permission denied while accessing one or more files: {e}")
    except paramiko.SSHException as e:
        print("c")
        raise Exception(f"SSH error while transferring the image: {e}")
    except IOError as e:
        print("d")
        raise Exception(f"IO error occurred while reading one or more of the files: {e}")
    except Exception as e:
        print("e")
        raise Exception(f"Unexpected error while reading the image: {e}")

    finally:
        try:
            self.close_sftp()
        except Exception as e:
            raise Exception(f"Error while closing SFTP connection: {e}")
  
  
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
        f"--framerate {self.stream_framerate} --codec {self.stream_codec} --libav-format mpegts -n -o {self.stream_source}",
        timeout=30) # if not streaming after 30 secs, it will timeout
        
        print("C")
        if standard_error := stderr.read().decode():
            raise Exception(standard_error)
          
        # output = stdout.read().decode()
        # print(f"Stream output: {output}")
        
        return True
    
    except Exception as e:
      print(f"Streaming error: {e}")
      return False
  
  