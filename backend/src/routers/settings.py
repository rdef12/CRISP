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


from src.database.models import Camera, CameraSettingsLink, Settings

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
def add_scintillator_edge_settings(setup_camera_id: int, settings_body: rb.SettingsCreateRequest):
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
    settings = cdi.get_settings_by_setup_camera_id_scintillator_edges(setup_camera_id)
    print(f"\n\n\n\n\n {settings} \n\n\n\n\n")
    return settings

@router.put("/scintillator-edges/{setup_camera_id}")
def update_scintillator_edges_camera_settings(setup_camera_id: int, settings_body: rb.SettingsCreateRequest):
    settings_id = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)
    return {"id": settings_id}

@router.post("/distortion-calibration/{setup_camera_id}")
def add_distortion_calibration_settings(setup_camera_id: int, settings_body: rb.SettingsCreateRequest):
    settings = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)
    settings_id = settings["id"]

    setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    camera_id = setup_camera.camera_id

    camera_settings_link = cdi.add_camera_settings_link(camera_id, settings_id)
    camera_settings_id = camera_settings_link["id"]

    cdi.update_distortion_calibration_camera_settings_id(setup_camera_id, camera_settings_id)
    return {"id": camera_settings_id}

@router.get("/distortion-calibration/{setup_camera_id}")
def get_distortion_calibration_settings(setup_camera_id: int, response: Response):
    settings = cdi.get_settings_by_setup_camera_id_distortion_calibration(setup_camera_id)
    return settings

@router.put("/scintillator-edges/{setup_camera_id}") #TODO Is function this right??
def update_scintillator_edges_camera_settings(setup_camera_id: int, settings_body: rb.SettingsCreateRequest):
    settings_id = cdi.add_settings(settings_body.frame_rate, settings_body.lens_position, settings_body.gain)
    return {"id": settings_id}

@router.get("/beam-run/test/{beam_run_id}/camera/{camera_id}")
def get_test_settings(beam_run_id: int, camera_id: int, response: Response):
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        all_camera_settings = session.exec(camera_settings_statement).all()
        print(f"\n\n\n all camera settings - \n {all_camera_settings} \n\n")
        all_settings = []
        for camera_settings in all_camera_settings:
            settings_id = camera_settings.settings_id
            settings = session.get(Settings, settings_id)
            all_settings += [settings]

        response.headers["Content-Range"] = str(len(all_settings))

        return all_settings


@router.get("/{settings_id}")
def get_settings_by_id_api(settings_id: int):
    settings = cdi.get_settings_by_id(settings_id)
    return settings