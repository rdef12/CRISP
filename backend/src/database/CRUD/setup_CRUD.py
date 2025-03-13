from datetime import datetime

import pytz
from src.database.database import engine
from sqlmodel import Session, select, PickleType
from sqlalchemy.orm.exc import NoResultFound

from src.database.models import Setup
from src.classes.JSON_request_bodies import request_bodies as rb


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

def get_setup_by_id(id: int) -> Setup:
    with Session(engine) as session:
        return session.get(Setup, id)
        

def get_setup_id_from_name(name: str) -> int:
    with Session(engine) as session:
        statement = select(Setup).where(Setup.name == name)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Setup with name: {name} not found")
        
def get_all_setups() -> list[Setup]:
    with Session(engine) as session:
        statement = select(Setup)
        results = session.exec(statement).all()
        return results if results else []

# Update

def patch_setup(setup_id: int, patch: rb.SetupPatchRequest):
    try:
        with Session(engine) as session:
            statement = select(Setup).where(Setup.id == setup_id)
            result = session.exec(statement).one()
            
            if patch.name is not None:
                result.name = patch.name

            if patch.block_x_dimension is not None:
                result.block_x_dimension = patch.block_x_dimension
            if patch.block_x_dimension_unc is not None:
                result.block_x_dimension_unc = patch.block_x_dimension_unc
            if patch.block_y_dimension is not None:
                result.block_y_dimension = patch.block_y_dimension
            if patch.block_y_dimension_unc is not None:
                result.block_y_dimension_unc = patch.block_y_dimension_unc
            if patch.block_z_dimension is not None:
                result.block_z_dimension = patch.block_z_dimension
            if patch.block_z_dimension_unc is not None:
                result.block_z_dimension_unc = patch.block_z_dimension_unc
            
            if patch.block_refractive_index is not None:
                result.block_refractive_index = patch.block_refractive_index
            if patch.block_refractive_index_unc is not None:
                result.block_refractive_index_unc = patch.block_refractive_index_unc

            result.date_last_edited = datetime.now(pytz.utc)
            session.commit()
            return f"Successfully patched parameters of setup with id: {setup_id}"
    except NoResultFound:
        raise ValueError(f"No camera setup link found for setup_id: {setup_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


# Delete