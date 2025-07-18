import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import pytz # affected by daylight saving?
import base64
from typing import List
from src.classes.Pi import Pi


from src.viewing_functions import *
from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.create_homographies import *
from src.classes.Camera import ImageSettings, PhotoContext, CalibrationImageSettings, ImageTestSettings
from src.calibration_functions import ROI, determine_frame_size
from src.distortion_correction import distortion_calibration_test_for_gui, perform_distortion_calibration_from_database
from src.routers import setup as setup_router
from src.routers import setup_camera as setup_camera_router
from src.routers import camera as camera_router
from src.routers import settings as settings_router
from src.routers import camera_settings as camera_settings_router
from src.routers import photo as photo_router
from src.routers import video as video_router
from src.routers import experiment as experiment_router
from src.routers import beam_run as beam_run_router
from src.routers import homography as homography_router
from src.routers import camera_analysis as camera_analysis_router
from src.routers import homography_calibration as homography_calibration_router
from src.routers import camera_analysis_plot as camera_analysis_plot_router


from src.classes.JSON_request_bodies import request_bodies as rb

from src.database.CRUD import CRISP_database_interaction as cdi
from src.database.database import create_db_and_tables
from src.database.models import Camera as CameraTable, CameraSettingsLink

import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_host_IP_address()
    create_db_and_tables() 
    yield 
    print("API closed")

app = FastAPI(lifespan=lifespan)

# MOUNTING THE SPHINX DOCS FOR ACCESS BY THE FRONTEND
docs_path = os.path.join(os.path.dirname(__file__), "docs", "_build", "html")
# Serve the entire docs folder so all files (HTML, CSS, JS, etc.) are accessible
app.mount("/docs", StaticFiles(directory=docs_path, html=True), name="docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range"]
)

from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
def render_error_page(endpoint: str, title: str, heading: str, detail: str, status_code: int) -> HTMLResponse:
    return HTMLResponse(
        content=f"""
        <html>
            <head>
                <title>{title}</title>
            </head>
            <body style="margin: 0; font-family: Arial, sans-serif; background-color: #f2f2f2;">
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                    <div style="background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center; max-width: 600px;">
                        <h1 style="color: #e74c3c; font-size: 36px; margin-bottom: 3px;">{heading}</h1>
                        <h2 style="color: #555; font-size: 18px; margin-bottom: 10px; font-weight: bold;">{endpoint}</h2>
                        <p style="color: #555; font-size: 18px;">{detail}</p>
                    </div>
                </div>
            </body>
        </html>
        """,
        status_code=status_code,
    )

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    endpoint = request.url.path
    if exc.status_code == 404:
        return render_error_page(endpoint, "Page Not Found", "404 - Not Found", exc.detail, 404)
    elif exc.status_code == 500:
        return render_error_page(endpoint, "Internal Server Error", "500 - Internal Server Error", exc.detail, 500)
    elif exc.status_code == 400:
        return render_error_page(endpoint, "Bad Request", "400 - Bad Request", exc.detail, 400)
    else:
        return await http_exception_handler(request, exc)


app.include_router(setup_router.router)
app.include_router(setup_camera_router.router)
app.include_router(camera_router.router)
app.include_router(settings_router.router)
app.include_router(camera_settings_router.router)
app.include_router(photo_router.router)
app.include_router(video_router.router)
app.include_router(experiment_router.router)
app.include_router(beam_run_router.router)
app.include_router(homography_router.router)
app.include_router(camera_analysis_router.router)
app.include_router(homography_calibration_router.router)
app.include_router(camera_analysis_plot_router.router)

@app.get("/get_pi_disk_space/{username}")
def get_pi_disk_space_api(username: str):
    if connected_pi := Pi.get_pi_with_username(username): 
        return {"used space / total space": connected_pi.get_pi_disk_space()}
    return {"Error": "No Pi connected with that username"}

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

@app.put("/update_pi/{username}")
def update_pi(username: str, update_body: rb.CameraPutRequestBody):
    with Session(engine) as session:
        camera_statement = select(CameraTable).where(CameraTable.username == username)
        camera = session.exec(camera_statement).one()
        camera.ip_address = update_body.IPAddress
        camera.model = update_body.cameraModel
        session.commit()
        return {"message": f"Raspberry pi with username {username} updated with IP Address {camera.ip_address} and model {camera.model}"}

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

@app.get("/get_pi_status/{username}")
def get_pi_status_api(username: str):
    pi_status = get_single_pi_status(username)
    return JSONResponse(content=pi_status)

@app.post("/connect_over_ssh/{username}")
def connect_over_ssh_api(username: str):
    connection_status = connect_over_ssh(username)
    return {"sshStatus": connection_status}

@app.post("/disconnect_from_ssh/{username}")
def disconnect_from_ssh_api(username: str):
    return {"sshStatus": disconnect_from_ssh(username)}

@app.post("/take_single_test_picture/{username}")
def take_single_test_picture_api(username: str, imageSettings: ImageTestSettings):
    context = PhotoContext.GENERAL
    photo_bytes, _ = take_single_image(username, imageSettings, context)
    if photo_bytes:
        return Response(content=photo_bytes, media_type="image/png")

@app.post("/take_single_picture/{username}")
def take_single_picture_api(username: str, imageSettings: ImageSettings):
    context = PhotoContext.GENERAL
    photo_bytes, _ = take_single_image(username, imageSettings, context)
    if photo_bytes:
        return Response(content=photo_bytes, media_type="image/png")

