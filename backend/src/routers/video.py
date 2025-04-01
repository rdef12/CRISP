from fastapi import Response, APIRouter
from fastapi.responses import HTMLResponse
import base64
from datetime import datetime
import pytz

from src.camera_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb
from src.database.CRUD import CRISP_database_interaction as cdi
from typing import Dict

router = APIRouter(
    prefix="/video",
    tags=["video"],
)

################### OLD APPROACH ######################

# @router.post("/take_video")
# def take_video(request_body: Dict[str, rb.MainVideoSettings]):
#     """
#     Possible that we want setup_id as a route variable in the future.
    
#     Request body is a hashmap with username/camera id as the key,
#     and video settings as the value
#     """
    
#     camera_settings_link_id_array = [1, 2, 3, 4] # TODO - might not work anymore since I changed so link not made inside Camera class method
#     photo_id_dictionary = take_multiple_videos_for_main_run(request_body, camera_settings_link_id_array)
#     photo_bytes_array = []
#     for photo_id_array in photo_id_dictionary.values():
#         for photo_id in photo_id_array:
#             photo_bytes = cdi.get_photo_from_id(photo_id)
#             photo_bytes_array.append(base64.b64encode(photo_bytes).decode('utf-8'))

#     return {"photo_bytes_array": photo_bytes_array}


@router.get("/trial_main_run_video")
def trial_main_run_video_api():
    
    setup_id = 1
    current_time = datetime.now(pytz.utc)
    experiment_id = cdi.add_experiment("trial_main_run_video", current_time, setup_id)["id"]
    print(f"experiment_id: {experiment_id}")
    
    camera_id = cdi.get_camera_id_from_username("lewisdean22")
    print(f"camera_id: {camera_id}")
    settings_id = cdi.add_settings(frame_rate=20, lens_position=5, gain=5)["id"]
    print(f"settings_id: {settings_id}")
    
    beam_run_id = cdi.add_beam_run(experiment_id=experiment_id, beam_run_number=1, 
                                   datetime_of_run=current_time, 
                                   ESS_beam_energy=150, beam_current=100, 
                                   beam_current_unc=0.1, is_test=False).id
    
    camera_settings_link_id =  cdi.add_camera_settings_link_with_beam_run(camera_id, settings_id, beam_run_id)["id"]
    print(f"camera_settings_link_id: {camera_settings_link_id}")
    
    photo_id_array = take_single_video_for_main_run(camera_settings_link_id)
    img_tags = ""
    for photo_id in photo_id_array:
        photo_bytes = cdi.get_photo_from_id(photo_id)
        photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
        img_tags += f'<img src="data:image/png;base64,{photo_base64}" width="200px"><br>'

    html_content = f"<html><body>{img_tags}</body></html>"
    return HTMLResponse(content=html_content)


@router.get("/trial_test_run_video")
def trial_test_run_video_api():
    
    setup_id = 1
    current_time = datetime.now(pytz.utc)
    experiment_id = cdi.add_experiment("trial_test_run_video", current_time, setup_id)["id"]
    print(f"experiment_id: {experiment_id}")
    
    beam_run_id = cdi.add_beam_run(experiment_id=experiment_id, beam_run_number=1, 
                                   datetime_of_run=current_time, 
                                   ESS_beam_energy=150, beam_current=100, 
                                   beam_current_unc=0.1, is_test=True).id
    
    camera_id = cdi.get_camera_id_from_username("lewisdean22")
    print(f"camera_id: {camera_id}")
    
    # Create the camera settings link ids
    gain_list = np.arange(1, 11, 1).astype(float).tolist() # argparse cannot handle np.float64
    camera_settings_link_id_array = []
    for gain in gain_list:
        settings_id = cdi.add_settings(frame_rate=20, lens_position=5, gain=gain)["id"]
        camera_settings_link_id =  cdi.add_camera_settings_link_with_beam_run(camera_id, settings_id, beam_run_id)["id"]
        camera_settings_link_id_array.append(camera_settings_link_id)
    
    print(f"camera_settings_link_id_array: {camera_settings_link_id_array}")
    photo_id_array = take_single_video_for_test_run(camera_settings_link_id_array)
    img_tags = ""
    for photo_id in photo_id_array:
        photo_bytes = cdi.get_photo_from_id(photo_id)
        photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")
        img_tags += f'<img src="data:image/png;base64,{photo_base64}" width="200px"><br>'

    html_content = f"<html><body>{img_tags}</body></html>"
    return HTMLResponse(content=html_content)