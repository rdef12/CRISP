from src.database.database import engine
from sqlmodel import Session, select
from src.database.models import Photo

# Create

def add_photo(camera_settings_link_id: int, photo: bytes, photo_metadata: bytes):
    try:
        photo = Photo(camera_settings_link_id=camera_settings_link_id, photo=photo, photo_metadata=photo_metadata)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(photo)
        session.commit()
        return {"message": f"Photo added to camera settings link.",
                "id": photo.id}

# For testing only
def add_photo_for_testing(camera_settings_link_id: int, photo: bytes): # TODO added without metadata for testing
    try:
        photo = Photo(camera_settings_link_id=camera_settings_link_id, photo=photo)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(photo)
        session.commit()
        return {"message": f"Photo added to camera settings link.",
                "id": photo.id}


# Read

def get_photo_from_camera_settings_link_id(camera_settings_link_id: int): # This may need changing so that the photos are read in differently.
    with Session(engine) as session:
        statement = select(Photo).where(Photo.camera_settings_link_id == camera_settings_link_id)
        results = session.exec(statement).all()
        if results:
            for result in results:
                return result.photo
        else:
            raise ValueError(f"Photo with camera_settings_link_id: {camera_settings_link_id} cannot be a found.")


def get_photo_from_id(photo_id: int) -> bytes:
    with Session(engine) as session:
        statement = select(Photo).where(Photo.id == photo_id)
        result = session.exec(statement).one()
        if result:
            return result.photo
        else:
            raise ValueError(f"Photo with photo id: {photo_id} cannot be found.")
    return

# Update

# Delete