import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import base64

from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.Camera import ImageSettings, PhotoContext
from src.calibration_functions import ROI, save_roi, determine_frame_size

from src.database.database import create_db_and_tables

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_host_IP_address()
    print(os.getenv("LOCAL_IP_ADDRESS"))
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
    return pi_status_array

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
    photo_bytes = take_single_image(username, imageSettings, context)
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
    
@app.post("/mock_roi_pic/{username}")
def mock_roi_pic_api(username: str, imageSettings: ImageSettings):

        # only temp encoding while using mock image
        with open("/code/temp_images/scintillator_top_image.jpeg", "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
            
        height, width = determine_frame_size(image_path="/code/temp_images/scintillator_top_image.jpeg")
        
        print(height, width)
        
        return ImageResponse(
        image_bytes=encoded_image,
        width=width,
        height=height
    )
        

@app.post("/save_scintillator_edges/{username}")
def save_scintillator_edges_api(username, submittedROI: ROI):
    
    # Round slider values to nearest int - pixel indices must be ints - done on frontend!
    save_roi(submittedROI) # Save ROI vals to database
    print(submittedROI)
    
    return {"message": "ROI boundaries saved"}
    
    
    
