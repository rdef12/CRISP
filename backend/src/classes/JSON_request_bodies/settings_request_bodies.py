from typing import Optional
from pydantic import BaseModel

class SettingsCreateRequest(BaseModel):
    frame_rate: int
    lens_position: float
    gain: float


class SettingsPutRequest(BaseModel):
    frame_rate: int
    lens_position: float
    gain: float

class TestBeamRunSettingsRequest(BaseModel):
    id: int
    camera_settings_id: int
    frame_rate: int
    lens_position: float
    gain: float
    is_optimal: Optional[bool] = None

class RealBeamRunSettingsRequest(BaseModel):
    id: int
    frame_rate: int
    lens_position: float
    gain: float
    has_settings: bool
    is_optimal: Optional[bool] = None


class UpdateIsOptimalRequest(BaseModel):
    id: int

class RealBeamRunSettingsPost(BaseModel):
    frame_rate: int
    gain: int

class RealBeamRunSettingsPut(BaseModel):
    frame_rate: int
    gain: int