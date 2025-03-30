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

class BeamRunSettingsRequest(BaseModel):
    id: int
    frame_rate: int
    lens_position: float
    gain: float
    is_optimal: Optional[bool] = None

class RealBeamRunSettingsPost(BaseModel):
    frame_rate: int
    gain: int

class RealBeamRunSettingsPut(BaseModel):
    frame_rate: int
    gain: int