@app.post("/take_distortion_calibration_image/{username}/{image_count}")
def take_distortion_calibration_image_api(username: str, image_count: int,
                                          distortionImageSettings: CalibrationImageSettings):
    try:
        context = PhotoContext.GENERAL
        photo_bytes, _ = take_single_image(username, distortionImageSettings.to_image_settings(), context)
        if photo_bytes:
            image = load_image_byte_string_to_opencv(photo_bytes)
            calibration_results = distortion_calibration_test_for_gui(image, distortionImageSettings.calibrationGridSize,
                                                                    distortionImageSettings.calibrationTileSpacing,
                                                                    image_count)
            response = {
                "results": calibration_results,
                "image_bytes": base64.b64encode(photo_bytes).decode('utf-8')
            }
            return JSONResponse(content=response)
    except Exception as e:
        print(f"Error taking distortion calibration image: {e}")

@app.delete("/reset_distortion_calibration/{setup_id}/{username}")
def reset_distortion_calibration_api(setup_id, username):
    
    camera_id = cdi.get_camera_entry_with_username(username).id
    
    cdi.update_camera_matrix(camera_id, setup_id, None)
    cdi.update_distortion_coefficients(camera_id, setup_id, None)
    cdi.update_distortion_calibration_pattern_type(camera_id, setup_id, None)
    cdi.update_distortion_calibration_pattern_spacing(camera_id, setup_id, None)
    
    # Call something to delete all photos associated with camera setup link
    # Call something to delete camera setup link
    return {"message": "Distortion calibration reset"}


@app.post("/perform_distortion_calibration/{setup_id}/{username}")
def perform_distortion_calibration_api(setup_id, username):
    
    perform_distortion_calibration_from_database(setup_id, username)
    return {"message": "distortion calibration completed"}
    

@app.get("/stream/{username}")
def stream_api(username: str):
    # Might want to add a fastapi background task which waits until stream cleanup is needed
    return StreamingResponse(stream_video_feed(username),
                             media_type="multipart/x-mixed-replace; boundary=frame")
    

@app.post("/take_roi_picture/{setup_id}/{username}")
def take_roi_picture_api(setup_id: str, username: str, imageSettings: ImageSettings):

    # context = PhotoContext.GENERAL
    # camera_id = cdi.get_camera_entry_with_username(username).id
    # photo_bytes, photo_id = take_single_image(username, imageSettings, context)
    # cdi.update_scintillator_edges_photo_id(camera_id, setup_id, photo_id)
    
    # only temp encoding while using mock image
    with open("/code/temp_images/scintillator_top_image.jpeg", "rb") as img_file:
        photo_bytes = img_file.read()

    height, width = get_image_bytestring_frame_size(photo_bytes)
    
    response = {
            "image_bytes": base64.b64encode(photo_bytes).decode('utf-8'),
            "width": width,
            "height": height
        }
    return JSONResponse(content=response)


@app.get("/load_roi_image/{setup_id}/{username}")
def load_roi_image_api(setup_id: str, username: str):
    
    # camera_id = cdi.get_camera_entry_with_username(username).id
    # setup_id = int(setup_id)
    # photo_id = scintillator_edges_photo_id(camera_id, setup_id)
    # image_bytes = cdi.get_photo_from_id(photo_id)
    
    # only temp encoding while using mock image
    with open("/code/temp_images/scintillator_top_image.jpeg", "rb") as img_file:
        photo_bytes = img_file.read()

    height, width = get_image_bytestring_frame_size(photo_bytes)
    response = {
            "image_bytes": base64.b64encode(photo_bytes).decode('utf-8'),
            "width": width,
            "height": height
        }
    return JSONResponse(content=response)
    

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


@app.post("/multiple_picture_test")
def multiple_picture_test_api(username_list: List[str]):
    context = PhotoContext.GENERAL
    
    # DEFINE BASIC IMAGESETTINGS HERE AS DEMO
    demo_settings = [ImageSettings(filename="multiple_image_test", gain=1, timeDelay=500, format="jpeg")] * len(username_list)
    output = take_multiple_images(username_list, demo_settings, context)
    
    photo_bytestring_list = list(output[:, 0]) # Slice this to get just an array of photobytes.
    
    encoded_images = [base64.b64encode(photo).decode('utf-8') for photo in photo_bytestring_list]
    response = {"images": encoded_images}
    return JSONResponse(content=response)


#############################################################################################################

import glob

class DirectoryOfPopulation(BaseModel):
    directory: str

def read_image_as_bytes(image_path: str):
    try:
        with open(image_path, "rb") as file:
            image_bytes = file.read()
        return image_bytes
    except FileNotFoundError as e:
        raise FileNotFoundError(f"FileNotFoundError: {e}") from e

@app.post("/fill-data/beam-run/{beam_run_id}/camera/{camera_id}")
def fill_photos_for_beam_run(beam_run_id: int, camera_id: int, directory: DirectoryOfPopulation):
    """
    {
      "directory": "./test_population_images/topHQ/" (camera id 2) or /sideAR/ (Camera id 1) make sure to match the camera id in the url
    }
    """
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                                    .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                    .where(CameraSettingsLink.camera_id == camera_id))
        camera_settings = session.exec(camera_settings_statement).one()
        camera_settings_id = camera_settings.id
        general_file_name = directory.directory + "*.jp*g"
        file_names = glob.glob(general_file_name)
        for file_name in file_names:
            photo_bytes = read_image_as_bytes(file_name)
            cdi.add_photo(camera_settings_id, photo_bytes)