from datetime import datetime
from fastapi import Response, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb


from src.database.models import Camera, CameraSettingsLink

from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/camera-settings",
    tags=["camera-settings"],
)

@router.post("/{camera_id}")
def add_camera_settings_link(camera_id, settings_body: rb.SettingsCreateRequest):
    settings_id = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)["id"]
    camera_settings_link_id = cdi.add_camera_settings_link(camera_id, settings_id)["id"]
    return {"id": camera_settings_link_id}

@router.get("/calibration/{camera_settings_id}")
def get_camera_settings_link(camera_settings_id):
    camera_settings = cdi.get_camera_settings_by_id(camera_settings_id)
    return camera_settings

@router.get("/beam-run/real/{beam_run_id}/camera/{camera_id}")
def get_real_settings(beam_run_id: int, camera_id: int):
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                              .where(CameraSettingsLink.beam_run_id == beam_run_id)
                              .where(CameraSettingsLink.camera_id == camera_id))
        try:
            camera_settings = session.exec(camera_settings_statement).one()
            number_of_images = camera_settings.number_of_images
            take_raw_images = camera_settings.take_raw_images
            if number_of_images is None or take_raw_images is None:
                return JSONResponse(content={"id": camera_id,
                                         "has_settings": False})
            return JSONResponse(content={"id": camera_id,
                                         "has_settings": True})
        except:
            return JSONResponse(content={"id": camera_id,
                                         "has_settings": False})
