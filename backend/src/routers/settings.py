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


from src.database.models import Camera

from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)

@router.post("")
def add_settings(settings_body: rb.SettingsCreateRequest):
    result = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)
    settings_id = result["id"]
    return {"id": settings_id}

@router.post("/scintillator-edges/{setup_camera_id}")
def add_settings(setup_camera_id: int, settings_body: rb.SettingsCreateRequest):
    settings = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)
    settings_id = settings["id"]

    setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    camera_id = setup_camera.camera_id

    camera_settings_link = cdi.add_camera_settings_link(camera_id, settings_id)
    camera_settings_id = camera_settings_link["id"]

    cdi.update_scintillator_edges_camera_settings_id(setup_camera_id, camera_settings_id)
    return {"id": camera_settings_id}


@router.get("/scintillator-edges/{setup_camera_id}")
def get_scintillator_edge_settings(setup_camera_id: int, response: Response):
    settings = cdi.get_all_settings_by_setup_camera_id(setup_camera_id)
    print(f"\n\n\n\n\n {settings} \n\n\n\n\n")

    return settings

@router.put("/scintillator-edges/{setup_camera_id}")
def update_scintillator_edges_camera_settings(setup_camera_id: int, settings_body: rb.SettingsCreateRequest):
    settings_id = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)
    return {"id": settings_id}




@router.get("/{settings_id}")
def get_settings_by_id_api(settings_id: int):
    settings = cdi.get_settings_by_id(settings_id)
    return settings