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


from src.database.models import Camera, CameraSetupLink, Setup

from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/setup",
    tags=["setup"],
)

@router.get("")
def get_setups_api(response: Response) -> list[Setup]:
    setup = cdi.get_all_setups()
    response.headers["Content-Range"] = str(len(setup))
    return setup

@router.get("/{setup_id}")
async def read_setup(setup_id: int) -> Setup:
  return cdi.get_setup_by_id(setup_id)


@router.post("")
async def create_setup(setup_name: rb.SetupCreateRequest):
    datetime_of_creation = datetime.now(pytz.utc)
    setup_id = cdi.add_setup(setup_name=setup_name.setup_name,
                             date_created=datetime_of_creation,
                             date_last_edited=datetime_of_creation)["id"]
    return {"message": f"Setup with name {setup_name} successfully added.",
            "id": setup_id}

@router.put("/{setup_id}")
async def patch_setup(setup_id: int, patch_request: rb.SetupPatchRequest):
    message = cdi.patch_setup(setup_id, patch_request)
    return {"message": message,
            "id": setup_id}

@router.post("/{setup_id}")
def add_camera_to_setup(setup_id: int, request: rb.SetupCameraCreateRequest):
    setup_camera_id = cdi.add_camera_to_setup(setup_id, request.camera_id)["id"]
    return {"message": f"Camera with id {request.camera_id} added to setup with id {setup_id}",
            "id": setup_camera_id}


@router.get("/{setup_id}/setup-camera")
async def get_setup_cameras(setup_id: int, response: Response) -> list[CameraSetupLink]:
    with Session(engine) as session:
        stmt = select(CameraSetupLink).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(stmt).all()
        result = result if result else []
        response.headers["Content-Range"] = str(len(result))
        return result
   