from datetime import datetime
from io import BytesIO
import pickle
from fastapi import HTTPException, Response, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.single_camera_analysis import get_beam_angle_and_bragg_peak_pixel
from src.image_processing import average_pixel_over_multiple_images
from src.database.database import engine
from PIL import Image


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb


from src.database.models import Camera, CameraAnalysis, CameraSettingsLink

from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/camera-analysis",
    tags=["camera-analysis"],
)

@router.post("/beam-run/{beam_run_id}/camera/{camera_id}")
def create_camera_analysis(beam_run_id: int, camera_id: int, payload: rb.CameraAnalysisPostPayload):
    colour_channel = payload.colour_channel
    with Session(engine) as session:
        remnant_camera_analyses_statement = (select(CameraAnalysis)
                                     .join(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        remnant_camera_analyses = session.exec(remnant_camera_analyses_statement).all()
        if len(remnant_camera_analyses) > 0:
            for remnant_camera_analysis in remnant_camera_analyses:
                session.delete(remnant_camera_analysis)
            session.commit()
        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        camera_settings = session.exec(camera_settings_statement).one()
        camera_settings_id = camera_settings.id

        camera_analysis_id = cdi.add_camera_analysis(camera_settings_id, colour_channel)["id"]
        average_pixel_over_multiple_images(camera_analysis_id)
        results = get_beam_angle_and_bragg_peak_pixel(camera_analysis_id)
        cdi.update_beam_angle(camera_analysis_id, float(results["beam_angle"]))
        cdi.update_unc_beam_angle(camera_analysis_id, float(results["beam_angle_error"]))
        cdi.update_bragg_peak_pixel(camera_analysis_id, [float(x) for x in results["bragg_peak_pixel"].flatten()])
        cdi.update_unc_bragg_peak_pixel(camera_analysis_id, [float(x) for x in results["bragg_peak_pixel_error"].flatten()])
        cdi.update_plots(camera_analysis_id, results["plot_byte_strings"])
    return rb.CameraAnalysisPostResponse(id=camera_analysis_id)

@router.get("/beam-run/{beam_run_id}/camera/{camera_id}")
def get_camera_analysis(beam_run_id: int, camera_id: int):
    with Session(engine) as session:
        camera_analysis_statement = (select(CameraAnalysis)
                                     .join(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        try:
            camera_analysis = session.exec(camera_analysis_statement).one()
        except:
            return rb.CameraAnalysisGetReponse(id=camera_id)
        unpickled_image = pickle.loads(camera_analysis.average_image)
        unpickled_image = unpickled_image.astype(np.uint8)
        pil_image = Image.fromarray(unpickled_image)
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()
        averaged_photo = base64.b64encode(image_bytes).decode("utf-8")
        unpickled_plots = pickle.loads(camera_analysis.plots)
        plots = list(unpickled_plots.values())
                
        return rb.CameraAnalysisGetReponse(id=camera_id,
                                           cameraSettingsId=camera_analysis.camera_settings_id,
                                           colourChannel=camera_analysis.colour_channel,
                                           averageImage=averaged_photo,
                                           beamAngle=camera_analysis.beam_angle,
                                           beamAngleUncertainty=camera_analysis.unc_beam_angle,
                                           braggPeakPixel=camera_analysis.bragg_peak_pixel,
                                           braggPeakPixelUncertainty=camera_analysis.unc_bragg_peak_pixel,
                                           plots=plots)

# @router.get("/plots/beam-run/{beam_run_id}/camera/{camera_id}")
# def get_beam_run_plots(beam_run_id: int, camera_id: int):
#     with Session(engine) as session:
#         camera_analysis_statement = (select(CameraAnalysis)
#                                      .join(CameraSettingsLink)
#                                      .where(CameraSettingsLink.beam_run_id == beam_run_id)
#                                      .where(CameraSettingsLink.camera_id == camera_id))
#         try:
#             camera_analysis = session.exec(camera_analysis_statement).one()
#         except:
#             return rb.Camera(id=camera_id)

#         results = get_beam_angle_and_bragg_peak_pixel(camera_analysis.id)
    