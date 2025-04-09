from datetime import datetime
from fastapi import HTTPException, Response, APIRouter
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.models import Camera, CameraSettingsLink, CameraSetupLink, Experiment, Photo, Settings
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb

from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/homography-calibration",
    tags=["homography-calibration"],
)

@router.get("/settings/{plane}/{setup_camera_id}")
def get_homography_calibration_settings(plane: str, setup_camera_id: int):
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        if plane == "near":
            camera_settings_id = setup_camera.near_face_calibration_photo_camera_settings_id
            gain = None
            if camera_settings_id is not None:
                camera_settings = session.get(CameraSettingsLink, camera_settings_id)
                settings = session.get(Settings, camera_settings.id)
                gain = settings.gain
            
            horizontal_grid_dimension = None
            vertical_grid_dimension = None
            if setup_camera.near_face_calibration_pattern_size is not None:
                horizontal_grid_dimension, vertical_grid_dimension = setup_camera.near_face_calibration_pattern_size
            
            horizontal_grid_spacing = None
            vertical_grid_spacing = None
            if setup_camera.near_face_calibration_spacing is not None:
                horizontal_grid_spacing, vertical_grid_spacing = setup_camera.near_face_calibration_spacing
            
            horizontal_grid_spacing_error = None
            vertical_grid_spacing_error = None
            if setup_camera.near_face_calibration_spacing_unc is not None:
                horizontal_grid_spacing_error, vertical_grid_spacing_error = setup_camera.near_face_calibration_spacing_unc
            
            board_thickness = setup_camera.near_face_calibration_board_thickness
            board_thickness_error = setup_camera.near_face_calibration_board_thickness_unc
            origin_shift_z_dir = setup_camera.near_face_z_shift
            origin_shift_z_dir_error = setup_camera.near_face_z_shift_unc
            origin_shift_non_z_dir = setup_camera.near_face_non_z_shift
            origin_shift_non_z_dir_error = setup_camera.near_face_non_z_shift_unc
            return rb.HomographyCalibrationSettingsGetBody(id=setup_camera_id,
                                                   camera_settings_id=camera_settings_id,
                                                   gain=gain,
                                                   horizontal_grid_dimension=horizontal_grid_dimension,
                                                   vertical_grid_dimension=vertical_grid_dimension,
                                                   horizontal_grid_spacing=horizontal_grid_spacing,
                                                   vertical_grid_spacing=vertical_grid_spacing,
                                                   horizontal_grid_spacing_error=horizontal_grid_spacing_error,
                                                   vertical_grid_spacing_error=vertical_grid_spacing_error,
                                                   board_thickness=board_thickness,
                                                   board_thickness_error=board_thickness_error,
                                                   origin_shift_z_dir=origin_shift_z_dir,
                                                   origin_shift_z_dir_error=origin_shift_z_dir_error,
                                                   origin_shift_non_z_dir=origin_shift_non_z_dir,
                                                   origin_shift_non_z_dir_error=origin_shift_non_z_dir_error)
        if plane == "far":
            camera_settings_id = setup_camera.far_face_calibration_photo_camera_settings_id
            gain = None
            if camera_settings_id is not None:
                camera_settings = session.get(CameraSettingsLink, camera_settings_id)
                settings = session.get(Settings, camera_settings.settings_id)
                gain = settings.gain
            
            horizontal_grid_dimension = None
            vertical_grid_dimension = None
            if setup_camera.far_face_calibration_pattern_size is not None:
                horizontal_grid_dimension, vertical_grid_dimension = setup_camera.far_face_calibration_pattern_size
            
            horizontal_grid_spacing = None
            vertical_grid_spacing = None
            if setup_camera.far_face_calibration_spacing is not None:
                horizontal_grid_spacing, vertical_grid_spacing = setup_camera.far_face_calibration_spacing
            
            horizontal_grid_spacing_error = None
            vertical_grid_spacing_error = None
            if setup_camera.far_face_calibration_spacing_unc is not None:
                horizontal_grid_spacing_error, vertical_grid_spacing_error = setup_camera.far_face_calibration_spacing_unc
            
            board_thickness = setup_camera.far_face_calibration_board_thickness
            board_thickness_error = setup_camera.far_face_calibration_board_thickness_unc
            origin_shift_z_dir = setup_camera.far_face_z_shift
            origin_shift_z_dir_error = setup_camera.far_face_z_shift_unc
            origin_shift_non_z_dir = setup_camera.far_face_non_z_shift
            origin_shift_non_z_dir_error = setup_camera.far_face_non_z_shift_unc
            return rb.HomographyCalibrationSettingsGetBody(id=setup_camera_id,
                                                   camera_settings_id=camera_settings_id,
                                                   gain=gain,
                                                   horizontal_grid_dimension=horizontal_grid_dimension,
                                                   vertical_grid_dimension=vertical_grid_dimension,
                                                   horizontal_grid_spacing=horizontal_grid_spacing,
                                                   vertical_grid_spacing=vertical_grid_spacing,
                                                   horizontal_grid_spacing_error=horizontal_grid_spacing_error,
                                                   vertical_grid_spacing_error=vertical_grid_spacing_error,
                                                   board_thickness=board_thickness,
                                                   board_thickness_error=board_thickness_error,
                                                   origin_shift_z_dir=origin_shift_z_dir,
                                                   origin_shift_z_dir_error=origin_shift_z_dir_error,
                                                   origin_shift_non_z_dir=origin_shift_non_z_dir,
                                                   origin_shift_non_z_dir_error=origin_shift_non_z_dir_error)
        raise HTTPException(status_code=400, detail=f"Invalid plane: {plane}. Must be 'near' or 'far'.")


