from pydantic import BaseModel

class SettingsCreateRequest(BaseModel):
    frame_rate: int #TODO just temporary
    lens_position: float #TODO just temporary
    gain: float