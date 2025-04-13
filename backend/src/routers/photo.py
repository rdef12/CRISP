from datetime import datetime
from fastapi import HTTPException, Response, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.create_homographies import ImagePointTransforms, test_grid_recognition_for_gui
from src.gain_automation import ColourChannel, set_optimal_settings, show_saturated_points
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.distortion_correction import distortion_calibration_test_for_gui, perform_distortion_calibration_from_database
from src.classes.JSON_request_bodies import request_bodies as rb


from src.database.models import BeamRun, Camera, CameraSettingsLink, CameraSetupLink, Experiment, Photo, Settings
from src.classes import Camera as PiCamera #TODO This may be a bit awkward
from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/photo",
    tags=["photo"],
)

@router.delete("/{photo_id}")
def delete_photo_by_id_api(photo_id: int):
    cdi.delete_photo_by_id(photo_id)
    return rb.PhotoDeleteResponse(id=photo_id)

# @router.post("scintillator-edges/{setup_camera_id}")
# def take_picture(setup_camera_id: str):
#     with Session(engine) as session:
#         statement = select()
#     camera_settings_link = 
#     settings_id = cdi.get_settings_by_setup_camera_id
#     context = PhotoContext.GENERAL
#     camera_id = cdi.get_camera_id_from_username(self.username)
#     added_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id)
#     camera_settings_link_id = added_camera_settings_link["id"]
#     photo_bytes, _ = take_single_image(username, imageSettings, context)
#     if photo_bytes:
#         return Response(content=photo_bytes, media_type="image/png")
    


def take_scintillator_edge_image(username: str, camera_settings_id:int, imageSettings: ImageSettings, context: PhotoContext):
    
    try:
        # Should have already validated the fact that Pis with these usernames are connected via SSH.
        # Pi with this username will have been deleted after SSH check if it disconnected.
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi instantiated with the username {username}")
        full_file_path = pi.camera.capture_image_without_making_settings(camera_settings_id, imageSettings, context)
        added_photo_id = pi.camera.transfer_image_overwrite(imageSettings, camera_settings_id, full_file_path)
        return added_photo_id
    
    except Exception as e:
        raise Exception(f"Error trying to take a picture: {e}")
    

def take_distortion_calibration_image(username: str, camera_settings_id:int, imageSettings: ImageSettings, context: PhotoContext):
    
    try:
        # Should have already validated the fact that Pis with these usernames are connected via SSH.
        # Pi with this username will have been deleted after SSH check if it disconnected.
        if (pi := Pi.get_pi_with_username(username)) is None:
            raise Exception(f"No pi instantiated with the username {username}")
        full_file_path = pi.camera.capture_image_without_making_settings(camera_settings_id, imageSettings, context)
        photo_bytes = pi.camera.transfer_image_without_writing_to_database(imageSettings, camera_settings_id, full_file_path)
        return photo_bytes
    
    except Exception as e:
        raise Exception(f"Error trying to take a picture: {e}")

def get_camera_and_settings_by_camera_settings_id(camera_settings_id: int) -> tuple[Camera, Settings]:
    with Session(engine) as session:
        camera_settings = session.get(CameraSettingsLink, camera_settings_id)
        settings = session.get(Settings, camera_settings.settings_id)
        camera = session.get(Camera, camera_settings.camera_id)
    return camera, settings

@router.post("/scintillator-edges/{setup_camera_id}")
def take_picture(setup_camera_id: int):
    camera_settings_id = None
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_settings_id = setup_camera.scintillator_edges_photo_camera_settings_id
    
    try:
        current_photo = cdi.get_photo_from_camera_settings_link_id(camera_settings_id)
        cdi.delete_photo_by_id(current_photo.id)
    except:
        pass
    camera, settings = get_camera_and_settings_by_camera_settings_id(camera_settings_id)
    
    filename = "scintillator_edge"
    gain = settings.gain #TODO Other settings need adding to ImageSettings
    timeDelay = 1
    format = "jpeg"
    image_settings = ImageSettings(filename=filename, gain=gain, timeDelay=timeDelay, format=format)
    photo_id = take_scintillator_edge_image(camera.username, camera_settings_id, image_settings, PhotoContext.GENERAL)
    cdi.update_scintillator_edges_camera_settings_id(setup_camera_id, camera_settings_id)
    return {"id": photo_id} #TODO is this id going to cause problems???


def get_image_bytestring_frame_size(image_byte_string: str):
    image = load_image_byte_string_to_opencv(image_byte_string)
    return determine_frame_size(image=image)

