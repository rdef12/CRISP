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
    
    photo_id_array = take_multiple_videos(request_body)
    photo_bytes_array = []
    for photo_id in photo_id_array:
        photo_bytes = cdi.get_photo_from_id(photo_id)
        photo_bytes_array.append(base64.b64encode(photo_bytes).decode('utf-8'))

    return {"photo_bytes_array": photo_bytes_array}