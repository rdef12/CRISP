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
    prefix="/camera",
    tags=["camera"],
)


@router.get("")
def get_all_cameras_api(response: Response) -> list[Camera]:
    camera = cdi.get_all_cameras_for_react_admin()
    response.headers["Content-Range"] = str(len(camera))
    return camera


@router.get("/statuses")
def get_pi_statuses(response: Response):
    pi_status_array = get_raspberry_pi_statuses()
    pi_status_response = []
    for pi_status in pi_status_array:
        camera_id = cdi.get_camera_id_from_username(pi_status.username)
        pi_status_response += [
                                rb.CameraStatusResponse(id=camera_id,
                                                        username=pi_status.username,
                                                        IPAddress=pi_status.IPAddress,
                                                        connectionStatus=pi_status.connectionStatus,
                                                        cameraModel=pi_status.cameraModel)
                              ]

    response.headers["Content-Range"] = str(len(pi_status_response))
    return pi_status_response


