from datetime import datetime
import pytz
from src.database.database import engine
from sqlmodel import Session, select, PickleType
from sqlalchemy.orm.exc import NoResultFound
import numpy as np
from typing import List, Literal
import pickle

from src.database.models import Camera, CameraSetupLink, Experiment, Setup, OpticalAxisEnum, DepthDirectionEnum
from src.classes.JSON_request_bodies import request_bodies as rb

# Create

def add_camera_to_setup(setup_id: int, camera_id:int):
    try:
        camera_setup_link = CameraSetupLink(camera_id=camera_id, setup_id=setup_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(camera_setup_link)
        session.commit()
        return {"message": f"Camera added to setup.",
                "id": camera_setup_link.id}

# Read

def get_setup_cameras_by_setup_id(setup_id: int) -> list[CameraSetupLink]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.setup_id == setup_id)
        camera_setups = session.exec(statement).all()
        return camera_setups if camera_setups else []

def get_setup_camera_by_id(id: int) -> CameraSetupLink:
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, id)
        print(f"\n\n\n\n\n THINGGGGGGG: {setup_camera} \n\n\n\n\n")
        return setup_camera

def get_cameras_in_setup(setup_id: int) -> list[Camera]:
    with Session(engine) as session:
        # statement = select(Camera).join(Setup).where(Setup.id == setup_id)
        # statement = select(Camera).where(Setup.id == setup_id)
        statement = (
                     select(Camera)
                     .join(CameraSetupLink)#, CameraSetupLink.camera_id == Camera.id)
                     .join(Setup)#, Setup.id == CameraSetupLink.setup_id)
                     .where(Setup.id == setup_id)
                    )
        cameras = session.exec(statement).all()
        print(f"\n\n\n\n Cameras - {cameras} \n\n")
        return cameras if cameras else []


def get_cameras_in_experiment(experiment_id: int) -> list[Camera]:
    with Session(engine) as session:
        statement = select(Camera).join(Experiment).where(Experiment.id == experiment_id)
        cameras = session.exec(statement).all()
        return cameras if cameras else []


# def get_far_face_calibration_photo(camera_id:int, setup_id:int) -> bytes:
#     with Session(engine) as session:
#         statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#         result = session.exec(statement).one()
#         if result:
#             return result.far_face_calibration_photo
#         else:
#             raise ValueError(f"Far face calibration photo not found for camera with id {camera_id} and setup with id {setup_id}.")


# def get_near_face_calibration_photo(camera_id:int, setup_id:int) -> bytes:
#     with Session(engine) as session:
#         statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#         result = session.exec(statement).one()
#         if result:
#             return result.near_face_calibration_photo
#         else:
#             raise ValueError(f"Near face calibration photo not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_camera_depth_direction(camera_id:int, setup_id:int) -> str:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.depth_direction.value # .value because type is enum
        else:
            raise ValueError(f"Camera's depth direction not found for camera with id {camera_id} and setup with id {setup_id}.")
        
def get_camera_optical_axis(camera_id:int, setup_id:int) -> int:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.optical_axis.value # .value because type is enum
        else:
            raise ValueError(f"Optical axis not found for camera with id {camera_id} and setup with id {setup_id}.")
       
