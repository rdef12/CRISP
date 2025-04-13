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


from src.database.models import Camera, CameraAnalysis, CameraAnalysisPlot, CameraSettingsLink, ColourChannelEnum

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

        for remnant_camera_analysis in remnant_camera_analyses:
            remnant_camera_analysis_plots_statement = (select(CameraAnalysisPlot)
                                                       .where(CameraAnalysisPlot.camera_analysis_id == remnant_camera_analysis.id))
            remnant_camera_analysis_plots = session.exec(remnant_camera_analysis_plots_statement).all()
            for remnant_camera_analysis_plot in remnant_camera_analysis_plots:
                session.delete(remnant_camera_analysis_plot)
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
        if camera_analysis.average_image is not None:
            unpickled_image = pickle.loads(camera_analysis.average_image)
            unpickled_image = unpickled_image.astype(np.uint8)

            colour_channel = camera_analysis.colour_channel
            print(f"\n\n\n COLOUR CHSANNNERL: {colour_channel}")
            print(f"unpickeled image {unpickled_image.shape}")
            skeleton_image = np.zeros((unpickled_image.shape[0], unpickled_image.shape[1], 3), dtype=np.uint8)
            print("\n\n\n\n\n\n\n I GOT HERE \n\n\n\n")
            if colour_channel == ColourChannelEnum.RED:
                skeleton_image[:,:,0] = 0 #blue channel
                skeleton_image[:,:,1] = 0 #green channel
                skeleton_image[:,:,2] = unpickled_image #red channel
                print("I AT LEAST GOT HERE")
            elif colour_channel == ColourChannelEnum.GREEN:
                print("IN GREEEN \n\n")
                
                skeleton_image[:,:,0] = 0 #blue channel
                skeleton_image[:,:,1] = unpickled_image #green channel
                skeleton_image[:,:,2] = 0 #red channel

            elif colour_channel == ColourChannelEnum.BLUE:
                print("INBLUER \n\n")

                skeleton_image[:,:,0] = unpickled_image #blue channel
                skeleton_image[:,:,1] = 0 #green channel
                skeleton_image[:,:,2] = 0 #red channel

            else:
                print("I ENDED UP HERE???? \n\n")
                skeleton_image = cv2.cvtColor(unpickled_image, cv2.COLOR_GRAY2BGR)

            # pil_image = Image.fromarray(unpickled_image)
            success, encoded_image = cv2.imencode('.jpg', skeleton_image)

            if success:
                image_bytes = encoded_image.tobytes()
                averaged_photo = base64.b64encode(image_bytes).decode("utf-8")
            else:
                raise ValueError("Could not encode image")

        return rb.CameraAnalysisGetReponse(id=camera_id,
                                           cameraSettingsId=camera_analysis.camera_settings_id,
                                           colourChannel=camera_analysis.colour_channel,
                                           averageImage=averaged_photo,
                                           beamAngle=camera_analysis.beam_angle,
                                           beamAngleUncertainty=camera_analysis.unc_beam_angle,
                                           braggPeakPixel=camera_analysis.bragg_peak_pixel,
                                           braggPeakPixelUncertainty=camera_analysis.unc_bragg_peak_pixel,
                                           )

@router.delete("/beam-run/{beam_run_id}/camera/{camera_id}")
def delete_camera_analysis(beam_run_id: int, camera_id: int):
    with Session(engine) as session:
        remnant_camera_analyses_statement = (select(CameraAnalysis)
                                     .join(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        remnant_camera_analyses = session.exec(remnant_camera_analyses_statement).all()

        for remnant_camera_analysis in remnant_camera_analyses:
            remnant_camera_analysis_plots_statement = (select(CameraAnalysisPlot)
                                                       .where(CameraAnalysisPlot.camera_analysis_id == remnant_camera_analysis.id))
            remnant_camera_analysis_plots = session.exec(remnant_camera_analysis_plots_statement).all()
            for remnant_camera_analysis_plot in remnant_camera_analysis_plots:
                session.delete(remnant_camera_analysis_plot)
            session.delete(remnant_camera_analysis)
        session.commit()
    return


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
    