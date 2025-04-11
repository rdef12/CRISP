from pydantic import BaseModel
from typing import Optional

class PhotoDeleteResponse(BaseModel):
    id: int

class ScintillatorEdgePhotoGet(BaseModel):
    id: int #setup camera id
    camera_settings_id: Optional[int] = None
    photo: Optional[bytes] = None
    height: Optional[int] = None
    width: Optional[int] = None

class DistortionCalibrationPhotoPost(BaseModel):
    id: int #setup camera id
    photo: bytes
    calibration_status: bool
    message: str

class DistortionCalibrationSaveRequest(BaseModel):
    photo: bytes

class DistortionCalibrationSaveResponse(BaseModel):
    id: int


class HomographyCalibrationPhotoGetResponse(BaseModel):
    id: int
    photo: Optional[bytes] = None
    status: Optional[bool] = None
    message: Optional[str] = None

class TestRunPhotoGet(BaseModel):
    id: int #camera_settings_id
    photo: bytes


class RealRunPhotoGet(BaseModel):
    id: int
    camera_id: int
    photo: bytes

class RealRunPhotoPostResponse(BaseModel):
    id: int