@router.get("/scintillator-edges/{setup_camera_id}")
def get_scintillator_edge_photo_data(setup_camera_id: int):
    camera_settings_id = None
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_settings_id = setup_camera.scintillator_edges_photo_camera_settings_id
    try:
        photos = cdi.get_photo_from_camera_settings_link_id(camera_settings_id)
    except ValueError as e:
        print(f"{e}")
        null_photo_response = rb.ScintillatorEdgePhotoGet(id=setup_camera_id,
                                                          camera_settings_id=None,
                                                          photo=None,
                                                          height=None,
                                                          width=None)
        return null_photo_response
    if len(photos) == 0:
        null_photo_response = rb.ScintillatorEdgePhotoGet(id=setup_camera_id,
                                                          camera_settings_id=None,
                                                          photo=None,
                                                          height=None,
                                                          width=None)
        return null_photo_response
    if len(photos) > 1:
        raise Exception("Multiple Scintillator Edge Pictures have been found")
    photo = photos[0]
    height, width = get_image_bytestring_frame_size(photo.photo)
    photo_base64 = base64.b64encode(photo.photo).decode("utf-8")
    photo_response = rb.ScintillatorEdgePhotoGet(id=setup_camera_id, #TODO This is janky, really this should be meta data in a setup camera body
                                                 camera_settings_id=photo.camera_settings_link_id,
                                                 photo=photo_base64,
                                                 height=height,
                                                 width=width)
    return photo_response



@router.post("/distortion-calibration/{setup_camera_id}")
def take_picture(setup_camera_id: int):
    camera_settings_id = None
    grid_size_z_dim = None
    grid_size_non_z_dim = None
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_settings_id = setup_camera.distortion_calibration_camera_settings_link
        grid_size_z_dim = setup_camera.distortion_calibration_pattern_size_z_dim
        grid_size_non_z_dim = setup_camera.distortion_calibration_pattern_size_non_z_dim

    camera, settings = get_camera_and_settings_by_camera_settings_id(camera_settings_id)
    
    photos = cdi.get_photo_from_camera_settings_link_id(camera_settings_id)
    number_of_photos = len(photos)
    current_photo_number = number_of_photos + 1

    filename = f"distortion_calibration_{current_photo_number}"
    gain = settings.gain #TODO Other settings need adding to ImageSettings
    timeDelay = 1
    format = "jpeg"
    image_settings = ImageSettings(filename=filename, gain=gain, timeDelay=timeDelay, format=format)
    photo_bytes = take_distortion_calibration_image(camera.username, camera_settings_id, image_settings, PhotoContext.GENERAL)
    
    if photo_bytes is None:
        raise Exception
    image = load_image_byte_string_to_opencv(photo_bytes)
    calibration_results = distortion_calibration_test_for_gui(image,
                                                                (grid_size_z_dim, grid_size_non_z_dim),
                                                                image_count=current_photo_number)
    photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")

    response = rb.DistortionCalibrationPhotoPost(id=setup_camera_id,
                                                 photo=photo_base64,
                                                 calibration_status=calibration_results["status"],
                                                 message=calibration_results["message"])
    return response

@router.post("/distortion-calibration/save/{setup_camera_id}")
def save_distortion_image_to_database(setup_camera_id: int, distortion_photo_body: rb.DistortionCalibrationSaveRequest):
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_settings_id = setup_camera.distortion_calibration_camera_settings_link
        photo_id = cdi.add_photo(camera_settings_id, distortion_photo_body.photo)["id"]
    return rb.DistortionCalibrationSaveResponse(id=setup_camera_id)

@router.get("/distortion-calibration/{setup_camera_id}")
def get_all_distortion_calibration_images(setup_camera_id: int, response: Response):
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_settings_id = setup_camera.distortion_calibration_camera_settings_link
        distortion_calibration_images = cdi.get_photo_from_camera_settings_link_id(camera_settings_id)
        response.headers["Content-Range"] = str(len(distortion_calibration_images))
        return distortion_calibration_images

