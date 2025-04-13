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


from src.database.models import BeamRun, Camera, CameraAnalysis, CameraSettingsLink, CameraSetupLink, Experiment, OpticalAxisEnum, Setup

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

@router.get("/{optical_axis}/beam-run/{beam_run_id}")
def get_cameras_on_optical_axis_with_complete_analysis(optical_axis: OpticalAxisEnum, beam_run_id):
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        all_camera_settings = session.exec(camera_settings_statement).all()
        
        complete_camera_settings = []
        for camera_settings in all_camera_settings:
            camera_analysis_statement = select(CameraAnalysis).where(CameraAnalysis.camera_settings_id == camera_settings.id)
            camera_analysis = session.exec(camera_analysis_statement).one()
            bragg_peak_pixel = camera_analysis.bragg_peak_pixel
            unc_bragg_peak_pixel = camera_analysis.unc_bragg_peak_pixel
            beam_angle = camera_analysis.beam_angle
            unc_beam_angle = camera_analysis.unc_beam_angle
            analysis_is_complete = (bragg_peak_pixel is not None
                                    and unc_bragg_peak_pixel is not None
                                    and beam_angle is not None
                                    and unc_beam_angle is not None)
            if analysis_is_complete:
                complete_camera_settings += [camera_settings]
        
        experiment = session.get(Experiment, beam_run.experiment_id)
        setup = session.get(Setup, experiment.setup_id)
        setup_camera_statement = None

        # if optical_axis == OpticalAxisEnum.x:
        #     setup_camera_statement = select(SetupCamera).where()
        # statement = (select(CameraSettingsLink, Camera)
        #              .join(CameraAnalysis)
        #              .join(BeamRun)
        #              .join(Experiment)
        #              .join(Experiment)
        #              .join(Setup)
        #              .join(CameraSetupLink)
        #              .where(CameraSetupLink.optical_axis == optical_axis)
        #              .where(CameraAnalysis.))