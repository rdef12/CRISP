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
    result = cdi.add_settings(30, 0, settings_body.gain)
    settings_id = result["id"]
    return {"id": settings_id}

@router.get("/{settings_id}")
def get_settings_by_id_api(settings_id: int):
    settings = cdi.get_settings_by_id(settings_id)
    return settings