from fastapi import FastAPI
import paramiko
import socket
import json
from src.classes.Camera import Camera
from src.database.CRUD import CRISP_database_interaction as cdi
import time

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
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # makes computer trust the ssh connection
        print(self.ip_address, self.username, self.password)
        # the reason I am setting a timeout is that the GUI will show connecting... for 1 min o/w
        # Having a timeout makes the GUI more responsive - quicker info on when something is going wrong.
        self.ssh_client.connect(hostname=self.ip_address,
                                port=22, username=self.username, 
                                password=self.password, timeout=15
                              ) 
      except Exception as e:
          self.ssh_status = False
          print(f"Error connecting over SSH to {self.username}: {e}")
        
      finally:
        print("{0} connection status: {1}".format(self.username, self.ssh_status))
        
  def check_ssh_connection(self):
        if self.ssh_status:
            try:
                # Try executing a simple command to check status
                # stdin, stdout, stderr = self.ssh_client.exec_command('echo "Hello"', timeout=10)
                # stdout.channel.recv_exit_status()  # Will raise an exception if the connection is broken
                
                return True # Above line commented out for demo purposes
            except (paramiko.SSHException, paramiko.AuthenticationException, socket.error):
                print(f"\n\n\n Connection to {self.username} is lost. \n\n\n")
                Pi.delete_pi(self.username)
                return False
        return False
      
  def get_pi_disk_space(self):
    if self.ssh_status:
        _, stdout, _ = self.ssh_client.exec_command("df -h / | grep '/' | awk '{print $3 \" / \" $2}'", timeout=10)
        return stdout.read().decode('utf-8').strip()
    raise paramiko.SSHException("SSH connection not established.")

  
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
  def parse_database(cls):
    all_cameras = cdi.get_all_cameras()
    return all_cameras


  @classmethod
  def instantiate_configured_pi_by_username(cls, username):
    raspberry_pi = cdi.get_camera_entry_with_username(username)
    return Pi(inputted_username=raspberry_pi.username,
                inputted_ip_address=raspberry_pi.ip_address,
                inputted_password=raspberry_pi.password,
                inputted_camera_model=raspberry_pi.model)
  
  # @classmethod
  # def load_pis_on_startup(cls):
  #   pass
        
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
