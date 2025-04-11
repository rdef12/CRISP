from src.classes.Pi import Pi
from src.database.CRUD import CRISP_database_interaction as cdi
from pydantic import BaseModel
import os

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
    
def configure_pi(pi_config: PiConfig): # Change to interact with database
    username = pi_config.username
    ip_address = pi_config.IPAddress
    password = pi_config.password
    model = pi_config.cameraModel
    camera_id = cdi.add_camera(username=username, ip_address=ip_address, password=password, model=model)
    return camera_id

def remove_configured_pi(username: str): # Change to interact with database
    cdi.delete_camera_with_username(username)    
    return None

def get_single_pi_status(username: str):
    if connected_pi := Pi.get_pi_with_username(username): 
            return connected_pi.check_ssh_connection()
    return False
     
def get_raspberry_pi_statuses():

    pis_in_database = Pi.parse_database()
    pi_status_array = []
    for pi_dict in pis_in_database:
        
        username = pi_dict.username
        # Looks to see if a Pi object exists with a given username in the config_file
        if connected_pi := Pi.get_pi_with_username(username): 
            connection_status = connected_pi.check_ssh_connection()
        else:
            connection_status = False
        pi_status_array.append(ClientSidePiStatus(username=username,
                                                  IPAddress=pi_dict.ip_address,
                                                  cameraModel=pi_dict.model,
                                                  connectionStatus=connection_status))
    return pi_status_array
    
    
def connect_over_ssh(username: str):
    
    if existing_pi := Pi.get_pi_with_username(username):
        Pi.delete_pi(username) # delete the pi object from memory
    
    pi = Pi.instantiate_configured_pi_by_username(username)
    try:
        pi.connect_via_ssh()
        if pi.ssh_status:
            return True
        else:
            return False
    except Exception as e:
        raise Exception(e)

def disconnect_from_ssh(username: str):
    try:
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi with the username {username}")

        Pi.delete_pi(username) # deleted from memory and network connections closed
        return False # False returned because this is the CONNECTION status

    except Exception as e:
        print(f"Error: {e}")
        return True # might be weird to return True here - trying to say disconnect failed