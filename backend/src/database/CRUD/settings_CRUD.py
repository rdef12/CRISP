from src.database.database import engine
from sqlmodel import Session, select
from src.database.models import CameraSettingsLink, CameraSetupLink, Settings

from src.database.CRUD import CRISP_database_interaction as cdi

# Create

def add_settings(frame_rate: int, lens_position: float, gain: float):
    try:
        statement = select(Settings).where(Settings.frame_rate == frame_rate).where(Settings.lens_position == lens_position).where(Settings.gain == gain)
    except TypeError as e:
        raise TypeError(f"TypeError adding settings: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError adding settings: {e}") from e
    
    with Session(engine) as session:
        try:
            existing_settings = session.exec(statement).one()
            return {"message": f"Settings already existed with frame_rate: {frame_rate}, lens_position: {lens_position}, gain: {gain}",
                    "id": existing_settings.id}
        except:
            pass
        new_settings = Settings(frame_rate=frame_rate, lens_position=lens_position, gain=gain)
        session.add(new_settings)
        session.commit()
        return {"message": f"Settings added with frame_rate: {frame_rate}, lens_position: {lens_position}, gain: {gain}",
                "id": new_settings.id}
        
# Read

def get_settings_id_from_settings(frame_rate: int, lens_position: float, gain: float) -> int:
    with Session(engine) as session:
        statement = select(Settings).where(Settings.frame_rate == frame_rate).where(Settings.lens_position == lens_position).where(Settings.gain == gain)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Settings with frame_rate: {frame_rate}, lens_position: {lens_position}, gain: {gain} not found")
        

def get_settings_by_id(settings_id: int):
    with Session(engine) as session:
        settings = session.get(Settings, settings_id)
        return settings

def get_settings_by_setup_camera_id_scintillator_edges(setup_camera_id: int):
    with Session(engine) as session:
        setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
        scintillator_edges_camera_settings_id = setup_camera.scintillator_edges_photo_camera_settings_id
        settings_id = cdi.get_settings_id_by_camera_settings_id(scintillator_edges_camera_settings_id)
        settings = get_settings_by_id(settings_id)
        
        return settings
    
def get_settings_by_setup_camera_id_distortion_calibration(setup_camera_id: int):
    with Session(engine) as session:
        setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
        distortion_calibration_camera_settings_id = setup_camera.distortion_calibration_camera_settings_link
        settings_id = cdi.get_settings_id_by_camera_settings_id(distortion_calibration_camera_settings_id)
        settings = get_settings_by_id(settings_id)
        return settings


# Update

# Delete