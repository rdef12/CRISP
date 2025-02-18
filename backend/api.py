import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.Camera import ImageSettings

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_host_IP_address()
    print(os.getenv("LOCAL_IP_ADDRESS"))
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
    configure_pi(pi_config)
    return {"message": "Pi configured successfully", "data": pi_config}

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

@app.post("/connect_over_ssh_{username}")
def connect_over_ssh_api(username: str):
    return {"sshStatus": connect_over_ssh(username)}

@app.post("/disconnect_from_ssh_{username}")
def disconnect_from_ssh_api(username: str):
    return {"sshStatus": disconnect_from_ssh(username)}

@app.post("/take_single_picture_{username}")
def take_single_picture_api(username: str, imageSettings: ImageSettings):
    if (filepath := take_single_picture(username, imageSettings)):  
        return FileResponse(filepath)
    
@app.get("/stream_{username}")
def stream_api(username: str):
    # Might want to add a fastapi background task which waits until stream cleanup is needed
    return StreamingResponse(stream_video_feed(username),
                             media_type="multipart/x-mixed-replace; boundary=frame")
