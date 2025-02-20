from src.database.database import engine
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound
from src.database.models import TestBeamRun

# Create

def add_test_beam_run(beam_run_number_id: int):
    try:
        test_beam_run = TestBeamRun(beam_run_number_id=beam_run_number_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(test_beam_run)
        session.commit()
        return {"message": f"Test beam run added successfully with beam_run_number_id: {beam_run_number_id}"}

# Read



# Update

# Delete