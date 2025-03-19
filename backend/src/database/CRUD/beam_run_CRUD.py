from datetime import datetime
from src.database.database import engine
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import BeamRun, CameraSettingsLink

# Create

def add_beam_run(experiment_id: int,
                        beam_run_number: int,
                        datetime_of_run: datetime,
                        ESS_beam_energy: float,
                        beam_current: float,
                        beam_current_unc: float,
                        is_test: bool): # And other beam parameters to be added
    try:
        beam_run = BeamRun(experiment_id=experiment_id,
                                        beam_run_number=beam_run_number,
                                        datetime_of_run=datetime_of_run,
                                        ESS_beam_energy=ESS_beam_energy,
                                        beam_current=beam_current,
                                        beam_current_unc=beam_current_unc,
                                        is_test=is_test)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(beam_run)
        session.commit()
        session.refresh(beam_run)
        return beam_run
        # return {"message": f"Beam run {beam_run} created for experiment with id: {experiment_id}",
        #         "id": beam_run.id}

# Read

def get_beam_run_id_from_experiment_id_and_beam_run_number(experiment_id: int, beam_run_number: int):
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.experiment_id == experiment_id).where(BeamRun.beam_run_number == beam_run_number)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Beam run with experiment_id: {experiment_id} and beam_run {beam_run_number} cannot be a found.")
        
def get_beam_run_id_from_camera_settings_link_id(camera_settings_link_id: int) -> int:
    with Session(engine) as session:
        statement = select(BeamRun).where(CameraSettingsLink.id == camera_settings_link_id)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Beam run with camera_setup_link_id: {camera_settings_link_id} cannot be found.")

# Update

def update_beam_run_is_test(beam_run_id: int, is_test: bool):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.is_test = is_test
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with is_test: {is_test}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_MSIC_beam_energy(beam_run_id: int, MSIC_beam_energy:float):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.MSIC_beam_energy = MSIC_beam_energy
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with MSIC beam energy: {MSIC_beam_energy}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

def update_MSIC_beam_energy_unc(beam_run_id: int, MSIC_beam_energy_unc:float):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.MSIC_beam_energy_unc = MSIC_beam_energy_unc
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with MSIC beam energy uncertainty: {MSIC_beam_energy_unc}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


# Delete
