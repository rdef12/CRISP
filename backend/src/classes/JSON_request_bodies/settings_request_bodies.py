from pydantic import BaseModel

class SettingsCreateRequest(BaseModel):
    frame_rate: int
    lens_position: float
    gain: float


class SettingsPutRequest(BaseModel):
    frame_rate: int
    lens_position: float
    gain: float