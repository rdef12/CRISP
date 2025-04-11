from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from src.database.models import CameraSetupLink

class HomographyCalibrationSettingsPostPayload(BaseModel):
    gain: float
    horizontal_grid_dimension: int
    vertical_grid_dimension: int
    horizontal_grid_spacing: float
    horizontal_grid_spacing_error: float
    vertical_grid_spacing: float
    vertical_grid_spacing_error: float
    board_thickness: float
    board_thickness_error: float
    origin_shift_z_dir: float
    origin_shift_z_dir_error: float
    origin_shift_non_z_dir: float
    origin_shift_non_z_dir_error: float

class HomographyCalibrationSettingsGetBody(BaseModel):
    id: int
    camera_settings_id: Optional[int] = None
    gain: Optional[float] = None
    horizontal_grid_dimension: Optional[int] = None
    vertical_grid_dimension: Optional[int] = None
    horizontal_grid_spacing: Optional[float] = None
    horizontal_grid_spacing_error: Optional[float] = None
    vertical_grid_spacing: Optional[float] = None
    vertical_grid_spacing_error: Optional[float] = None
    board_thickness: Optional[float] = None
    board_thickness_error: Optional[float] = None
    origin_shift_z_dir: Optional[float] = None
    origin_shift_z_dir_error: Optional[float] = None
    origin_shift_non_z_dir: Optional[float] = None
    origin_shift_non_z_dir_error: Optional[float] = None

