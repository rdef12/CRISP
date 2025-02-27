from datetime import datetime
from src.database.database import engine
from sqlmodel import Session, select, PickleType
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import Setup

# Create

def add_setup(setup_name: str, date_created: datetime, date_last_edited: datetime):
    try:
        setup = Setup(name=setup_name, date_created=date_created, date_last_edited=date_last_edited)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(setup)
        session.commit()
        return {"message": f"Setup added successfully with: name {setup_name}, date_created {date_created} and date_last_edited {date_last_edited}.",
                "id" : setup.id}


# Read

def get_setup_id_from_name(name: str) -> int:
    with Session(engine) as session:
        statement = select(Setup).where(Setup.name == name)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Setup with name: {name} not found")
        
def get_all_setups():
    with Session(engine) as session:
        statement = select(Setup)
        results = session.exec(statement).all()
        return results

# Update

# Delete