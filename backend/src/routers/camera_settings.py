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
    prefix="/camera_settings",
    tags=["camera_settings"],
)

@router.post("/{camera_id}")
def add_camera_settings_link(camera_id, settings_body: rb.SettingsCreateRequest):
    settings_id = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)["id"]
    camera_settings_link_id = cdi.add_camera_settings_link(camera_id, settings_id)["id"]
    return {"id": camera_settings_link_id}