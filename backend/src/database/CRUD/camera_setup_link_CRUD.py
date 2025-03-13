from datetime import datetime
import pytz
from src.database.database import engine
from sqlmodel import Session, select, PickleType
from sqlalchemy.orm.exc import NoResultFound
import numpy as np
from typing import List

from src.database.models import CameraSetupLink, Setup
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

def get_setup_camera_by_id(id: int) -> CameraSetupLink:
    with Session(engine) as session:
        return session.get(CameraSetupLink, id)

def get_far_face_calibration_photo(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_calibration_photo
        else:
            raise ValueError(f"Far face calibration photo not found for camera with id {camera_id} and setup with id {setup_id}.")


def get_near_face_calibration_photo(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_calibration_photo
        else:
            raise ValueError(f"Near face calibration photo not found for camera with id {camera_id} and setup with id {setup_id}.")


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


def get_far_face_homography_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_homography_matrix
        else:
            raise ValueError(f"Homography matrix not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_far_face_homography_covariance_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.far_face_homography_covariance_matrix
        else:
            raise ValueError(f"Homography covariance matrix not found for camera with id {camera_id} and setup with id {setup_id}.")

def get_near_face_homography_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_homography_matrix
        else:
            raise ValueError(f"Homography matrix not found for camera with id {camera_id} and setup with id {setup_id}.")


def get_near_face_homography_covariance_matrix(camera_id:int, setup_id:int) -> bytes:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        result = session.exec(statement).one()
        if result:
            return result.near_face_homography_covariance_matrix
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

# def update_far_face_camera_settings_link(camera_id:int, setup_id:int, camera_settings_id:int):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#             camera_setup_link = session.exec(statement).one()
#             camera_setup_link.far_face_calibration_photo_camera_settings_link = camera_settings_id
#             session.commit()
#             return {"message": f"Camera settings link updated for camera with id {camera_id} and setup with id {setup_id}."}
#     except NoResultFound:
#         raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")

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

# def update_near_face_camera_settings_link(camera_id:int, setup_id:int, camera_settings_id:int):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
#             camera_setup_link = session.exec(statement).one()
#             camera_setup_link.near_face_calibration_photo_camera_settings_link = camera_settings_id
#             session.commit()
#             return {"message": f"Camera settings link updated for camera with id {camera_id} and setup with id {setup_id}."}
#     except NoResultFound:
#         raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")
    

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


def update_scintillator_edges_photo_id(camera_id:int, setup_id:int, photo_id:int):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            camera_setup_link = session.exec(statement).one()
            camera_setup_link.scintillator_edges_photo_id = photo_id
            session.commit()
            return {"message": f"Camera settings link updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

def update_horizontal_scintillator_scintillator_limits(camera_id:int, setup_id:int, horizontal_scintillator_limits: tuple[int, int]):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.horizontal_scintillator_limits = horizontal_scintillator_limits
            session.commit()
            return {"message": f"Horizontal scintillator limits updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_vertical_scintillator_limits(camera_id:int, setup_id:int, vertical_scintillator_limits: tuple[int, int]):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.vertical_scintillator_limits = vertical_scintillator_limits
            session.commit()
            return {"message": f"Vertical scintillator limits updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def patch_setup_camera(setup_camera_id: int, patch: rb.SetupCameraPatchRequest):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.id == setup_camera_id)
            result = session.exec(statement).one()
            
        # Far Face
            if patch.far_face_calibration_pattern_size is not None:
                result.far_face_calibration_pattern_size = patch.far_face_calibration_pattern_size
            if patch.far_face_calibration_pattern_type is not None:
                result.far_face_calibration_pattern_type = patch.far_face_calibration_pattern_type
            if patch.far_face_calibration_spacing is not None:
                result.far_face_calibration_spacing = patch.far_face_calibration_spacing
            if patch.far_face_calibration_spacing_unc is not None:
                result.far_face_calibration_spacing_unc = patch.far_face_calibration_spacing_unc
            if patch.far_face_calibration_photo_id is not None:
                result.far_face_calibration_photo_id = patch.far_face_calibration_photo_id
            
            if patch.far_x_offset is not None:
                print("\n\n\n\n\n\n\n ABOUT TO PATCH THE FAR X OFFSET \n\n\n\n\n")
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
            if patch.near_face_calibration_photo_id is not None:
                result.near_face_calibration_photo_id = patch.near_face_calibration_photo_id
            
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
            if patch.scintillator_edges_photo_id is not None:
                result.scintillator_edges_photo_id = patch.scintillator_edges_photo_id
            if patch.horizontal_scintillator_limits is not None:
                result.horizontal_scintillator_limits = patch.horizontal_scintillator_limits
            if patch.vertical_scintillator_limits is not None:
                result.vertical_scintillator_limits = patch.vertical_scintillator_limits
            setup_statement = select(Setup).where(CameraSetupLink.id == setup_camera_id)
            setup_result = session.exec(setup_statement).one()
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
    
def update_distortion_calibration_pattern_size(camera_id:int, setup_id:int, distortion_calibration_pattern_size: List[int]|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.distortion_calibration_pattern_size = distortion_calibration_pattern_size
            session.commit()
            return {"message": f"Distortion calibration pattern size updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_distortion_calibration_pattern_type(camera_id:int, setup_id:int, distortion_calibration_pattern_type: str|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.distortion_calibration_pattern_type = distortion_calibration_pattern_type
            session.commit()
            return {"message": f"Distortion calibration pattern type updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_distortion_calibration_pattern_spacing(camera_id:int, setup_id:int, distortion_calibration_pattern_spacing: float|None):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.distortion_calibration_pattern_spacing = distortion_calibration_pattern_spacing
            session.commit()
            return {"message": f"Distortion calibration pattern spacing updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# Delete
