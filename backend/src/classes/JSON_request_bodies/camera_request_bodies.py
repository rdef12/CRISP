from pydantic import BaseModel

from src.database.models import Camera, CameraSettingsLink, Photo, Settings

class CameraStatusResponse(BaseModel):
    id: int
    username: str
    IPAddress: str
    cameraModel: str
    connectionStatus: bool

class CameraPutRequestBody(BaseModel):
    IPAddress: str
    cameraModel: str