@router.post("/homography-calibration/{plane}/{setup_camera_id}")
def take_homography_calibration_image(plane: str, setup_camera_id: int):
    context = PhotoContext.GENERAL
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_id = setup_camera.camera_id
        setup_id = setup_camera.setup_id
        username = cdi.get_username_from_camera_id(camera_id)

        camera_settings_id = None
        if plane == "near":
            camera_settings_id = setup_camera.near_face_calibration_photo_camera_settings_id
        elif plane == "far":
            camera_settings_id = setup_camera.far_face_calibration_photo_camera_settings_id
        else:
            raise HTTPException(status_code=400, detail=f"Invalid plane: {plane}. Must be 'near' or 'far'.")
        
        old_photos_statement = select(Photo).where(Photo.camera_settings_link_id == camera_settings_id)
        old_photos = session.exec(old_photos_statement).all()
        for old_photo in old_photos:
            session.delete(old_photo)
        session.commit()

        camera_settings = session.get(CameraSettingsLink, camera_settings_id)

        settings = session.get(Settings, camera_settings.settings_id)

        filename = f"{plane}_plane_calibration"
        gain = settings.gain
        timeDelay = 1 # Hardcoded
        format = "jpg" # Hardcoded
        meta_data_format = "dng" # Hardcoded
        image_settings = ImageSettings(filename=filename,
                                       gain=gain,
                                       timeDelay=timeDelay,
                                       format=format,
                                       meta_data_format=meta_data_format)
        photo_bytes, _ = take_single_image(username, image_settings, context)
        photo_id = cdi.add_photo(camera_settings_id, photo_bytes)["id"]
        return JSONResponse(content={"id": setup_camera_id})

@router.get("/homography-calibration/{plane}/{setup_camera_id}")
def get_homography_calibration_image(plane: str, setup_camera_id: int,
                                     horizontal_flip: bool = False,
                                     vertical_flip: bool = False,
                                     swap_axes: bool = False):
    with Session(engine) as session:
        setup_camera = session.get(CameraSetupLink, setup_camera_id)
        camera_settings_id = None
        if plane == "near":
            camera_settings_id = setup_camera.near_face_calibration_photo_camera_settings_id
        elif plane == "far":
            camera_settings_id = setup_camera.far_face_calibration_photo_camera_settings_id
        else:
            raise HTTPException(status_code=400, detail=f"Invalid plane: {plane}. Must be 'near' or 'far'.")
        print(f"\n\n\n\n Camera setuigngs isd: {camera_settings_id}\n\n\n\n")
        photo_statement = select(Photo).where(Photo.camera_settings_link_id == camera_settings_id)
        
        photos = session.exec(photo_statement).all()
        if len(photos) == 0:
            print("SURES")
            return rb.HomographyCalibrationPhotoGetResponse(id=setup_camera_id)
        if len(photos) > 1:
            raise HTTPException(503, detail="Multiple photos found for homography calibration")
        photo = photos[0]
        # photo_bytes = photo.photo
        setup_id = setup_camera.setup_id
        camera_id = setup_camera.camera_id
        username = cdi.get_username_from_camera_id(camera_id)

        transforms = ImagePointTransforms(horizontal_flip=horizontal_flip,
                                          vertical_flip=vertical_flip,
                                          swap_axes=swap_axes)
        response = test_grid_recognition_for_gui(username, setup_id, plane, image_point_transforms=transforms, photo_id=photo.id)
        
        return rb.HomographyCalibrationPhotoGetResponse(id=setup_camera_id,
                                                        photo=response["image_bytes"],
                                                        status=response["status"],
                                                        message=response["message"])
# return {
#         "status": False,
#         "message": "Calibration pattern could not be recognised in the image",
#         "image_bytes": base64.b64encode(buffer).decode("utf-8")
# }

# return {
#     "status": True,
#     "message": "Calibration pattern succesfully recognised. Origin of coordinate system overlayed as a red circle.",
#     "image_bytes": image_bytes
# }

# @router.get("/beam-run/test/{beam_run_id}/camera-settings/{camera_settings_id}")
# def get_test_run_photo(beam_run_id: int, camera_settings_id: int):
#     with Session(engine) as session:
#         photo_statement = select(Photo).where(Photo.camera_settings_link_id == camera_settings_id)
#         photo = session.exec(photo_statement).one()
#         horizontal_start, horizontal_end, vertical_start, vertical_end = cdi.get_scintillator_edges_by_photo_id(photo.id)
#         image = load_image_byte_string_to_opencv(photo.photo)
#         image = show_saturated_points(image,
#                                         horizontal_start,
#                                         horizontal_end,
#                                         vertical_start,
#                                         vertical_end,
#                                         colour_channel=ColourChannel.RED)
#         photo_base64 = base64.b64encode(image).decode("utf-8")
#         return rb.TestRunPhotoGet(id=camera_settings_id,
#                                   photo=photo_base64)
    

