from pydantic import BaseModel
from typing import Optional, List

from src.database.models import Camera, Settings

class SetupCameraCreateRequest(BaseModel):
    camera_id: int

class SetupCameraGetRequest(BaseModel):
    id: int
    camera_id: int
    setup_id: int
    camera: Camera

class SetupCameraScintillatorEdgeRequest(BaseModel):
    id: int
    camera_id: int
    setup_id: int
    scintillator_edges_photo_camera_settings_id: Optional[int]
    settings: Optional[Settings]
    horizontal_start: Optional[int]
    horizontal_end: Optional[int]
    vertical_start: Optional[int]
    vertical_end: Optional[int]


class SetupCameraDistortionCalibrationGetRequest(BaseModel):
    id: int
    camera_id: int
    setup_id: Optional[int] = None
    distortion_calibration_camera_settings_link: Optional[int] = None
    settings: Optional[Settings] = None
    do_distortion_calibration: Optional[bool] = None
    distortion_calibration_pattern_size_z_dim: Optional[int] = None
    distortion_calibration_pattern_size_non_z_dim: Optional[int] = None
    distortion_calibration_pattern_type: Optional[str] = None
    distortion_calibration_pattern_spacing: Optional[float] = None

class SetupCameraDistortionCalibrationPostRequest(BaseModel):
    gain: float
    distortion_calibration_pattern_size_z_dim: int
    distortion_calibration_pattern_size_non_z_dim: int
    distortion_calibration_pattern_type: str
    distortion_calibration_pattern_spacing: float

class SetupCameraPatchRequest(BaseModel):
# Far face
    #Calibration pattern type here too?
    far_face_calibration_pattern_size: Optional[List[int]] = None
    far_face_calibration_pattern_type: Optional[str] = None
    far_face_calibration_spacing: Optional[List[float]] = None
    far_face_calibration_spacing_unc: Optional[List[float]] = None
    far_face_calibration_photo_camera_settings_id: Optional[int] = None
    far_x_offset: Optional[float] = None
    far_x_offset_unc: Optional[float] = None
    far_y_offset: Optional[float] = None
    far_y_offset_unc: Optional[float] = None
    far_z_offset: Optional[float] = None
    far_z_offset_unc: Optional[float] = None
# Near face
    near_face_calibration_pattern_size: Optional[List[int]] = None
    near_face_calibration_pattern_type: Optional[str] = None
    near_face_calibration_spacing: Optional[List[float]] = None
    near_face_calibration_spacing_unc: Optional[List[float]] = None
    near_face_calibration_photo_camera_settings_id: Optional[int] = None
    near_x_offset: Optional[float] = None
    near_x_offset_unc: Optional[float] = None
    near_y_offset: Optional[float] = None
    near_y_offset_unc: Optional[float] = None
    near_z_offset: Optional[float] = None
    near_z_offset_unc: Optional[float] = None
# Scintillator edges
    scintillator_edges_photo_camera_settings_id: Optional[int] = None
    horizontal_scintillator_start: Optional[int] = None
    horizontal_scintillator_end: Optional[int] = None
    vertical_scintillator_start: Optional[int] = None
    vertical_scintillator_end: Optional[int] = None
# Distortion calibration
    do_distortion_calibration: Optional[bool] = None
    distortion_calibration_camera_settings_link: Optional[int] = None
    distortion_calibration_pattern_size_z_dim: Optional[int] = None
    distortion_calibration_pattern_size_non_z_dim: Optional[int] = None
    distortion_calibration_pattern_spacing: Optional[float] = None
    distortion_calibration_pattern_type: Optional[str] = None
# Others
    lens_position: Optional[float] = None
    # e_log_entry: #How is this going to be stored, surely theres a better way than just a string?