@router.post("/settings/{plane}/{setup_camera_id}")
def add_homography_calibration_settings(plane: str, setup_camera_id: int, payload: rb.HomographyCalibrationSettingsPostPayload):
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        
        ### Clean up of remnant data ###
        old_camera_settings_id = None
        if plane == "near":
            old_camera_settings_id = setup_camera.near_face_calibration_photo_camera_settings_id
        elif plane == "far":
            old_camera_settings_id = setup_camera.far_face_calibration_photo_camera_settings_id
        else:
            raise HTTPException(status_code=400, detail=f"Invalid plane: {plane}. Must be 'near' or 'far'.")
        
        if old_camera_settings_id is not None:
            camera_settings = session.get(CameraSettingsLink, old_camera_settings_id)
            photos_statement = select(Photo).where(Photo.camera_settings_link_id == old_camera_settings_id)
            photos = session.exec(photos_statement).all()
            for photo in photos:
                session.delete(photo)
            session.delete(camera_settings)
            session.commit()
        
        ### Creation of settings ###
        lens_position = setup_camera.lens_position
        frame_rate = 30 # Hard coded
        gain = payload.gain

        ### Creation of camera settings link ###
        settings_id = cdi.add_settings(frame_rate, lens_position, gain)["id"]
        camera_id = setup_camera.camera_id
        camera_settings_id = cdi.add_camera_settings_link(camera_id, settings_id)["id"]

        ### Updating setup camera table ###
        if plane == "near":
            setup_camera.near_face_calibration_photo_camera_settings_id = camera_settings_id
            setup_camera.near_face_calibration_pattern_size = [payload.horizontal_grid_dimension, payload.vertical_grid_dimension]
            setup_camera.near_face_calibration_pattern_type = "chessboard" #TODO SHOULD NOT BE HARDCODED
            setup_camera.near_face_calibration_spacing = [payload.horizontal_grid_spacing, payload.vertical_grid_spacing]
            setup_camera.near_face_calibration_spacing_unc = [payload.horizontal_grid_spacing_error, payload.vertical_grid_spacing_error]
            setup_camera.near_face_calibration_board_thickness = payload.board_thickness
            setup_camera.near_face_calibration_board_thickness_unc = payload.board_thickness_error
            setup_camera.near_face_z_shift = payload.origin_shift_z_dir
            setup_camera.near_face_z_shift_unc = payload.origin_shift_z_dir_error
            setup_camera.near_face_non_z_shift = payload.origin_shift_non_z_dir
            setup_camera.near_face_non_z_shift_unc = payload.origin_shift_non_z_dir_error
        if plane == "far":
            setup_camera.far_face_calibration_photo_camera_settings_id = camera_settings_id
            setup_camera.far_face_calibration_pattern_size = [payload.horizontal_grid_dimension, payload.vertical_grid_dimension]
            setup_camera.far_face_calibration_pattern_type = "chessboard" #TODO SHOULD NOT BE HARDCODED
            setup_camera.far_face_calibration_spacing = [payload.horizontal_grid_spacing, payload.vertical_grid_spacing]
            setup_camera.far_face_calibration_spacing_unc = [payload.horizontal_grid_spacing_error, payload.vertical_grid_spacing_error]
            setup_camera.far_face_calibration_board_thickness = payload.board_thickness
            setup_camera.far_face_calibration_board_thickness_unc = payload.board_thickness_error
            setup_camera.far_face_z_shift = payload.origin_shift_z_dir
            setup_camera.far_face_z_shift_unc = payload.origin_shift_z_dir_error
            setup_camera.far_face_non_z_shift = payload.origin_shift_non_z_dir
            setup_camera.far_face_non_z_shift_unc = payload.origin_shift_non_z_dir_error
        session.commit()
        return setup_camera
    

