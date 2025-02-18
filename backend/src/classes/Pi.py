from fastapi import FastAPI
import paramiko
import json
from src.classes.Camera import Camera

class Pi:
  
  all = [] # List of currently instantiated Pis - not all the Pi with credentials stored by the user
  def __init__(self, inputted_username: str, inputted_ip_address: str, inputted_password: str, inputted_camera_model: str):
    
    self.username = inputted_username
    self.ip_address = inputted_ip_address
    self.password = inputted_password
    self.cameraModel = inputted_camera_model
    self.ssh_client = paramiko.SSHClient()
    self.ssh_status = False
    self.camera = Camera(self.username, self.cameraModel, self.ssh_client) 

    Pi.all.append(self)
  
  def __del__(self):
        if self.ssh_status:
          self.close_ssh_connection()
        print(f"Pi object for {self.username} destroyed.")
  
  # The two special methods below are defined for Pi instances such that
  # the Pi.all set behaves as intended. Namely, if two Pis with the same
  # username are to be instantiated, only one will be added to Pi.all.
  # Unfortunately, object would still be constructed, taking memory, just 
  # not accessible via Pi.all.
  def __hash__(self):
        return hash(self.username) # unique identifier for each Pi is the username

  # Special method called when equating Pi object to some other object
  def __eq__(self, other_object):
      if not isinstance(other_object, Pi):
          return False
      else:
        return self.username == other_object.username

  def connect_via_ssh(self):
      try:
        # Can try with an ssh connection key (see if this changes over time or constant for the device)
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # makes computer trust the ssh connection

        print("TEST")
        self.ssh_client.connect(hostname=self.ip_address,
                                port=22, username=self.username, 
                                password=self.password
                              )
        self.ssh_status = True
        
      except Exception as e:
          self.ssh_status = False
          print(f"Error connecting over SSH to f{self.username}: f{e}")
        
      finally:
        print("{0} connection status: {1}".format(self.username, self.ssh_status))
    
  def close_ssh_connection(self):
    if self.ssh_status:
      self.ssh_client.close()
      self.ssh_status = False
  
  @classmethod  
  def pis_connected_by_ssh(cls):
    return [pi for pi in Pi.all if pi.ssh_status]
  
  @classmethod  
  def get_pi_with_username(cls, user_name: str):
    
    for pi in Pi.all:
      if pi.username == user_name:
        return pi
    return None
  
  @classmethod
  def parse_config_json(cls, filename: str):
    with open(filename, 'r') as json_file:
      raspberry_pi_setup_file = json.load(json_file)
    return raspberry_pi_setup_file # Array of jsons
  
  @classmethod
  def instantiate_configured_pi_by_username(cls, username, filename: str):
    
    raspberry_pis = cls.parse_config_json(filename)
    valid_pi_list = [pi_dict for pi_dict in raspberry_pis if pi_dict.get("username") == username]
    
    if len(valid_pi_list) == 1:
      pi = valid_pi_list[0]
      return Pi(inputted_username=pi.get("username", "no username provided"),
                inputted_ip_address=pi.get("IPAddress", "no IP address provided"),
                inputted_password=pi.get("password", "no password provided"),
                inputted_camera_model=pi.get("cameraModel", "no camera model provided"))
    else:
      print("ERROR IN CONFIG") # clean later
    
  @classmethod
  def instantiate_all_pis_from_config_json(cls, filename: str):
    
    raspberry_pis = cls.parse_config_json(filename)
    for pi in raspberry_pis["pi_index"]:
      if not any(current_pi.username == pi.get("username") for current_pi in cls.all):

        Pi(
          inputted_username=pi.get("username", "no username provided"),
          inputted_ip_address=pi.get("IPAddress", "no IP address provided"),
          inputted_password=pi.get("password", "no password provided"),
          inputted_camera_model=pi.get("cameraModel", "no camera model provided")
        )
        
  @classmethod
  def delete_pi(cls, identifier): # type hint for identifier removed for now (str or Pi object)
    try:
      if isinstance(identifier, str):
          pi = cls.get_pi_with_username(identifier)
      elif isinstance(identifier, Pi):
          pi = identifier if identifier in cls.all else None
      else:
        raise Exception(f"Invalid identifer type {identifier}")
      
      if not pi:
        raise Exception(f"No Pi found with identifier: {identifier}")
      
       # If this is the last reference to the Pi object, __del__()
       # should be called by Python's garbage collection
      cls.all.remove(pi)
      
    except Exception as e:
      print(f"Error in deleting Pi instance: {e}")
