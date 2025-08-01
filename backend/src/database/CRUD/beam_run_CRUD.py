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
                        is_test: bool): # And other beam parameters to be added
    try:
        beam_run = BeamRun(experiment_id=experiment_id,
                                        beam_run_number=beam_run_number,
                                        datetime_of_run=datetime_of_run,
                                        ESS_beam_energy=ESS_beam_energy,
                                        beam_current=beam_current,
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

def get_experiment_id_from_beam_run_id(beam_run_id: int):
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.experiment_id
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be a found.")

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
        statement = select(BeamRun).join(CameraSettingsLink).where(CameraSettingsLink.id == camera_settings_link_id)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Beam run with camera_setup_link_id: {camera_settings_link_id} cannot be found.")

def get_beam_run_ESS_beam_energy(beam_run_id: int) -> float:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.ESS_beam_energy
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be found.")
        
def get_bragg_peak_3d_position(beam_run_id: int) -> list[float]:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.bragg_peak_3d_position
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be found.")
        
def get_unc_bragg_peak_3d_position(beam_run_id: int) -> list[float]:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.unc_bragg_peak_3d_position
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be found.")
        
def get_beam_incident_3d_position(beam_run_id: int) -> list[float]:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.beam_incident_3d_position
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be found.")
        
def get_unc_beam_incident_3d_position(beam_run_id: int) -> list[float]:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.unc_beam_incident_3d_position
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be found.")

def get_beam_path_vector(beam_run_id: int) -> list[float]:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.beam_path_vector
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be found.")
        
def get_unc_beam_path_vector(beam_run_id: int) -> list[float]:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.id == beam_run_id)
        result = session.exec(statement).one()
        if result:
            return result.unc_beam_path_vector
        else:
            raise ValueError(f"Beam run with id {beam_run_id} cannot be found.")
    
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
    
def update_bragg_peak_3d_position(beam_run_id: int, bragg_peak_3d_position: list[float]):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.bragg_peak_3d_position = bragg_peak_3d_position
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with BP 3D position: {bragg_peak_3d_position}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_unc_bragg_peak_3d_position(beam_run_id: int, unc_bragg_peak_3d_position: list[float]):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.unc_bragg_peak_3d_position = unc_bragg_peak_3d_position
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with BP 3D position error: {unc_bragg_peak_3d_position}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_beam_incident_3d_position(beam_run_id: int, beam_incident_3d_position: list[float]):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.beam_incident_3d_position = beam_incident_3d_position
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with beam incident position: {beam_incident_3d_position}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_unc_beam_incident_3d_position(beam_run_id: int, unc_beam_incident_3d_position: list[float]):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.unc_beam_incident_3d_position = unc_beam_incident_3d_position
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with beam incident position uncertainty: {unc_beam_incident_3d_position}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

    
def update_beam_path_vector(beam_run_id: int, beam_path_vector: list[float]):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.beam_path_vector = beam_path_vector
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with beam path vector: {beam_path_vector}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
    
def update_unc_beam_path_vector(beam_run_id: int, unc_beam_path_vector: list[float]):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.unc_beam_path_vector = unc_beam_path_vector
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with beam path vector error: {unc_beam_path_vector}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    

def update_bragg_peak_depth(beam_run_id: int, bragg_peak_depth: float):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.bragg_peak_depth = bragg_peak_depth
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with bragg peak depth: {bragg_peak_depth}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_unc_bragg_peak_depth(beam_run_id: int, unc_bragg_peak_depth: float):
    try:
        with Session(engine) as session:
            statement = select(BeamRun).where(BeamRun.id == beam_run_id)
            result = session.exec(statement).one()
            result.unc_bragg_peak_depth = unc_bragg_peak_depth
            session.commit()
            return {"message": f"Beam run with id: {beam_run_id} updated with bragg peak depth: {unc_bragg_peak_depth}"}
    except NoResultFound:
        raise ValueError(f"No beam run found for beam_run_id={beam_run_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")



# Delete