@router.put("/settings/{plane}/{setup_camera_id}")
def update_homography_calibration_settings(plane: str, setup_camera_id: int, payload: rb.HomographyCalibrationSettingsPostPayload):
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        
        ### Clean up of remnant data ###
        old_camera_settings_id = None
        if plane == "near":
            old_camera_settings_id = setup_camera.near_face_calibration_photo_camera_settings_id
            setup_camera.near_face_calibration_photo_camera_settings_id = None
        elif plane == "far":
            old_camera_settings_id = setup_camera.far_face_calibration_photo_camera_settings_id
            setup_camera.far_face_calibration_photo_camera_settings_id = None
        else:
            raise HTTPException(status_code=400, detail=f"Invalid plane: {plane}. Must be 'near' or 'far'.")
        
        if old_camera_settings_id is not None:
            camera_settings = session.get(CameraSettingsLink, old_camera_settings_id)
            photos_statement = select(Photo).where(Photo.camera_settings_link_id == old_camera_settings_id)
            photos = session.exec(photos_statement).all()
            for photo in photos:
                session.delete(photo)
            session.delete(camera_settings)
            session.commit()
        
        ### Creation of settings ###
        lens_position = setup_camera.lens_position
        frame_rate = 30 # Hard coded
        gain = payload.gain

        ### Creation of camera settings link ###
        settings_id = cdi.add_settings(frame_rate, lens_position, gain)["id"]
        camera_id = setup_camera.camera_id
        camera_settings_id = cdi.add_camera_settings_link(camera_id, settings_id)["id"]

        ### Updating setup camera table ###
        if plane == "near":
            setup_camera.near_face_calibration_photo_camera_settings_id = camera_settings_id
            setup_camera.near_face_calibration_pattern_size = [payload.horizontal_grid_dimension, payload.vertical_grid_dimension]
            setup_camera.near_face_calibration_pattern_type = "chessboard" #TODO SHOULD NOT BE HARDCODED
            setup_camera.near_face_calibration_spacing = [payload.horizontal_grid_spacing, payload.vertical_grid_spacing]
            setup_camera.near_face_calibration_spacing_unc = [payload.horizontal_grid_spacing_error, payload.vertical_grid_spacing_error]
            setup_camera.near_face_calibration_board_thickness = payload.board_thickness
            setup_camera.near_face_calibration_board_thickness_unc = payload.board_thickness_error
            setup_camera.near_face_z_shift = payload.origin_shift_z_dir
            setup_camera.near_face_z_shift_unc = payload.origin_shift_z_dir_error
            setup_camera.near_face_non_z_shift = payload.origin_shift_non_z_dir
            setup_camera.near_face_non_z_shift_unc = payload.origin_shift_non_z_dir_error
        if plane == "far":
            setup_camera.far_face_calibration_photo_camera_settings_id = camera_settings_id
            setup_camera.far_face_calibration_pattern_size = [payload.horizontal_grid_dimension, payload.vertical_grid_dimension]
            setup_camera.far_face_calibration_pattern_type = "chessboard" #TODO SHOULD NOT BE HARDCODED
            setup_camera.far_face_calibration_spacing = [payload.horizontal_grid_spacing, payload.vertical_grid_spacing]
            setup_camera.far_face_calibration_spacing_unc = [payload.horizontal_grid_spacing_error, payload.vertical_grid_spacing_error]
            setup_camera.far_face_calibration_board_thickness = payload.board_thickness
            setup_camera.far_face_calibration_board_thickness_unc = payload.board_thickness_error
            setup_camera.far_face_z_shift = payload.origin_shift_z_dir
            setup_camera.far_face_z_shift_unc = payload.origin_shift_z_dir_error
            setup_camera.far_face_non_z_shift = payload.origin_shift_non_z_dir
            setup_camera.far_face_non_z_shift_unc = payload.origin_shift_non_z_dir_error
        session.commit()
        return rb.HomographyCalibrationSettingsGetBody(id=setup_camera_id)