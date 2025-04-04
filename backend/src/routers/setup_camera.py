from fastapi import Response, APIRouter
from pydantic import BaseModel
from sqlmodel import Session, select
from src.distortion_correction import save_distortion_calibration_to_database
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *

from src.database.models import Camera, CameraSetupLink, Photo, Settings, Setup

from src.database.CRUD import CRISP_database_interaction as cdi
from src.classes.JSON_request_bodies import request_bodies as rb

router = APIRouter(
    prefix="/setup-camera",
    tags=["setup-camera"],
)

@router.get("/{setup_id}")
def get_camera_setups(setup_id: int, response: Response) -> list[rb.SetupCameraGetRequest]:
    camera_setups = cdi.get_setup_cameras_by_setup_id(setup_id)
    response_body = []
    for camera_setup in camera_setups:
        camera = cdi.get_camera_by_id(camera_setup.camera_id)
        response_body_element = rb.SetupCameraGetRequest(id=camera_setup.id,
                                                         camera_id=camera_setup.camera_id,
                                                         setup_id=camera_setup.setup_id,
                                                         camera=camera)
        response_body += [response_body_element]
    response.headers["Content-Range"] = str(len(response_body))
    return response_body

# @router.get("/{setup_camera_id}")
# async def read_setup_camera(setup_camera_id: int) -> CameraSetupLink:
#     setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
#     return setup_camera

@router.get("/calibration/{setup_camera_id}")
async def read_setup_camera(setup_camera_id: int) -> CameraSetupLink:
    setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    print(f"\n\n\n\n\nHELLLLLLLLLLLOOOOOOO: {setup_camera} \n\n\n\n\n")
    return setup_camera


@router.get("/scintillator-edges/{setup_camera_id}")
async def read_setup_camera(setup_camera_id: int) -> rb.SetupCameraScintillatorEdgeRequest:
    setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    settings = cdi.get_settings_by_setup_camera_id_scintillator_edges(setup_camera_id)
    print(f"\n\n Settings: {settings} \n\n")

    setup_camera_body = rb.SetupCameraScintillatorEdgeRequest(id=setup_camera.id,
                                                              camera_id=setup_camera.id,
                                                              setup_id=setup_camera.setup_id,
                                                              scintillator_edges_photo_camera_settings_id=setup_camera.scintillator_edges_photo_camera_settings_id,
                                                              settings=settings,
                                                              horizontal_start=setup_camera.horizontal_scintillator_start,
                                                              horizontal_end=setup_camera.horizontal_scintillator_end,
                                                              vertical_start=setup_camera.vertical_scintillator_start,
                                                              vertical_end=setup_camera.vertical_scintillator_end)
    return setup_camera_body

@router.put("/scintillator-edges/{setup_camera_id}") #TODO why am i not using the standard put here?
async def read_setup_camera(setup_camera_id: int, settings_body: rb.SetupCameraScintillatorEdgeRequest):
    if settings_body.settings is not None:
        result = cdi.add_settings(settings_body.settings.frame_rate, settings_body.settings.lens_position, settings_body.settings.gain)
        settings_id = result["id"]

        setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
        camera_id = setup_camera.camera_id

        camera_settings_link = cdi.add_camera_settings_link(camera_id, settings_id)
        camera_settings_id = camera_settings_link["id"]

        cdi.update_scintillator_edges_camera_settings_id(setup_camera_id, camera_settings_id)
    if settings_body.horizontal_start is not None:
        cdi.update_horizontal_scintillator_scintillator_start(setup_camera_id, settings_body.horizontal_start)
    if settings_body.horizontal_end is not None:
        cdi.update_horizontal_scintillator_scintillator_end(setup_camera_id, settings_body.horizontal_end)

    if settings_body.vertical_start is not None:
        cdi.update_vertical_scintillator_scintillator_start(setup_camera_id, settings_body.vertical_start)
    if settings_body.vertical_end is not None:
        cdi.update_vertical_scintillator_scintillator_end(setup_camera_id, settings_body.vertical_end)
    return {"id": camera_settings_id}
    # setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    # settings = cdi.get_settings_by_setup_camera_id_scintillator_edges(setup_camera_id)
    # setup_camera_body = rb.SetupCameraScintillatorEdgeRequest(id=setup_camera.id,
    #                                                           camera_id=setup_camera.id,
    #                                                           setup_id=setup_camera.setup_id,
    #                                                           scintillator_edges_photo_camera_settings_id=setup_camera.scintillator_edges_photo_camera_settings_id,
    #                                                           settings=settings,
    #                                                           horizontal_scintillator_limits=setup_camera.horizontal_scintillator_limits,
    #                                                           vertical_scintillator_limits=setup_camera.vertical_scintillator_limits)
    # return setup_camera_body


