from src.database.database import engine
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import CameraSettingsLink, BeamRun

# Create

def add_camera_settings_link(camera_id: int, settings_id: int): # Need to enforce this as impossible for beam runs or maybe enforce this as first step then have to add beam run link
    try:
        camera_setup_link = CameraSettingsLink(camera_id=camera_id, settings_id=settings_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(camera_setup_link)
        session.commit()
        return {"message": f"Camera added to setup.",
                "id": camera_setup_link.id}

def add_camera_settings_link_with_beam_run(camera_id: int, settings_id: int, beam_run_id: int):
    try:
        camera_setup_link = CameraSettingsLink(camera_id=camera_id, settings_id=settings_id, beam_run_id=beam_run_id)
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

def get_camera_settings_link_id(camera_id: int, settings_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).where(CameraSettingsLink.camera_id == camera_id).where(CameraSettingsLink.settings_id == settings_id)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Camera settings link with camera_id: {camera_id} and settings_id {settings_id} cannot be a found.")
        

def get_camera_and_settings_ids(camera_settings_link_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).where(CameraSettingsLink.id == camera_settings_link_id)
        result = session.exec(statement).one()
        if result:
            return {"camera_id": result.camera_id, "settings_id": result.settings_id}
        else:
            raise ValueError(f"Camera settings link with id: {camera_settings_link_id} cannot be a found.")


def get_cameras_and_settings_from_beam_run_id(beam_run_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        result = session.exec(statement).all()
        if result:
            return [{"camera_id": r.camera_id, "settings_id": r.settings_id} for r in result]
        else:
            raise ValueError(f"Camera settings link with beam_run_id: {beam_run_id} cannot be a found.")


def get_optimal_settings_id_for_camera(camera_id: int, ESS_beam_energy: float, beam_current: float):
    with Session(engine) as session:
        statement = (select(CameraSettingsLink)
                     .where(CameraSettingsLink.camera_id == camera_id)
                     .where(BeamRun.ESS_beam_energy == ESS_beam_energy)
                     .where(BeamRun.beam_current == beam_current)
                     .where(CameraSettingsLink.is_optimal == True)
                     .where(BeamRun.is_test == True))
        result = session.exec(statement).one()
        if result:
            return {"camera_id": result.camera_id, "settings_id": result.settings_id}
        else:
            raise ValueError(f"Optimal settings for camera_id: {camera_id} with ESS_beam_energy: {ESS_beam_energy} and beam_current: {beam_current} cannot be a found.")

# Update

def flag_optimal_settings(beam_run_id: int, camera_id: int, settings_id: int):
    try:
        with Session(engine) as session:
            statement = (select(CameraSettingsLink)
                         .where(BeamRun.id == beam_run_id)
                         .where(CameraSettingsLink.camera_id == camera_id)
                         .where(CameraSettingsLink.settings_id == settings_id))
            result = session.exec(statement).one()
            result.is_optimal = True
            session.commit()
            return {"message": f"Camera settings link with beam_run_id: {beam_run_id}, camera_id: {camera_id} and settings_id: {settings_id} - set to optimal"}
    except NoResultFound:
        raise ValueError(f"No camera settings link found for beam_run_id={beam_run_id} and camera_id={camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_is_optimal(beam_run_id: int, camera_id: int, settings_id: int, is_optimal: bool):
    try:
        with Session(engine) as session:
            statement = select(CameraSettingsLink).where(BeamRun.id == beam_run_id).where(CameraSettingsLink.camera_id == camera_id).where(CameraSettingsLink.settings_id == settings_id)
            result = session.exec(statement).one()
            result.is_optimal = is_optimal
            session.commit()
            return {"message": f"Camera settings link with beam_run_id: {beam_run_id} and camera_id: {camera_id} updated with settings_id: {settings_id}"}
    except NoResultFound:
        raise ValueError(f"No camera settings link found for beam_run_id={beam_run_id} and camera_id={camera_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# Delete