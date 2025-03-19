from fastapi import Response, APIRouter

from src.camera_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb
from src.database.CRUD import CRISP_database_interaction as cdi
from typing import Dict

router = APIRouter(
    prefix="/video",
    tags=["video"],
)

@router.post("/take_video")
def take_video(request_body: Dict[str, rb.VideoSettings]):
    """
    Possible that we want setup_id as a route variable in the future.
    
    Request body is a hashmap with username/camera id as the key,
    and video settings as the value
    """
    for username, video_settings in request_body.items():
        take_single_video(username, video_settings)
    
    return None