@router.get("/distortion-calibration/{setup_camera_id}")
async def read_setup_camera(setup_camera_id: int) -> rb.SetupCameraDistortionCalibrationGetRequest:
    setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    settings = cdi.get_settings_by_setup_camera_id_distortion_calibration(setup_camera_id)
    print(f"\n\n Settings: {settings} \n\n")

    setup_camera_body = rb.SetupCameraDistortionCalibrationGetRequest(id=setup_camera.id,
                                                                   camera_id=setup_camera.id,
                                                                   setup_id=setup_camera.setup_id,
                                                                   distortion_calibration_camera_settings_link=setup_camera.distortion_calibration_camera_settings_link,
                                                                   settings=settings,
                                                                   do_distortion_calibration=setup_camera.do_distortion_calibration,
                                                                   distortion_calibration_pattern_size_z_dim=setup_camera.distortion_calibration_pattern_size_z_dim,
                                                                   distortion_calibration_pattern_size_non_z_dim=setup_camera.distortion_calibration_pattern_size_non_z_dim,
                                                                   distortion_calibration_pattern_type=setup_camera.distortion_calibration_pattern_type,
                                                                   distortion_calibration_pattern_spacing=setup_camera.distortion_calibration_pattern_spacing)
    return setup_camera_body #TODO maybe matrices and internals need to be able to be returned here

@router.post("/distortion-calibration/{setup_camera_id}")
async def add_distortion_calibration_settings(setup_camera_id: int, distortion_settings_body: rb.SetupCameraDistortionCalibrationPostRequest) -> rb.SetupCameraDistortionCalibrationGetRequest:
    setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
    lens_position = setup_camera.lens_position
    frame_rate = 30 #FIXED ARBITRARILY AT 30
    
    settings_id = cdi.add_settings(frame_rate, lens_position, distortion_settings_body.gain)["id"]
    camera_id = setup_camera.camera_id

    camera_settings_link = cdi.add_camera_settings_link(camera_id, settings_id)
    camera_settings_id = camera_settings_link["id"]

    cdi.update_distortion_calibration_camera_settings_id(setup_camera_id, camera_settings_id)

    cdi.update_distortion_calibration_pattern_size_z_dim(setup_camera_id, distortion_settings_body.distortion_calibration_pattern_size_z_dim)
    cdi.update_distortion_calibration_pattern_size_non_z_dim(setup_camera_id, distortion_settings_body.distortion_calibration_pattern_size_non_z_dim)
    cdi.update_distortion_calibration_pattern_type(setup_camera_id, distortion_settings_body.distortion_calibration_pattern_type)
    cdi.update_distortion_calibration_pattern_spacing(setup_camera_id, distortion_settings_body.distortion_calibration_pattern_spacing)
    response = rb.SetupCameraDistortionCalibrationGetRequest(id=setup_camera_id, camera_id=camera_id)
    return response

@router.post("/distortion-calibration/save/{setup_camera_id}")
async def add_distortion_calibration_settings(setup_camera_id: int):
    save_distortion_calibration_to_database(setup_camera_id)
    return rb.DistortionCalibrationSaveResponse(id=setup_camera_id)

@router.delete("/distortion-calibration/reset/{setup_camera_id}")
def reset_distortion_calibration(setup_camera_id: int):
    distortion_result = cdi.reset_distortion_calibration(setup_camera_id)

# @router.get("/{setup_camera_id}")
# async def read_setup_camera(setup_camera_id: int) -> Setup:
#     setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
#     print(f"\n\n\n\n\n You called the right one {setup_camera} \n\n\n\n")
#     return setup_camera

@router.patch("/{setup_camera_id}")
async def patch_setup_camera(setup_camera_id: int, patch_request: rb.SetupCameraPatchRequest):
    cdi.patch_setup_camera(setup_camera_id, patch_request)
    return


@router.put("/calibration/{setup_camera_id}")
async def patch_setup_camera(setup_camera_id: int, patch_request: rb.SetupCameraPatchRequest):
    print(f"\n\n PATCH REQUEST {patch_request} \n SETUP CAMERA ID {setup_camera_id} \n\n")
    cdi.patch_setup_camera(setup_camera_id, patch_request)
    print("\n\n I DONE A PATCH \n\n")
    return {"message": "Successfully added calibration parameters",
            "id": setup_camera_id}

@router.delete("/{setup_camera_id}")
async def delete_setup_camera(setup_camera_id: int):
    cdi.delete_setup_camera(setup_camera_id)
    return rb.SetupCameraDeleteRequest(id=setup_camera_id)

    




