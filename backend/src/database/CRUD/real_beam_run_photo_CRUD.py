from src.database.database import engine
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound
from src.database.models import RealBeamRunPhoto

# Create

def add_real_beam_run_photo(real_beam_run_settings_and_cameras_id: int, photo: bytes, photo_metadata: bytes):
    try:
        real_beam_run_photo = RealBeamRunPhoto(real_beam_run_settings_and_cameras_id=real_beam_run_settings_and_cameras_id,
                                               photo=photo,
                                               photo_metadata=photo_metadata)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(real_beam_run_photo)
        session.commit()
        return {"message": f"Real beam run photo added successfully with real_beam_run_settings_and_cameras_id: {real_beam_run_settings_and_cameras_id}"}

# Read



# Update

# Delete