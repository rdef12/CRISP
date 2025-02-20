from datetime import datetime
from src.database.database import engine
from src.database.models import Experiment, Setup, Camera, CameraSetupLink
from sqlmodel import Session, select

# Create

def add_experiment(name: str, date_started: datetime, setup_id: int):
    try:
        experiment = Experiment(name=name, date_started=date_started, setup_id=setup_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(experiment)
        session.commit()
        return {"message", f"Experiment added to setup called {name}."}

# Read

def get_experiment_id_from_name(name: str) -> int:
    with Session(engine) as session:
        statement = select(Experiment).where(Experiment.name == name)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Experiment with name: {name} not found")


def get_setup_id_from_experiment_id(experiment_id: int) -> int:
    with Session(engine) as session:
        statement = select(Experiment).where(Experiment.id == experiment_id)
        result = session.exec(statement).one()
        if result:
            return result.setup_id
        else:
            raise ValueError(f"Experiment with id: {experiment_id} not found")


def get_camera_ids_from_experiment_id(experiment_id: int) -> int:
    with Session(engine) as session:
        statement = select(CameraSetupLink).where(Experiment.id == experiment_id)
        results = session.exec(statement).all()
        camera_ids = []
        for result in results:
            camera_ids += [result.camera_id]
        return camera_ids

# Update



# Delete