@router.get("/beam-run/test/{beam_run_id}/camera-settings/{camera_settings_id}")
def get_test_run_overlays(camera_settings_id: int, response: Response):
    overlayed_images = [] 
    with Session(engine) as session:
        photo_statement = select(Photo).where(Photo.camera_settings_link_id == camera_settings_id)
        photo = session.exec(photo_statement).one()
        horizontal_start, horizontal_end, vertical_start, vertical_end = cdi.get_scintillator_edges_by_photo_id(photo.id)
        image = load_image_byte_string_to_opencv(photo.photo)
        for count, colour_channel in enumerate(ColourChannel):
            overlayed_image = show_saturated_points(image,
                                        horizontal_start,
                                        horizontal_end,
                                        vertical_start,
                                        vertical_end,
                                        colour_channel=colour_channel)
            overlayed_image_bytes = base64.b64encode(overlayed_image).decode("utf-8") 
            overlayed_images += [rb.TestRunPhotoGet(id=count, photo=overlayed_image_bytes)]
    response.headers["Content-Range"] = str(len(overlayed_images))
    return overlayed_images
            

@router.get("/beam-run/real/{beam_run_id}/camera/{camera_id}")
def get_real_run_photo(beam_run_id: int, camera_id: int, response: Response):
    with Session(engine) as session:
        photos_statement = (select(Photo)
                            .join(CameraSettingsLink)
                            .where(CameraSettingsLink.beam_run_id == beam_run_id)
                            .where(CameraSettingsLink.camera_id == camera_id))
        photos = session.exec(photos_statement).all()
        photo_list = []
        for photo in photos:
            photo_base64 = base64.b64encode(photo.photo).decode("utf-8")
            photo_list += [rb.RealRunPhotoGet(id=photo.id, camera_id=camera_id, photo=photo_base64)]
        response.headers["Content-Range"] = str(len(photo_list))
        
        return photo_list
    

@router.post("/beam-run/real/{beam_run_id}")
def take_real_beam_run_images(beam_run_id: int):
    all_camera_settings_ids = []
    with Session(engine) as session:
        camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        all_camera_settings = session.exec(camera_settings_statement).all()
        for camera_settings in all_camera_settings:
            all_camera_settings_ids += [camera_settings.id]
        
        experiment_statement = select(Experiment).join(BeamRun).join(CameraSettingsLink).where(CameraSettingsLink.id == all_camera_settings_ids[0]) #TODO a bit janky with [0]
        experiment = session.exec(experiment_statement).one()
        experiment_id = experiment.id  

        # TODO Maybe have a try here and return with the issue as well as what was completed??
        print("\n\n\n GONNA DO A THINGGY in realllllll")
        print(f"FOr my next trick i shall input experiment id {experiment_id} and all camera settings ids {all_camera_settings_ids}")
        print(f"Settings of {cdi.get_settings_by_id(cdi.get_settings_id_by_camera_settings_id(all_camera_settings_ids[0]))}")
        results_dict = take_multiple_videos_for_main_run(experiment_id, all_camera_settings_ids) #TODO Temporary [0] and single video for a little test
        print("DONE A THINGY \n\n\n")
        return rb.RealRunPhotoPostResponse(id=beam_run_id)

@router.post("/beam-run/test/{beam_run_id}")
def take_test_beam_run_images(beam_run_id: int):  
    with Session(engine) as session:
        camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        all_camera_settings = session.exec(camera_settings_statement).all()
        
        first_camera_settings = all_camera_settings[0] #TODO SHOULD THIS BE MORE BOMB PROOF
        experiment_statement = select(Experiment).join(BeamRun).join(CameraSettingsLink).where(CameraSettingsLink.id == first_camera_settings.id)
        experiment = session.exec(experiment_statement).one()
        experiment_id = experiment.id        
        camera_and_settings_ids = np.empty((len(all_camera_settings), 2), dtype=int)
        for count, camera_settings in enumerate(all_camera_settings):
            camera_id = camera_settings.camera_id
            camera_settings_id = camera_settings.id

            camera_and_settings_ids[count, 0] = camera_id
            camera_and_settings_ids[count, 1] = camera_settings_id

        unique_camera_ids = np.unique(camera_and_settings_ids[:, 0])
        grouped_camera_settings = [camera_and_settings_ids[camera_and_settings_ids[:, 0] == cam_id, 1].tolist() for cam_id in unique_camera_ids]

        # TODO Maybe have a try here and return with the issue as well as what was completed??
        print("\n\n\n About to take pictures")
        results_dict = take_multiple_videos_for_test_run(experiment_id, grouped_camera_settings) #TODO SHOULD BE MULTIPLE PRESUMABLY
        print(f"\n\n\n Pictures taken \n\n")
        
        for photo_id_array in results_dict.values():
            set_optimal_settings(photo_id_array, threshold=5) #TODO Blue channel hardcoded currently
        return rb.RealRunPhotoPostResponse(id=beam_run_id)
    
