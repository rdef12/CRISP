import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
from datetime import datetime
import pytz # affected by daylight saving?
import base64


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.Camera import ImageSettings, PhotoContext
from src.calibration_functions import ROI, determine_frame_size

from src.classes.JSON_request_bodies import request_bodies as rb

from src.database.CRUD import CRISP_database_interaction as cdi
from src.database.database import create_db_and_tables

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_host_IP_address()
    create_db_and_tables() 
    yield 
    print("API closed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/add_pi")
async def add_pi(pi_config: PiConfig):
    camera_id = configure_pi(pi_config)
    return {"message": "Pi configured successfully",
            "data": pi_config,
            "camera_id": camera_id}

@app.post("/remove_pi_{username}")
async def remove_pi(username: str):
    remove_configured_pi(username)
    return {"message": "Pi configuration successfully deleted"}

@app.get("/health")
def heath_check():
    return {"healthCheckStatus": "healthy"}

@app.get("/get_raspberry_pi_statuses")
def get_raspberry_pi_statuses_api():
    pi_status_array = get_raspberry_pi_statuses()
    # Create a JSONResponse with no caching headers
    response = JSONResponse(content=[status.dict() for status in pi_status_array])
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

@app.post("/connect_over_ssh/{username}")
def connect_over_ssh_api(username: str):
    connection_status = connect_over_ssh(username)
    return {"sshStatus": connection_status}

@app.post("/disconnect_from_ssh/{username}")
def disconnect_from_ssh_api(username: str):
    return {"sshStatus": disconnect_from_ssh(username)}

@app.post("/take_single_picture/{username}") #TODO Add saving to database
def take_single_picture_api(username: str, imageSettings: ImageSettings):
    context = PhotoContext.GENERAL
    photo_bytes, _ = take_single_image(username, imageSettings, context)
    if photo_bytes:
        return Response(content=photo_bytes, media_type="image/png")

    
@app.get("/stream/{username}")
def stream_api(username: str):
    # Might want to add a fastapi background task which waits until stream cleanup is needed
    return StreamingResponse(stream_video_feed(username),
                             media_type="multipart/x-mixed-replace; boundary=frame")
    
    
class ImageResponse(BaseModel):
    image_bytes: str
    width: int
    height: int

@app.post("/take_roi_picture/{setup_id}/{username}")
def take_roi_picture_api(setup_id: str, username: str, imageSettings: ImageSettings):

    # context = PhotoContext.GENERAL
    # camera_id = cdi.get_camera_entry_with_username(username).id
    # photo_bytes, photo_id = take_single_image(username, imageSettings, context)
    # cdi.update_scintillator_edges_photo_id(camera_id, setup_id, photo_id)
    
    # only temp encoding while using mock image
    with open("/code/temp_images/scintillator_top_image.jpeg", "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

    height, width = get_image_bytestring_frame_size(encoded_image)
    
    return ImageResponse(
    image_bytes=encoded_image,
    width=width,
    height=height
)
    
@app.get("/load_roi_image/{setup_id}/{username}")
def load_roi_image_api(setup_id: str, username: str):
    
    # camera_id = cdi.get_camera_entry_with_username(username).id
    # setup_id = int(setup_id)
    # photo_id = scintillator_edges_photo_id(camera_id, setup_id)
    # image_bytes = cdi.get_photo_from_id(photo_id)
    
    with open("/code/temp_images/scintillator_top_image.jpeg", "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

    height, width = get_image_bytestring_frame_size(encoded_image)
    
    return ImageResponse(
    image_bytes=encoded_image,
    width=width,
    height=height
    )
    

@app.get("/get_setups")
def get_setups_api():
    setups = cdi.get_all_cameras
    return setups

@app.post("/add_setup")
def add_setup_api(setup_name: rb.SetupCreateRequest):
    datetime_of_creation = datetime.now(pytz.utc)
    # Needed to add key on the end because json returned by CRUD
    setup_id = cdi.add_setup(setup_name=setup_name.setup_name,
                             date_created=datetime_of_creation,
                             date_last_edited=datetime_of_creation).get("id")
    
    return {"message": f"Setup with name {setup_name} successfully added.",
            "setup_id": setup_id}


    
@app.post("/save_scintillator_edges/{setup_id}/{username}")
def save_scintillator_edges_api(setup_id, username, submittedROI: ROI):
    
    camera_id = cdi.get_camera_entry_with_username(username).id
    setup_id = int(setup_id)
    
    cdi.update_horizontal_scintillator_scintillator_limits(camera_id, setup_id, (submittedROI.hStart, submittedROI.hEnd))
    cdi.update_vertical_scintillator_limits(camera_id, setup_id, (submittedROI.vStart, submittedROI.vEnd))
    return {"message": "ROI boundaries saved"}
    
