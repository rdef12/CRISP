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
def take_video(request_body: Dict[str, rb.MainVideoSettings]):
    """
    Possible that we want setup_id as a route variable in the future.
    
    Request body is a hashmap with username/camera id as the key,
    and video settings as the value
    """
    
    camera_settings_link_id_array = [1, 2, 3, 4] # TODO - might not work anymore since I changed so link not made inside Camera class method
    photo_id_dictionary = take_multiple_videos_for_main_run(request_body, camera_settings_link_id_array)
    photo_bytes_array = []
    for photo_id_array in photo_id_dictionary.values():
        for photo_id in photo_id_array:
            photo_bytes = cdi.get_photo_from_id(photo_id)
            photo_bytes_array.append(base64.b64encode(photo_bytes).decode('utf-8'))

    return {"photo_bytes_array": photo_bytes_array}