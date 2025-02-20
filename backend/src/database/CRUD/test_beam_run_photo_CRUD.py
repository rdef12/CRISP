from src.database.database import engine
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound
from src.database.models import TestBeamRunPhoto

# Create

def add_test_beam_run_photo_just_settings_and_camera(beam_run_id: int, settings_id: int, camera_id: int):
    # A little confusing since no actual photo is added here
    try:
        test_beam_run_photo = TestBeamRunPhoto(beam_run_id=beam_run_id, settings_id=settings_id, camera_id=camera_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(test_beam_run_photo)
        session.commit()
        return {"message": f"Test beam run photo added successfully with beam_run_id: {beam_run_id}, settings_id: {settings_id} and camera_id: {camera_id}."}

# Read

def get_test_beam_run_id_from_beam_run_id_settings_id_and_camera_id(beam_run_id: int, settings_id: int, camera_id: int):
    # THIS ONLY UNIQUELY DEFINES IT IF SETTINGS ARE ENFORCED TO BE DIFFERENT
    with Session(engine) as session:
        statement = select(TestBeamRunPhoto).where(TestBeamRunPhoto.beam_run_id == beam_run_id).where(TestBeamRunPhoto.settings_id == settings_id).where(TestBeamRunPhoto.camera_id == camera_id)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Test beam run photo with beam_run_id: {beam_run_id}, settings_id: {settings_id} and camera_id: {camera_id}not found (or not unique).")

# def get_optimum_gain_photo_id_from_beam_ESS_energy_and_current(beam_ESS_energy: float, beam_current: int):
    

# Update

def update_test_beam_run_photo(beam_run_id: int, settings_id: int, camera_id:int, photo: bytes):
    try:
        with Session(engine) as session:
            statement = select(TestBeamRunPhoto).where(TestBeamRunPhoto.beam_run_id == beam_run_id).where(TestBeamRunPhoto.settings_id == settings_id).where(TestBeamRunPhoto.camera_id == camera_id)
            result = session.exec(statement).one()
            result.photo = photo
            session.commit()
            return {"message": f"Test beam run photo with beam_run_id: {beam_run_id} and settings_id: {settings_id} updated."}
    except NoResultFound:
        raise ValueError(f"No test beam run photo found for beam_run_id={beam_run_id} and settings_id={settings_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_optimal_gain_flag(test_beam_run_photo_id: int, optimal_gain_flag: bool):
    try:
        with Session(engine) as session:
            statement = select(TestBeamRunPhoto).where(TestBeamRunPhoto.id == test_beam_run_photo_id)
            result = session.exec(statement).one()
            result.optimal_gain_flag = optimal_gain_flag
            session.commit()
            return {"message": f"Test beam run photo with id: {test_beam_run_photo_id} updated with optimal_gain_flag: {optimal_gain_flag}"}
    except NoResultFound:
        raise ValueError(f"No test beam run photo found for test_beam_run_photo_id={test_beam_run_photo_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# Delete