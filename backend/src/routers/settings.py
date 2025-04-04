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


from src.database.models import BeamRun, Camera, CameraSettingsLink, CameraSetupLink, Experiment, Settings, Setup

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
        all_settings = []
        for camera_settings in all_camera_settings:
            settings_id = camera_settings.settings_id
            settings_entry = session.get(Settings, settings_id)

            settings = rb.TestBeamRunSettingsRequest(id=settings_entry.id,
                                                 camera_settings_id=camera_settings.id,
                                                 frame_rate=settings_entry.frame_rate,
                                                 lens_position=settings_entry.lens_position,
                                                 gain=settings_entry.gain,
                                                 is_optimal=camera_settings.is_optimal)
            all_settings += [settings]

        response.headers["Content-Range"] = str(len(all_settings))

        return all_settings


@router.put("/beam-run/test/{beam_run_id}/camera-settings/{camera_settings_id}")
def update_is_optimal(beam_run_id: int, camera_settings_id: int):
    # with Session(engine) as session:
    #     camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
    #     all_camera_settings = session.exec(camera_settings_statement).all()
    #     for camera_settings in all_camera_settings:
    #         if camera_settings.id == camera_settings_id:
    #             print("\n\n I AM HERREEE \n\n")
    #             camera_settings.is_optimal = True
    #         else:
    #             print("\n\n I AM IN THE ELSE \n\n")

    #             camera_settings.is_optimal = False
    #     session.commit()
    result = cdi.update_is_optimal_by_camera_settings_id(camera_settings_id)
    return rb.UpdateIsOptimalRequest(id=camera_settings_id)

@router.get("/beam-run/real/{beam_run_id}/camera/{camera_id}")
def get_real_settings(beam_run_id: int, camera_id: int):
    with Session(engine) as session:
        settings_statement = (select(Settings)
                              .join(CameraSettingsLink)
                              .where(CameraSettingsLink.beam_run_id == beam_run_id)
                              .where(CameraSettingsLink.camera_id == camera_id))
        # try:
        # settings_list = session.exec(settings_statement).all()
        # if len(settings_list) == 1:
        try:
            settings = session.exec(settings_statement).one()
            # return rb.RealBeamRunSettingsRequest(id=camera_id,
            #                             frame_rate=settings.frame_rate,
            #                             lens_position=settings.lens_position,
            #                                 gain=settings.gain)
            return JSONResponse(content={"id": camera_id,
                                         "has_settings": True})
        except:
            # return rb.RealBeamRunSettingsRequest(id=camera_id,
            #                                      frame_rate=None,
            #                                      lens_position=None)
            return JSONResponse(content={"id": camera_id,
                                         "has_settings": False})
        #     return settings_list
#         # else:
#         #     raise Exception("No items or multiple items found.")

# @router.get("/beam-run/real/{beam_run_id}/camera/{camera_id}")
# def get_test_settings(beam_run_id: int, camera_id: int, response: Response):
#     with Session(engine) as session:
#         camera_settings_statement = (select(CameraSettingsLink)
#                                      .where(CameraSettingsLink.beam_run_id == beam_run_id)
#                                      .where(CameraSettingsLink.camera_id == camera_id))
#         all_camera_settings = session.exec(camera_settings_statement).all()
#         all_settings = []
#         for camera_settings in all_camera_settings:
#             print("\n\n\n LOOOOOK AT MEEEEEEEEE \n\n\n")
#             settings_id = camera_settings.settings_id
#             settings_entry = session.get(Settings, settings_id)

#             settings = rb.RealBeamRunSettingsRequest(id=settings_entry.id,
#                                                  frame_rate=settings_entry.frame_rate,
#                                                  lens_position=settings_entry.lens_position,
#                                                  gain=settings_entry.gain,
#                                                  is_optimal=camera_settings.is_optimal)
#             all_settings += [settings]

#         response.headers["Content-Range"] = str(len(all_settings))

#         return all_settings

# @router.post("/beam-run/real/{beam_run_id}/camera/{camera_id}")
# def add_real_settings(beam_run_id: int, camera_id: int, settings_body: rb.RealBeamRunSettingsPost):
#     with Session(engine) as session:
#         print(f"\n\n\n I am the request body {settings_body} \n\n\n")
#         setup_camera_statement = select(CameraSetupLink).join(Setup).join(Experiment).join(BeamRun).where(BeamRun.id == beam_run_id).where(CameraSetupLink.camera_id == camera_id)
#         setup_camera = session.exec(setup_camera_statement).one()
#         camera_id = setup_camera.camera_id
#         lens_position = setup_camera.lens_position


#         previous_camera_settings_statement = (select(CameraSettingsLink)
#                                         .where(CameraSettingsLink.beam_run_id == beam_run_id)
#                                         .where(CameraSettingsLink.camera_id == camera_id))
#         all_previous_camera_settings = session.exec(previous_camera_settings_statement).all()
#         for previous_camera_settings in all_previous_camera_settings:
#             session.delete(previous_camera_settings)
#         session.commit()
#         settings_id = cdi.add_settings(settings_body.frame_rate, lens_position, settings_body.gain)["id"]
#         camera_settings_id = cdi.add_camera_settings_link_with_beam_run(camera_id, settings_id, beam_run_id)["id"]
#         return {"id": camera_settings_id}

        
    
# @router.put("/beam-run/real/{beam_run_id}/camera/{camera_id}")
# def get_real_settings(beam_run_id: int, camera_id: int, put_settings_body: rb.RealBeamRunSettingsPut):
#     with Session(engine) as session:
#         camera_settings_statement = (select(CameraSettingsLink)
#                                      .where(CameraSettingsLink.beam_run_id == beam_run_id)
#                                      .where(CameraSettingsLink.camera_id == camera_id))
#         # try:
#         camera_settings = session.exec(camera_settings_statement).one()
#         setup_camera_statement = select(CameraSetupLink).join(Setup).join(Experiment).join(BeamRun).where(BeamRun.id == beam_run_id).where(CameraSetupLink.camera_id == camera_id)
#         setup_camera = session.exec(setup_camera_statement).one()
#         lens_position = setup_camera.lens_position
#         settings_id = cdi.add_settings(put_settings_body.frame_rate, lens_position, put_settings_body.gain)["id"]
#         camera_settings.settings_id = settings_id
#         session.commit()
#         return rb.RealBeamRunSettingsRequest(id=camera_id,
#                                          frame_rate=put_settings_body.frame_rate,
#                                          lens_position=lens_position,
#                                          gain=put_settings_body.gain)
#         # except:
#         #     return None

@router.get("/{settings_id}")
def get_settings_by_id_api(settings_id: int):
    settings = cdi.get_settings_by_id(settings_id)
    return settings