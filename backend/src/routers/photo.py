from datetime import datetime
from fastapi import Response, APIRouter
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb


from src.database.models import Camera, CameraSettingsLink, CameraSetupLink, Settings
from src.classes import Camera as PiCamera #TODO This may be a bit awkward
from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/photo",
    tags=["photo"],
)

# @router.post("scintillator-edges/{setup_camera_id}")
# def take_picture(setup_camera_id: str):
#     with Session(engine) as session:
#         statement = select()
#     camera_settings_link = 
#     settings_id = cdi.get_settings_by_setup_camera_id
#     context = PhotoContext.GENERAL
#     camera_id = cdi.get_camera_id_from_username(self.username)
#     added_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id)
#     camera_settings_link_id = added_camera_settings_link["id"]
#     photo_bytes, _ = take_single_image(username, imageSettings, context)
#     if photo_bytes:
#         return Response(content=photo_bytes, media_type="image/png")
    


def take_scintillator_edge_image(username: str, camera_settings_id:int, imageSettings: ImageSettings, context: PhotoContext):
    
    try:
        # Should have already validated the fact that Pis with these usernames are connected via SSH.
        # Pi with this username will have been deleted after SSH check if it disconnected.
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi instantiated with the username {username}")
        full_file_path = pi.camera.capture_image_without_making_settings(camera_settings_id, imageSettings, context)
        added_photo_id = pi.camera.transfer_image_overwrite(imageSettings, camera_settings_id, full_file_path)
        return added_photo_id
    
    except Exception as e:
        raise Exception(f"Error trying to take a picture: {e}")

def get_camera_and_settings_by_camera_settings_id(camera_settings_id: int) -> tuple[Camera, Settings]:
    with Session(engine) as session:
        camera_settings = session.get(CameraSettingsLink, camera_settings_id)
        settings = session.get(Settings, camera_settings.settings_id)
        camera = session.get(Camera, camera_settings.camera_id)
    return camera, settings

@router.post("/scintillator-edges/{setup_camera_id}")
def take_picture(setup_camera_id: str):
    camera_settings_id = None
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_settings_id = setup_camera.scintillator_edges_photo_camera_settings_id
    camera, settings = get_camera_and_settings_by_camera_settings_id(camera_settings_id)
    
    filename = "scintillator_edge"
    gain = settings.gain #TODO Other settings need adding to ImageSettings
    timeDelay = 1
    format = "jpeg"
    image_settings = ImageSettings(filename=filename, gain=gain, timeDelay=timeDelay, format=format)
    photo_id = take_scintillator_edge_image(camera.username, camera_settings_id, image_settings, PhotoContext.GENERAL)
    cdi.update_scintillator_edges_camera_settings_id(setup_camera_id, camera_settings_id)
    return {"id": photo_id}

# @router.get("/scintillator-edges/{setup_camera_id}")
# def get_scintillator_edge_picture(setup_camera_id: str):
