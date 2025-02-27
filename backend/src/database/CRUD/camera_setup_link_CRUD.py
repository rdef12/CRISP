from src.database.database import engine
from sqlmodel import Session, select, PickleType
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import CameraSetupLink

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
        return {"message": f"Camera added to setup."}

# Read

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

def update_far_face_calibration_photo(camera_id:int, setup_id:int, far_face_calibration_photo_bytes: bytes):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.far_face_calibration_photo = far_face_calibration_photo_bytes
            session.commit()
            return {"message": f"Far face calibration photo updated for camera with id {camera_id} and setup with id {setup_id}."}
    except NoResultFound:
        raise ValueError(f"No camera setup link found for camera_id={camera_id} and setup_id={setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

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
    

def update_near_face_calibration_photo(camera_id:int, setup_id:int, near_face_calibration_photo_bytes: bytes):
    try:
        with Session(engine) as session:
            statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
            result = session.exec(statement).one()
            result.near_face_calibration_photo = near_face_calibration_photo_bytes
            session.commit()
            return {"message": f"Near face calibration photo updated for camera with id {camera_id} and setup with id {setup_id}."}
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
    

# Delete