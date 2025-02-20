from src.database.database import engine
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import RealBeamRunSettingsAndCamera

# Create

def add_real_beam_run_settings_and_camera(real_beam_run_id: int, camera_id: int, camera_settings_id: int):
    try:
        real_beam_run_settings_and_camera = RealBeamRunSettingsAndCamera(real_beam_run_id=real_beam_run_id, camera_id=camera_id, camera_settings_id=camera_settings_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(real_beam_run_settings_and_camera)
        session.commit()
        return {"message": f"Real beam run settings and camera added successfully with real_beam_run_id: {real_beam_run_id}, camera_id: {camera_id} and camera_settings_id: {camera_settings_id}"}

# Read

def get_real_beam_run_settings_and_cameras_id(real_beam_run_id: int, camera_id: int, settings_id: int):
    with Session(engine) as session:
        statement = select(RealBeamRunSettingsAndCamera).where(RealBeamRunSettingsAndCamera.real_beam_run_id == real_beam_run_id).where(RealBeamRunSettingsAndCamera.camera_id == camera_id).where(RealBeamRunSettingsAndCamera.settings_id == settings_id)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Real beam run settings and camera with real_beam_run_id: {real_beam_run_id}, camera_id: {camera_id} and settings_id: {settings_id} not found")

# Something to return all pairs of camera_id and settings_id for a given real_beam_run_id

# Update

# Delete