def get_far_face_z_shift(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_z_shift
        else:
            raise ValueError(f"Far face Z shift not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_z_shift_unc(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_z_shift_unc
        else:
            raise ValueError(f"Far face Z shift uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_non_z_shift(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_non_z_shift
        else:
            raise ValueError(f"Far face non-Z shift not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_non_z_shift_unc(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_non_z_shift_unc
        else:
            raise ValueError(f"Far face non-Z shift uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_calibration_board_thickness(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_calibration_board_thickness
        else:
            raise ValueError(f"Far face calibration board thickness not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_calibration_board_thickness_unc(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_calibration_board_thickness_unc
        else:
            raise ValueError(f"Far face calibration board thickness uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_z_shift(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_z_shift
        else:
            raise ValueError(f"Near face Z shift not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_z_shift_unc(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_z_shift_unc
        else:
            raise ValueError(f"Near face Z shift uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_non_z_shift(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_non_z_shift
        else:
            raise ValueError(f"Near face non-Z shift not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_non_z_shift_unc(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_non_z_shift_unc
        else:
            raise ValueError(f"Near face non-Z shift uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_calibration_board_thickness(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_calibration_board_thickness
        else:
            raise ValueError(f"Near face calibration board thickness not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_calibration_board_thickness_unc(camera_id: int, setup_id: int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_calibration_board_thickness_unc
        else:
            raise ValueError(f"Near face calibration board thickness uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_calibration_pattern_size(camera_id:int, setup_id:int) -> tuple[int, int]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_calibration_pattern_size
        else:
            raise ValueError(f"Far face calibration pattern size not found for camera with id {camera_id} and setup with id {setup_id}.")


def get_near_face_calibration_pattern_size(camera_id:int, setup_id:int) -> tuple[int, int]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_calibration_pattern_size
        else:
            raise ValueError(f"Near face calibration pattern size not found for camera with id {camera_id} and setup with id {setup_id}.")


def get_far_face_calibration_pattern_type(camera_id:int, setup_id:int) -> str:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_calibration_pattern_type
        else:
            raise ValueError(f"Far face calibration pattern type not found for camera with id {camera_id} and setup with id {setup_id}.")


def get_near_face_calibration_pattern_type(camera_id:int, setup_id:int) -> str:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_calibration_pattern_type
        else:
            raise ValueError(f"Near face calibration pattern type not found for camera with id {camera_id} and setup with id {setup_id}.")
        
def get_far_face_calibration_spacing(camera_id:int, setup_id:int) -> List[float]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_calibration_spacing
        else:
            raise ValueError(f"Far face calibration pattern spacing not found for camera with id {camera_id} and setup with id {setup_id}.")
        
def get_near_face_calibration_spacing(camera_id:int, setup_id:int) -> List[float]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_calibration_spacing
        else:
            raise ValueError(f"Near face calibration pattern spacing not found for camera with id {camera_id} and setup with id {setup_id}.")
        
def get_far_face_calibration_spacing_unc(camera_id:int, setup_id:int) -> List[float]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_calibration_spacing_unc
        else:
            raise ValueError(f"Far face calibration pattern spacing uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_calibration_spacing_unc(camera_id:int, setup_id:int) -> List[float]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_calibration_spacing_unc
        else:
            raise ValueError(f"Near face calibration pattern spacing uncertainty not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_homography_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return pickle.loads(result.far_face_homography_matrix)
        else:
            raise ValueError(f"Homography matrix not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_homography_covariance_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return pickle.loads(result.far_face_homography_covariance_matrix)
        else:
            raise ValueError(f"Homography covariance matrix not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_homography_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return pickle.loads(result.near_face_homography_matrix)
        else:
            raise ValueError(f"Homography matrix not found for camera with id {camera_id} and setup with id {setup_id}.")


def get_near_face_homography_covariance_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return pickle.loads(result.near_face_homography_covariance_matrix)
        else:
            raise ValueError(f"Homography covariance matrix not found for camera with id {camera_id} and setup with id {setup_id}.")


def get_horizontal_scintillator_limits(camera_id:int, setup_id:int) -> tuple[int, int]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.horizontal_scintillator_limits
        else:
            raise ValueError(f"Initial horizontal ROI not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_vertical_scintillator_limits(camera_id:int, setup_id:int) -> tuple[int, int]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.vertical_scintillator_limits
        else:
            raise ValueError(f"Initial vertical ROI not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_scintillator_edges_photo_id(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.scintillator_edges_photo_id
        else:
            raise ValueError(f"Far face calibration photo not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_camera_matrix(camera_id:int, setup_id:int) -> np.ndarray:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.camera_matrix
        else:
            raise ValueError(f"Camera matrix not found for camera with id {camera_id} and setup with id {setup_id}.")
  
      
def get_distortion_coefficients(camera_id:int, setup_id:int) -> np.ndarray:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.distortion_coefficients
        else:
            raise ValueError(f"Distortion coefficients not found for camera with id {camera_id} and setup with id {setup_id}.")
        
def get_distortion_calibration_pattern_size(camera_id:int, setup_id:int) -> List[int]:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.distortion_calibration_pattern_size
        else:
            raise ValueError(f"Distortion calibration grid size not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_distortion_calibration_pattern_type(camera_id:int, setup_id:int) -> str:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.distortion_calibration_pattern_type
        else:
            raise ValueError(f"Distortion calibration pattern type not found for camera with id {camera_id} and setup with id {setup_id}.")
        
def get_distortion_calibration_pattern_spacing(camera_id:int, setup_id:int) -> float:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.distortion_calibration_pattern_spacing
        else:
            raise ValueError(f"Distortion calibration spacing type not found for camera with id {camera_id} and setup with id {setup_id}.")

# Update

def update_far_face_camera_settings_link(camera_id:int, setup_id:int, camera_settings_id:int):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.far_face_calibration_photo_camera_settings_link = camera_settings_id
            session.commit()
            return {"message": f"Camera settings link updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# def update_far_face_calibration_photo(camera_id:int, setup_id:int, far_face_calibration_photo_bytes: bytes):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#             result = session.exec(statement).one()
#             result.far_face_calibration_photo = far_face_calibration_photo_bytes
#             session.commit()
#             return {"message": f"Far face calibration photo updated for camera with id {camera_id} and setup with id {setup_id}."}
#     except NoResultFound:
#         raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_camera_settings_link(camera_id:int, setup_id:int, camera_settings_id:int):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.near_face_calibration_photo_camera_settings_link = camera_settings_id
            session.commit()
            return {"message": f"Camera settings link updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

# def update_near_face_calibration_photo(camera_id:int, setup_id:int, near_face_calibration_photo_bytes: bytes):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#             result = session.exec(statement).one()
#             result.near_face_calibration_photo = near_face_calibration_photo_bytes
#             session.commit()
#             return {"message": f"Near face calibration photo updated for camera with id {camera_id} and setup with id {setup_id}."}
#     except NoResultFound:
#         raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")

def update_far_face_z_shift(camera_id: int, setup_id: int, z_shift: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.far_face_z_shift = z_shift
            session.commit()
            return {"message": f"Far face Z shift updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_far_face_z_shift_unc(camera_id: int, setup_id: int, z_shift_unc: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.far_face_z_shift_unc = z_shift_unc
            session.commit()
            return {"message": f"Far face Z shift uncertainty updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_far_face_non_z_shift(camera_id: int, setup_id: int, non_z_shift: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.far_face_non_z_shift = non_z_shift
            session.commit()
            return {"message": f"Far face non-Z shift updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_far_face_non_z_shift_unc(camera_id: int, setup_id: int, non_z_shift_unc: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.far_face_non_z_shift_unc = non_z_shift_unc
            session.commit()
            return {"message": f"Far face non-Z shift uncertainty updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_far_face_calibration_board_thickness(camera_id: int, setup_id: int, thickness: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.far_face_calibration_board_thickness = thickness
            session.commit()
            return {"message": f"Far face calibration board thickness updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_far_face_calibration_board_thickness_unc(camera_id: int, setup_id: int, thickness_unc: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.far_face_calibration_board_thickness_unc = thickness_unc
            session.commit()
            return {"message": f"Far face calibration board thickness uncertainty updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
    
def update_near_face_z_shift(camera_id: int, setup_id: int, z_shift: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.near_face_z_shift = z_shift
            session.commit()
            return {"message": f"Near face Z shift updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_z_shift_unc(camera_id: int, setup_id: int, z_shift_unc: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.near_face_z_shift_unc = z_shift_unc
            session.commit()
            return {"message": f"Near face Z shift uncertainty updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_non_z_shift(camera_id: int, setup_id: int, non_z_shift: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.near_face_non_z_shift = non_z_shift
            session.commit()
            return {"message": f"Near face non-Z shift updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_non_z_shift_unc(camera_id: int, setup_id: int, non_z_shift_unc: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.near_face_non_z_shift_unc = non_z_shift_unc
            session.commit()
            return {"message": f"Near face non-Z shift uncertainty updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_calibration_board_thickness(camera_id: int, setup_id: int, thickness: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.near_face_calibration_board_thickness = thickness
            session.commit()
            return {"message": f"Near face calibration board thickness updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_calibration_board_thickness_unc(camera_id: int, setup_id: int, thickness_unc: float):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.near_face_calibration_board_thickness_unc = thickness_unc
            session.commit()
            return {"message": f"Near face calibration board thickness uncertainty updated for camera {camera_id} and setup {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_camera_optical_axis(camera_id:int, setup_id:int, camera_optical_axis: Literal["x", "y", "z"]):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.optical_axis = camera_optical_axis
            session.commit()
            return {"message": f"Optical axis updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
    
def update_camera_depth_direction(camera_id:int, setup_id:int, camera_depth_direction: Literal[1, -1]):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.depth_direction = camera_depth_direction
            session.commit()
            return {"message": f"Depth direction updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_far_face_calibration_pattern_size(camera_id:int, setup_id:int, far_face_calibration_pattern_size: tuple[int, int]):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.far_face_calibration_pattern_size = far_face_calibration_pattern_size
            session.commit()
            return {"message": f"Far face calibration pattern size updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_near_face_calibration_pattern_size(camera_id:int, setup_id:int, near_face_calibration_pattern_size: tuple[int, int]):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.near_face_calibration_pattern_size = near_face_calibration_pattern_size
            session.commit()
            return {"message": f"Near face calibration pattern size updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_far_face_calibration_pattern_type(camera_id:int, setup_id:int, far_face_calibration_pattern_type: str = "chessboard"):
    ### This should be changed to accept other types but will need a list of possible or something ###
    ### Could maybe do with removing the option for now? ###
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.far_face_calibration_pattern_type = far_face_calibration_pattern_type
            session.commit()
            return {"message": f"Far face calibration pattern type updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_near_face_calibration_pattern_type(camera_id:int, setup_id:int, near_face_calibration_pattern_type: str = "chessboard"):
    ### This should be changed to accept other types but will need a list of possible or something ###
    ### Could maybe do with removing the option for now? ###
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.near_face_calibration_pattern_type = near_face_calibration_pattern_type
            session.commit()
            return {"message": f"Near face calibration pattern type updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_far_face_homography_matrix(camera_id:int, setup_id:int, far_face_homography_matrix: PickleType):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.far_face_homography_matrix = far_face_homography_matrix
            session.commit()
            return {"message": f"Far face homography matrix updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_far_face_homography_covariance_matrix(camera_id:int, setup_id:int, far_face_homography_covariance_matrix: PickleType):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.far_face_homography_covariance_matrix = far_face_homography_covariance_matrix
            session.commit()
            return {"message": f"Far face homography covariance matrix updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_homography_matrix(camera_id:int, setup_id:int, near_face_homography_matrix: PickleType):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.near_face_homography_matrix = near_face_homography_matrix
            session.commit()
            return {"message": f"Near face homography matrix updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

def update_near_face_homography_covariance_matrix(camera_id:int, setup_id:int, near_face_homography_covariance_matrix: PickleType):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.near_face_homography_covariance_matrix = near_face_homography_covariance_matrix
            session.commit()
            return {"message": f"Near face homography covariance matrix updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_distortion_calibration_camera_settings_id(setup_camera_id: int, distortion_calibration_photo_camera_settings_id: int):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.id == setup_camera_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.distortion_calibration_camera_settings_link = distortion_calibration_photo_camera_settings_id
            session.commit()
            return {"message": f"Camera settings link updated for setup camera link with id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup camera link with id {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_scintillator_edges_camera_settings_id(setup_camera_id: int, scintillator_edges_photo_camera_settings_id: int):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.id == setup_camera_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.scintillator_edges_photo_camera_settings_id = scintillator_edges_photo_camera_settings_id
            session.commit()
            return {"message": f"Camera settings link updated for setup camera link with id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup camera link with id {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

def update_horizontal_scintillator_scintillator_start(setup_camera_id: int, horizontal_scintillator_start: int):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.horizontal_scintillator_start = horizontal_scintillator_start
            session.commit()
            return {"message": f"Horizontal scintillator start updated for setup camera with id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for id: {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_horizontal_scintillator_scintillator_end(setup_camera_id: int, horizontal_scintillator_end: int):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.horizontal_scintillator_end = horizontal_scintillator_end
            session.commit()
            return {"message": f"Horizontal scintillator end updated for setup camera with id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for id: {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_vertical_scintillator_scintillator_start(setup_camera_id: int, vertical_scintillator_start: int):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.vertical_scintillator_start = vertical_scintillator_start
            session.commit()
            return {"message": f"Vertical scintillator start updated for setup camera with id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for id: {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_vertical_scintillator_scintillator_end(setup_camera_id: int, vertical_scintillator_end: int):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.vertical_scintillator_end = vertical_scintillator_end
            session.commit()
            return {"message": f"Vertical scintillator end updated for setup camera with id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for id: {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

# def update_vertical_scintillator_limits(camera_id:int, setup_id:int, vertical_scintillator_limits: tuple[int, int]):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#             result = session.exec(statement).one()
#             result.vertical_scintillator_limits = vertical_scintillator_limits
#             session.commit()
#             return {"message": f"Vertical scintillator limits updated for camera with id {camera_id} and setup with id {setup_id}."}
#     except NoResultFound:
#         raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")
    
def patch_setup_camera(setup_camera_id: int, patch: rb.SetupCameraPatchRequest):
    try:
        print(f"\n\n\nPATCH: {patch} \n\n\n")
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.id == setup_camera_id)
            # result = session.exec(statement).one()
            result = session.get(CameraSetupLink, setup_camera_id)
        # Far Face
            if patch.far_face_calibration_pattern_size is not None:
                result.far_face_calibration_pattern_size = patch.far_face_calibration_pattern_size
            if patch.far_face_calibration_pattern_type is not None:
                result.far_face_calibration_pattern_type = patch.far_face_calibration_pattern_type
            if patch.far_face_calibration_spacing is not None:
                result.far_face_calibration_spacing = patch.far_face_calibration_spacing
            if patch.far_face_calibration_spacing_unc is not None:
                result.far_face_calibration_spacing_unc = patch.far_face_calibration_spacing_unc
            if patch.far_face_calibration_photo_camera_settings_id is not None:
                result.far_face_calibration_photo_camera_settings_id = patch.far_face_calibration_photo_camera_settings_id
            
            if patch.far_x_offset is not None:
                result.far_x_offset = patch.far_x_offset
            if patch.far_y_offset is not None:
                result.far_y_offset = patch.far_y_offset
            if patch.far_z_offset is not None:
                result.far_z_offset = patch.far_z_offset
            if patch.far_x_offset_unc is not None:
                result.far_x_offset_unc = patch.far_x_offset_unc
            if patch.far_y_offset_unc is not None:
                result.far_y_offset_unc = patch.far_y_offset_unc
            if patch.far_z_offset_unc is not None:
                result.far_z_offset_unc = patch.far_z_offset_unc
        # Near face
            if patch.near_face_calibration_pattern_size is not None:
                result.near_face_calibration_pattern_size = patch.near_face_calibration_pattern_size
            if patch.near_face_calibration_pattern_type is not None:
                result.near_face_calibration_pattern_type = patch.near_face_calibration_pattern_type
            if patch.near_face_calibration_spacing is not None:
                result.near_face_calibration_spacing = patch.near_face_calibration_spacing
            if patch.near_face_calibration_spacing_unc is not None:
                result.near_face_calibration_spacing_unc = patch.near_face_calibration_spacing_unc
            if patch.near_face_calibration_photo_camera_settings_id is not None:
                result.far_face_calibration_photo_camera_settings_id = patch.near_face_calibration_photo_camera_settings_id
            
            if patch.near_x_offset is not None:
                result.near_x_offset = patch.near_x_offset
            if patch.near_y_offset is not None:
                result.near_y_offset = patch.near_y_offset
            if patch.near_z_offset is not None:
                result.near_z_offset = patch.near_z_offset
            if patch.near_x_offset_unc is not None:
                result.near_x_offset_unc = patch.near_x_offset_unc
            if patch.near_y_offset_unc is not None:
                result.near_y_offset_unc = patch.near_y_offset_unc
            if patch.near_z_offset_unc is not None:
                result.near_z_offset_unc = patch.near_z_offset_unc
        # Scintillator edges
            if patch.scintillator_edges_photo_camera_settings_id is not None:
                result.scintillator_edges_photo_camera_settings_id = patch.scintillator_edges_photo_camera_settings_id
            if patch.horizontal_scintillator_start is not None:
                result.horizontal_scintillator_start = patch.horizontal_scintillator_start
            if patch.horizontal_scintillator_end is not None:
                result.horizontal_scintillator_end = patch.horizontal_scintillator_end
            if patch.vertical_scintillator_start is not None:
                result.vertical_scintillator_start = patch.vertical_scintillator_start
            if patch.vertical_scintillator_end is not None:
                result.vertical_scintillator_end = patch.vertical_scintillator_end
        # Distortion calibration
            if patch.do_distortion_calibration is not None:
                result.do_distortion_calibration = patch.do_distortion_calibration
            if patch.distortion_calibration_camera_settings_link is not None:
                result.distortion_calibration_camera_settings_link = patch.distortion_calibration_camera_settings_link
            if patch.distortion_calibration_pattern_size_z_dim is not None:
                result.distortion_calibration_pattern_size_z_dim = patch.distortion_calibration_pattern_size_z_dim
            if patch.distortion_calibration_pattern_size_non_z_dim is not None:
                result.distortion_calibration_pattern_size_non_z_dim = patch.distortion_calibration_pattern_size_non_z_dim
            if patch.distortion_calibration_pattern_spacing is not None:
                result.distortion_calibration_pattern_spacing = patch.distortion_calibration_pattern_spacing
            if patch.distortion_calibration_pattern_type is not None:
                result.distortion_calibration_pattern_type = patch.distortion_calibration_pattern_type
        # Others
            if patch.lens_position is not None:
                result.lens_position = patch.lens_position

            setup_statement = select(Setup).join(CameraSetupLink).where(CameraSetupLink.id == setup_camera_id)
            setup_result = session.exec(setup_statement).one() #from .one()
            setup_result.date_last_edited = datetime.now(pytz.utc)
            session.commit()
            return f"Successfully patched parameters of setup camera with id: {setup_camera_id}"
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup_camera_id: {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_camera_matrix(camera_id:int, setup_id:int, camera_matrix: np.ndarray[float, float]|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.camera_matrix = camera_matrix
            session.commit()
            return {"message": f"Camera matrix updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_distortion_coefficients(camera_id:int, setup_id:int, distortion_coefficients: np.ndarray[float]|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.distortion_coefficients = distortion_coefficients
            session.commit()
            return {"message": f"Distortion coefficients updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
# def update_distortion_calibration_pattern_size(camera_id:int, setup_id:int, distortion_calibration_pattern_size: List[int]|None):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#             result = session.exec(statement).one()
#             result.distortion_calibration_pattern_size = distortion_calibration_pattern_size
#             session.commit()
#             return {"message": f"Distortion calibration pattern size updated for camera with id {camera_id} and setup with id {setup_id}."}
#     except NoResultFound:
#         raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")

def update_distortion_calibration_pattern_size_z_dim(setup_camera_id: int, distortion_calibration_pattern_size_z_dim: int):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.distortion_calibration_pattern_size_z_dim = distortion_calibration_pattern_size_z_dim
            session.commit()
            return {"message": f"Distortion calibration pattern size updated for setup camera id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup camera id {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

def update_distortion_calibration_pattern_size_non_z_dim(setup_camera_id: int, distortion_calibration_pattern_size_non_z_dim: int):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.distortion_calibration_pattern_size_non_z_dim = distortion_calibration_pattern_size_non_z_dim
            session.commit()
            return {"message": f"Distortion calibration pattern size updated for setup camera id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup camera id {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_distortion_calibration_pattern_type(setup_camera_id: int, distortion_calibration_pattern_type: str):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.distortion_calibration_pattern_type = distortion_calibration_pattern_type
            session.commit()
            return {"message": f"Distortion calibration pattern type updated for setup camera id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup camera id {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_distortion_calibration_pattern_spacing(setup_camera_id: int, distortion_calibration_pattern_spacing: float):
    try:
        with Session(engine) as session:
            # statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            # result = session.exec(statement).one()
            setup_camera = session.get(CameraSetupLink, setup_camera_id)
            setup_camera.distortion_calibration_pattern_spacing = distortion_calibration_pattern_spacing
            session.commit()
            return {"message": f"Distortion calibration pattern spacing updated for setup camera id {setup_camera_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup camera id {setup_camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
    
def update_far_face_calibration_spacing(camera_id:int, setup_id:int, far_face_calibration_spacing: list[float]|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.far_face_calibration_spacing = far_face_calibration_spacing
            session.commit()
            return {"message": f"Far face homography calibration pattern spacing updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_near_face_calibration_spacing(camera_id:int, setup_id:int, near_face_calibration_spacing: list[float]|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.near_face_calibration_spacing = near_face_calibration_spacing
            session.commit()
            return {"message": f"Near face homography calibration pattern spacing updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_far_face_calibration_spacing_unc(camera_id:int, setup_id:int, far_face_calibration_spacing_unc: list[float]|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.far_face_calibration_spacing_unc = far_face_calibration_spacing_unc
            session.commit()
            return {"message": f"Far face homography calibration pattern spacing uncertainty updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_near_face_calibration_spacing_unc(camera_id:int, setup_id:int, near_face_calibration_spacing_unc: list[float]|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.near_face_calibration_spacing_unc = near_face_calibration_spacing_unc
            session.commit()
            return {"message": f"Near face homography calibration pattern spacing uncertainty updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
# Delete
