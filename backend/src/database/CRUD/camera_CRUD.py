from sqlmodel import Session, select

from src.database.database import engine
from src.database.models import Camera

# Create

def add_camera(username:str, ip_address: str, password: str, model: str):
    try:
        camera = Camera(username=username, ip_address=ip_address, password=password, model=model)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(camera)
        session.commit()
        session.refresh(camera)
        return {"message": f"Camera added successfully with: usernname {username}, IP address {ip_address} and password {password}.",
                "id": camera.id}

# Read

def get_camera_id_from_username(username: str) -> int:
    with Session(engine) as session:
        statement = select(Camera).where(Camera.username == username)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Camera with username: {username} not found")
        
def get_username_from_camera_id(camera_id: int) -> str:
    with Session(engine) as session:
        statement = select(Camera).where(Camera.id == camera_id)
        result = session.exec(statement).one()
        if result:
            return result.username
        else:
            raise ValueError(f"Camera with id = {camera_id} not found")

def get_camera_entry_with_username(username: str):
    with Session(engine) as session:
        statement = select(Camera).where(Camera.username == username)
        result = session.exec(statement).one()
        if result:
            return result
        else:
            raise ValueError(f"Camera with username: {username} not found")


def get_all_cameras():
    with Session(engine) as session:
        statement = select(Camera)
        results = session.exec(statement).all()
        return results

def get_all_cameras_for_react_admin() -> list[Camera]:
    with Session(engine) as session:
        statement = select(Camera)
        results = session.exec(statement).all()
        return results if results else []
    
def get_camera_by_id(id: int) -> Camera:
    with Session(engine) as session:
        return session.get(Camera, id)
    

# Update

# Delete

def delete_camera_with_username(username: str):
    with Session(engine) as session:
        statement = select(Camera).where(Camera.username == username)
        result = session.exec(statement).one()
        if result:
            session.delete(result)
            session.commit()
            return {"message": f"Camera with username: {username} successfully deleted"}
        else:
            raise ValueError(f"Camera with username: {username} not found")