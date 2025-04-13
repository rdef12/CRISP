from sqlmodel import Session, select, PickleType
from sqlalchemy.orm.exc import NoResultFound

from src.database.database import engine
from src.database.models import CameraAnalysis, CameraSettingsLink
import numpy as np
from typing import Literal
import pickle

# Create
def add_camera_analysis(camera_settings_id: int,
                        colour_channel: Literal["red", "green", "blue", "grey", "gray"]):
    try:
        camera_analysis = CameraAnalysis(camera_settings_id=camera_settings_id,
                                         colour_channel=colour_channel)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(camera_analysis)
        session.commit()
        return {"message": f"Camera analysis added to beam run with camera settings id {camera_settings_id}.",
                "id": camera_analysis.id}
       
# Read     
def get_camera_analysis_by_id(camera_analysis_id: int) -> CameraAnalysis:
    with Session(engine) as session:
        return session.get(CameraAnalysis, camera_analysis_id)
    
def get_camera_settings_link_id_by_camera_analysis_id(camera_analysis_id: int) -> int:
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
        result = session.exec(statement).one()
        if result:
            return result.camera_settings_id
        else:
            raise ValueError(f"Camera analysis with id {camera_analysis_id} not found.")

def get_average_image(camera_analysis_id: int) -> np.ndarray:
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
        result = session.exec(statement).one()
        if result:
            return pickle.loads(result.average_image)
        else:
            raise ValueError(f"Camera analysis with id {camera_analysis_id} not found.")

def get_colour_channel(camera_analysis_id: int) -> str:
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
        result = session.exec(statement).one()
        if result:
            return result.colour_channel.value
        else:
            raise ValueError(f"Camera analysis with id {camera_analysis_id} not found.")

def get_beam_angle(camera_analysis_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
        result = session.exec(statement).one()
        if result:
            return result.beam_angle
        else:
            raise ValueError(f"Camera analysis with id {camera_analysis_id} not found.")

def get_unc_beam_angle(camera_analysis_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
        result = session.exec(statement).one()
        if result:
            return result.unc_beam_angle
        else:
            raise ValueError(f"Camera analysis with id {camera_analysis_id} not found.")

def get_bragg_peak_pixel(camera_analysis_id: int) -> list:
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
        result = session.exec(statement).one()
        if result:
            return result.bragg_peak_pixel
        else:
            raise ValueError(f"Camera analysis with id {camera_analysis_id} not found.")

def get_unc_bragg_peak_pixel(camera_analysis_id: int) -> list:
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
        result = session.exec(statement).one()
        if result:
            return result.unc_bragg_peak_pixel
        else:
            raise ValueError(f"Camera analysis with id {camera_analysis_id} not found.")


def get_camera_analysis_id_by_camera_settings(camera_settings: CameraSettingsLink):
    with Session(engine) as session:
        statement = select(CameraAnalysis).where(CameraAnalysis.camera_settings_id == camera_settings.id)
        camera_analysis = session.exec(statement).one()
        return camera_analysis.id

def get_camera_analysis_ids_by_camera_settings_list(camera_settings_list: list[CameraSettingsLink]):
    camera_analysis_ids = []
    for camera_settings in camera_settings_list:
        camera_analysis_id = get_camera_analysis_id_by_camera_settings(camera_settings)
        camera_analysis_ids += [camera_analysis_id]
    return camera_analysis_ids


# Update
def update_average_image(camera_analysis_id: int, average_image: PickleType):
    try:
        with Session(engine) as session:
            statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
            camera_analysis = session.exec(statement).one()
            camera_analysis.average_image = average_image
            session.commit()
            return {"message": f"Average image updated for analysis with camara analysis id = {camera_analysis_id}."}
    except NoResultFound:
        raise ValueError(f"No camera analysis found with camara analysis id = {camera_analysis_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_beam_angle(camera_analysis_id: int, beam_angle: float):
    try:
        with Session(engine) as session:
            statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
            camera_analysis = session.exec(statement).one()
            camera_analysis.beam_angle = beam_angle
            session.commit()
            return {"message": f"Beam angle updated for analysis with camera analysis id = {camera_analysis_id}."}
    except NoResultFound:
        raise ValueError(f"No camera analysis found with camera analysis id = {camera_analysis_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_unc_beam_angle(camera_analysis_id: int, unc_beam_angle: float):
    try:
        with Session(engine) as session:
            statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
            camera_analysis = session.exec(statement).one()
            camera_analysis.unc_beam_angle = unc_beam_angle
            session.commit()
            return {"message": f"Uncertainty in beam angle updated for analysis with camera analysis id = {camera_analysis_id}."}
    except NoResultFound:
        raise ValueError(f"No camera analysis found with camera analysis id = {camera_analysis_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_bragg_peak_pixel(camera_analysis_id: int, bragg_peak_pixel: list[float]):
    try:
        with Session(engine) as session:
            statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
            camera_analysis = session.exec(statement).one()
            camera_analysis.bragg_peak_pixel = bragg_peak_pixel
            session.commit()
            return {"message": f"Bragg peak pixel updated for analysis with camera analysis id = {camera_analysis_id}."}
    except NoResultFound:
        raise ValueError(f"No camera analysis found with camera analysis id = {camera_analysis_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_unc_bragg_peak_pixel(camera_analysis_id: int, unc_bragg_peak_pixel: list[float]):
    try:
        with Session(engine) as session:
            statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
            camera_analysis = session.exec(statement).one()
            camera_analysis.unc_bragg_peak_pixel = unc_bragg_peak_pixel
            session.commit()
            return {"message": f"Uncertainty in Bragg peak pixel updated for analysis with camera analysis id = {camera_analysis_id}."}
    except NoResultFound:
        raise ValueError(f"No camera analysis found with camera analysis id = {camera_analysis_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_range(camera_analysis_id: int, range: float):
    try:
        with Session(engine) as session:
            statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
            camera_analysis = session.exec(statement).one()
            camera_analysis.range = range
            session.commit()
            return {"message": f"Range updated for analysis with camera analysis id = {camera_analysis_id}."}
    except NoResultFound:
        raise ValueError(f"No camera analysis found with camera analysis id = {camera_analysis_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_range_uncertainty(camera_analysis_id: int, range_uncertainty: float):
    try:
        with Session(engine) as session:
            statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
            camera_analysis = session.exec(statement).one()
            camera_analysis.range_uncertainty = range_uncertainty
            session.commit()
            return {"message": f"Range uncertainty updated for analysis with camera analysis id = {camera_analysis_id}."}
    except NoResultFound:
        raise ValueError(f"No camera analysis found with camera analysis id = {camera_analysis_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# def update_plots(camera_analysis_id: int, plots: bytes):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraAnalysis).where(CameraAnalysis.id == camera_analysis_id)
#             camera_analysis = session.exec(statement).one()
#             camera_analysis.plots = plots
#             session.commit()
#             return {"message": f"Plots updated for analysis with camera analysis id = {camera_analysis_id}."}
#     except NoResultFound:
#         raise ValueError(f"No camera analysis found with camera analysis id = {camera_analysis_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")
