from src.classes.Pi import Pi
from pydantic import BaseModel
import os
import json

# The database will replace this in the future
PI_CONFIG_FILEPATH = os.path.join(os.path.dirname(__file__), "pi_config.json")

class ClientSidePiStatus(BaseModel):
    # FastAPI uses Pydantic for data validation and serialization
    username: str
    IPAddress: str
    cameraModel: str
    connectionStatus: bool 

class PiConfig(BaseModel):
    username: str
    IPAddress: str
    password: str
    cameraModel: str
    
def configure_pi(pi_config):
    with open(PI_CONFIG_FILEPATH, "r") as file:
            data = json.load(file)

    data.append(pi_config.dict())
    with open(PI_CONFIG_FILEPATH, "w") as file:
        json.dump(data, file, indent=4)
    return None

def remove_configured_pi(username: str):
    with open(PI_CONFIG_FILEPATH, "r") as file:
            data = json.load(file)
            
    # Remove the dictionary with the matching username
    new_list = [item for item in data if item.get("username") != username]

    with open(PI_CONFIG_FILEPATH, "w") as file:
        json.dump(new_list, file, indent=4)
    
    # Pi object associated with this config entry is deleted if it exists
    if (pi := Pi.get_pi_with_username(username)):
        Pi.delete_pi(pi)
    return None


def get_raspberry_pi_statuses():

    configured_pis = Pi.parse_config_json(PI_CONFIG_FILEPATH)
    pi_status_array = []
    for pi_dict in configured_pis:
        
        username = pi_dict.get("username")
        # Looks to see if a Pi object exists with a given username in the config_file
        if connected_pi := Pi.get_pi_with_username(username): 
            connection_status = connected_pi.ssh_status
        else:
            connection_status = False
            
        pi_status_array.append(ClientSidePiStatus(username=username,
                                                  IPAddress=pi_dict.get("IPAddress"),
                                                  cameraModel=pi_dict.get("cameraModel"),
                                                  connectionStatus=connection_status))
    return pi_status_array
    
    
def connect_over_ssh(username: str):

    pi = Pi.instantiate_configured_pi_by_username(username, PI_CONFIG_FILEPATH)
    try:
        pi.connect_via_ssh()
        if pi.ssh_status:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        
def disconnect_from_ssh(username: str):

    try:
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi with the username {username}")

        Pi.delete_pi(username) # deleted from memory and network connections closed
        return False # False returned because this is the CONNECTION status

    except Exception as e:
        print(f"Error: {e}")
        return True # might be weird to return True here - trying to say disconnect failed