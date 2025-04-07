from typing import List, Optional
from pydantic import BaseModel

from src.database.models import CameraAnalysis

class CameraAnalysisPostPayload(BaseModel):
    colour_channel: str

class CameraAnalysisPostResponse(BaseModel):
    id: int


class CameraAnalysisGetReponse(BaseModel):
    id: int
    cameraSettingsId: Optional[int] = None
    colourChannel: Optional[str] = None
    averageImage: Optional[bytes] = None
    beamAngle: Optional[float] = None
    beamAngleUncertainty: Optional[float] = None
    braggPeakPixel: Optional[List[float]] = None
    braggPeakPixelUncertainty: Optional[List[float]] = None
    plots: Optional[List[str]] = None
    
