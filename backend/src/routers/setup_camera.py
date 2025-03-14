from fastapi import Response, APIRouter
from pydantic import BaseModel
from sqlmodel import Session, select
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *

from src.database.models import Camera, CameraSetupLink, Setup

from src.database.CRUD import CRISP_database_interaction as cdi
from src.classes.JSON_request_bodies import request_bodies as rb

router = APIRouter(
    prefix="/setup-camera",
    tags=["setup-camera"],
)

@router.get("/{setup_id}")
def get_camera_setups(setup_id: int, response: Response) -> list[CameraSetupLink]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.setup_id == setup_id)
        results = session.exec(statement).all()
        results = results if results else []
        response.headers["Content-Range"] = str(len(results))
        return results

@router.get("/calibration/{setup_camera_id}")
async def read_setup_camera(setup_camera_id: int) -> CameraSetupLink:
    setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    return setup_camera


# @router.get("/{setup_camera_id}")
# async def read_setup_camera(setup_camera_id: int) -> Setup:
#     setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
#     print(f"\n\n\n\n\n You called the right one {setup_camera} \n\n\n\n")
#     return setup_camera

@router.patch("/{setup_camera_id}")
async def patch_setup_camera(setup_camera_id: int, patch_request: rb.SetupCameraPatchRequest):
    cdi.patch_setup_camera(setup_camera_id, patch_request)
    return
    




