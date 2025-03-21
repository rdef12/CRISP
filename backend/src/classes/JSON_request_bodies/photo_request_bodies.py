from pydantic import BaseModel
from typing import Optional

class ScintillatorEdgePhotoGet(BaseModel):
    id: int
    camera_settings_id: Optional[int]
    photo: Optional[bytes]
    height: Optional[int]
    width: Optional[int]