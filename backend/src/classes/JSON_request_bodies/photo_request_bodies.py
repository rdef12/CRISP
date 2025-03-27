from pydantic import BaseModel
from typing import Optional

class ScintillatorEdgePhotoGet(BaseModel):
    id: int #setup camera id
    camera_settings_id: Optional[int]
    photo: Optional[bytes]
    height: Optional[int]
    width: Optional[int]

class DistortionCalibrationPhotoPost(BaseModel):
    id: int #setup camera id
    photo: bytes
    calibration_status: bool
    message: str
