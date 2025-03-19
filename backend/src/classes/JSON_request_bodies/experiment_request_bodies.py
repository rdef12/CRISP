from datetime import datetime
from pydantic import BaseModel

from src.database.models import Camera, Setup

class ExperimentCreateRequest(BaseModel):
    experiment_name: str
    setup_id: int


class ExperimentalSetupRequest(BaseModel):
    id: int
    name: str
    date_started: datetime
    setup_id: int
    setup: Setup
    cameras: list[Camera]
    