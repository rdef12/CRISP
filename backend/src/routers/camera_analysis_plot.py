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
    prefix="/camera-analysis-plots",
    tags=["camera-analysis-plots"],
)

@router.get("/beam-run/{beam_run_id}/camera/{camera_id}")
def get_cameras_plots(beam_run_id: int, camera_id: int, response: Response):
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                                    .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                    .where(CameraSettingsLink.camera_id == camera_id))
        camera_settings = session.exec(camera_settings_statement).one()
        camera_settings_id = camera_settings.id
        camera_analysis_statement = select(CameraAnalysis).where(CameraAnalysis.camera_settings_id == camera_settings_id)
        camera_analysis = session.exec(camera_analysis_statement).one()
        camera_analysis_id = camera_analysis.id
        camera_analysis_plots_statement = select(CameraAnalysisPlot).where(CameraAnalysisPlot.camera_analysis_id == camera_analysis_id)
        plots = session.exec(camera_analysis_plots_statement).all()
        plots = sorted(plots, key=lambda plot: int(plot.id))
        plot_responses = []
        for plot in plots:
            plot_base_64 = base64.b64encode(plot.plot_figure).decode("utf-8")
            plot_response = rb.CameraAnalysisPlotGetResponse(id=plot.id,
                                                             plot_type=plot.plot_type,
                                                             plot_figure=plot_base_64,
                                                             figure_format=plot.figure_format,
                                                             parameter_labels=plot.parameter_labels,
                                                             parameter_values=plot.parameter_values,
                                                             parameter_uncertainties=plot.parameter_uncertainties,
                                                             chi_squared=plot.chi_squared,
                                                             number_of_data_points=plot.number_of_data_points,
                                                             description=plot.description,)
            plot_responses += [plot_response]
        response.headers["Content-Range"] = str(len(plot_responses))
        return plot_responses

