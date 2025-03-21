from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
import paramiko
import cv2
import os
import tarfile
from io import BytesIO


from src.classes.JSON_request_bodies import request_bodies as rb
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
    format: Literal["png", "jpg", "raw", "jpeg"] = Field("jpeg", example="png") #TODO Should we disallow .raw?
    meta_data_format: str = "dng" #TODO Can be made variable if need be
    

class CalibrationImageSettings(ImageSettings):
    """
    conlist used to specift field constraints.
    """    
    calibrationGridSize: List[int] = Field(..., min_items=2, max_items=2, description="Grid size as (rows, columns).")
    calibrationTileSpacing: List[float] = Field(..., min_items=1, description="Spacing between tiles in mm.")
    calibrationTileSpacingErrors: Optional[List[float]] = Field(None, max_items=2, description="Error in spacing between tiles in mm.")
    
     # Validator to ensure grid dimensions are greater than 0
    @validator("calibrationGridSize", each_item=True)
    def check_positive_grid_dimensions(cls, v):
        if v <= 1:
            raise ValueError("Grid dimensions must be greater than 1.")
        return v
    
    @validator("calibrationTileSpacing", each_item=True)
    def check_positive_spacing(cls, value):
        if value <= 0:
            raise ValueError("Each spacing value must be greater than 0")
        return value

    # Validator to ensure grid size errors are greater than 0 if provided
    @validator("calibrationTileSpacingErrors", pre=True, always=True)
    def check_positive_errors(cls, v):
        if v is None:
            return v 
        if any(error <= 0 for error in v):
            raise ValueError("All grid spacing errors must be greater than 0.")
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
    
    self.video_script_filename = "video_script.py"
    
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
  
  def generate_filename(self, camera_settings_link_id: int, context: PhotoContext, file_format, 
                        filename=None, length_of_index=5): #TODO Think length of index must be 1-9?
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
            raw = "--raw" if imageSettings.format == "raw" else ""
            
            command = f"libcamera-still -o {full_file_path}.{imageSettings.format} -t {imageSettings.timeDelay} --gain {imageSettings.gain} -n {raw} --lens-position 5"
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

  def capture_image_without_making_settings(self, camera_settings_link_id:int, imageSettings: ImageSettings, context: PhotoContext):
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
            raw = ""
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
            return full_file_path
        except Exception as e:
            raise Exception(f"Error capturing image: {e}")


  def transfer_image_overwrite(self, imageSettings: ImageSettings, camera_settings_link_id: int, full_file_path: str):
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
            added_photo = cdi.update_photo(camera_settings_link_id=camera_settings_link_id, photo=photo_bytes)#, photo_metadata=photo_meta_data_bytes)
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
        
  def check_video_script_exists(self):
    """
    Need to store video script file in the root, then store the 
    images in the test run or real run directory depending on the
    photo context. root/context/run_num/(image files here)
    """
    script_file_path = f"{self.remote_root_directory}/{self.video_script_filename}"
    # Check if the script exists on the pi.
    stdin, stdout, stderr = self.ssh_client.exec_command(f"[ -f '{script_file_path}' ] && echo true || echo false")
    
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    stdin.close()
    
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:  # Only raise an error if the command failed
        raise Exception(f"\n\n\nError when checking video script exists: \n\nOUTPUT: {output}\n\n" +
                        f"ERROR: {error}\n\n\n")
    
    if output == "true":
        return True
    
    try:
        self.open_sftp()
        local_script_path = os.path.join("/code/src", self.video_script_filename)  
        self.sftp_client.put(local_script_path, script_file_path)
        stdin, stdout, stderr = self.ssh_client.exec_command(f"[ -f '{script_file_path}' ] && echo true || echo false")
        output = stdout.read().decode().strip()
        return output == "true" # will be False if script not found

    except Exception as e:
        raise Exception(f"Error transferring video script to Pi: {e}")
    finally:
        self.close_sftp()
    

  def run_pi_video_script(self, video_settings: rb.VideoSettings):
    """
    If script not found on pi, transfer script from here to the pi.
    Then run SSH command with flags from rb.VideoSettings
    """
    log = "-log" if video_settings.log == True else ""
    command = (f"python video_script.py -dir {video_settings.directory_name} " +
              f"-num {video_settings.num_of_images} -c {video_settings.colour} " +
              f"-g {video_settings.gain} -f {video_settings.format} {log} " +
              f"-b {video_settings.bit_depth} -fr {video_settings.frame_rate}")
    
    stdin, stdout, stderr = self.ssh_client.exec_command(command)
    error = stderr.read().decode().strip()
    output_lines = stdout.readlines()
    last_line = output_lines[-1].strip() if output_lines else "" # Script prints "Image capture complete" when done
    
    if "Image capture complete" in last_line:
        print(f"Image capture finished on {self.username}.")
    else:
        raise Exception(f"Command failed with error:\n{error}")
    stdin.close()

    return None
  
  
  def create_camera_settings_link_for_video(self, username: str, video_settings: rb.VideoSettings):
      
        #TODO obviously these will take variable values once model is fleshed out
        added_settings = cdi.add_settings(frame_rate=5, lens_position=0.5, gain=video_settings.gain)
        settings_id = added_settings["id"]
        camera_id = cdi.get_camera_id_from_username(self.username)
        added_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id)
        camera_settings_link_id = added_camera_settings_link["id"]
        return camera_settings_link_id
  
  
  def transfer_video_frames(self, username: str, video_settings: rb.VideoSettings): 
    try:
        self.open_sftp()
        # Alternatively, could print tar_archive path from script and extract from stdout
        files_in_directory = self.sftp_client.listdir(f"{self.remote_root_directory}/{video_settings.directory_name}")
        tarball_files = [f for f in files_in_directory if f.endswith(('.tar', '.tar.gz', '.tgz'))]
        if not tarball_files:
            raise Exception("No tarball found in the directory.")

        # Assuming there's only one tarball, use the first match
        tarball_name = tarball_files[0]
        remote_tar_path = os.path.join(video_settings.directory_name, tarball_name)
        print(f"\n\n\nFound tarball: {tarball_name}, proceeding with extraction...\n\n\n")
        
        camera_settings_link_id = self.create_camera_settings_link_for_video(username, video_settings)
        photo_id_array = []
        with self.sftp_client.open(remote_tar_path, "rb") as remote_file:
            # Open the tarball as a stream (without loading the whole file into memory)
            with tarfile.open(fileobj=remote_file, mode="r|*") as tar:
                for member in tar:
                    if member.isfile(): 
                        extracted_file = tar.extractfile(member)
                        image_bytes = extracted_file.read()
                        
                        added_photo = cdi.add_photo(camera_settings_link_id=camera_settings_link_id, photo=image_bytes)
                        photo_id_array.append(added_photo["id"])
                
        return photo_id_array
        
    except Exception as e:
        print(f"Error transferring video frames to local device: {e}")
  
  
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
  
  