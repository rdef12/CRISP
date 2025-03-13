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
    prefix="/photo",
    tags=["photo"],
)

@router.post("/{camera_settings_id}")
def take_picture():
  return