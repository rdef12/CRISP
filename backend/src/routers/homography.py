from fastapi import Response, APIRouter

from src.camera_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb
from src.database.CRUD import CRISP_database_interaction as cdi
from src.classes.Camera import PhotoContext, CalibrationImageSettings
from src.create_homographies import *
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/homography",
    tags=["homography"],
)

@router.post("/take_homography_calibration_image/{setup_id}/{username}/{plane_type}")
def take_homography_calibration_image_api(setup_id: str, username: str, plane_type: str,
                                          homographyImageSettings: CalibrationImageSettings):
    try:
        context = PhotoContext.GENERAL
        pattern_type = "chessboard" #TODO - add setting to frontend as an option?
        camera_id = cdi.get_camera_entry_with_username(username).id
        
        photo_bytes, _ = take_single_image(username, homographyImageSettings.to_image_settings(), context)
        if photo_bytes:
            match plane_type:
                case "far":
                    cdi.update_far_face_calibration_pattern_size(camera_id, setup_id, homographyImageSettings.calibrationGridSize)
                    cdi.update_far_face_calibration_pattern_type(camera_id, setup_id, pattern_type)
                    cdi.update_far_face_calibration_spacing(camera_id, setup_id, homographyImageSettings.calibrationTileSpacing)
                    cdi.update_far_face_calibration_spacing_unc(camera_id, setup_id, homographyImageSettings.calibrationTileSpacingErrors)
                case "near":
                    cdi.update_near_face_calibration_pattern_size(camera_id, setup_id, homographyImageSettings.calibrationGridSize)
                    cdi.update_near_face_calibration_pattern_type(camera_id, setup_id, pattern_type)
                    cdi.update_near_face_calibration_spacing(camera_id, setup_id, homographyImageSettings.calibrationTileSpacing)
                    cdi.update_near_face_calibration_spacing_unc(camera_id, setup_id, homographyImageSettings.calibrationTileSpacingErrors)
            
            response = test_grid_recognition_for_gui(username, setup_id, plane_type, photo_bytes=photo_bytes)
        return JSONResponse(content=response)
    except Exception as e:
        print(f"Error taking homography calibration image: {e}")
        

@router.post("/perform_homography_calibration/{setup_id}/{username}/{plane_type}")
def perform_homography_calibration_image_api(setup_id: str, username: str, plane_type: str,
                                             transforms: ImagePointTransforms):
    try:
        # camera_id = cdi.get_camera_id_from_username(username)
        # match plane_type:
        #     case "far":
        #         photo_bytes = cdi.get_far_face_calibration_photo(camera_id, setup_id)
        #     case "near":
        #         photo_bytes = cdi.get_near_face_calibration_photo(camera_id, setup_id)
                
        photo_id = 321
        photo_bytes = cdi.get_photo_from_id(photo_id)
                
        status = perform_homography_calibration(username, setup_id, plane_type, transforms, photo_bytes=photo_bytes)
    except Exception as e:
        print(f"Error performing homography calibration: {e}")
        status = False
    
    return {"status": status}
    



@router.post("/flip_homography_origin_position/{setup_id}/{username}/{plane_type}")
def flip_homography_origin_position_api(setup_id: str, username: str, plane_type: str, 
                                        transforms: ImagePointTransforms):
    """
    Image need not be taken again in this case
    """
    # camera_id = cdi.get_camera_id_from_username(username)
    # match plane_type:
    #     case "far":
    #         photo_bytes = cdi.get_far_face_calibration_photo(camera_id, setup_id)
    #     case "near":
    #         photo_bytes = cdi.get_near_face_calibration_photo(camera_id, setup_id)
    
    photo_id = 321
    photo_bytes = cdi.get_photo_from_id(photo_id)
    
    response = test_grid_recognition_for_gui(username, setup_id, plane_type, transforms, photo_bytes=photo_bytes)
    return JSONResponse(content=response)


################ FOR TESTING HOMOGRAPHY PINPOINTING SCRIPT WORKS #############################


@router.get("/add_mock_homography_images")
def add_mock_homography_images_api():
    
    # Arbitrary settings choice because only interested in the images
    # Use raspi4b3 for the username/camera ID
    
    added_settings = cdi.add_settings(frame_rate=5, lens_position=0.5, gain=1)
    settings_id = added_settings["id"] # Do I need to make a uique one for each settings?
    camera_id = cdi.get_camera_id_from_username("raspi4b3")
    
    side_far_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id) # same args so same link?
    side_near_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id)
    side_far_photo_camera_settings_link_id = side_far_photo_camera_settings_link["id"]
    side_near_photo_camera_settings_link_id = side_near_photo_camera_settings_link["id"]
    
    with open("/code/src/calibration_testing_19_11_24/side_arducam_front_chessboard_calibration_20_by_10_spacing_10mm.jpeg", "rb") as img_file:
        side_near_photo_bytes = img_file.read()
    with open("/code/src/calibration_testing_19_11_24/side_arducam_back_chessboard_calibration_20_by_10_spacing_10mm.jpeg", "rb") as img_file:
        side_far_photo_bytes = img_file.read()
    
    side_far_photo = cdi.update_photo(camera_settings_link_id=side_far_photo_camera_settings_link_id, photo=side_far_photo_bytes)
    side_far_photo_id = side_far_photo["id"]
    side_near_photo = cdi.update_photo(camera_settings_link_id=side_near_photo_camera_settings_link_id, photo=side_near_photo_bytes)
    side_near_photo_id = side_near_photo["id"]
    
    top_far_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id) # same args so same link?
    top_near_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=camera_id, settings_id=settings_id)
    top_far_photo_camera_settings_link_id = top_far_photo_camera_settings_link["id"]
    top_near_photo_camera_settings_link_id = top_near_photo_camera_settings_link["id"]
    
    with open("/code/src/calibration_testing_19_11_24/top_hq_front_chessboard_calibration_20_by_5_spacing_10mm.jpeg", "rb") as img_file:
        top_near_photo_bytes = img_file.read()
    with open("/code/src/calibration_testing_19_11_24/top_hq_back_chessboard_calibration_20_by_5_spacing_10mm.jpeg", "rb") as img_file:
        top_far_photo_bytes = img_file.read()
    
    top_far_photo = cdi.update_photo(camera_settings_link_id=top_far_photo_camera_settings_link_id, photo=top_far_photo_bytes)
    top_far_photo_id = top_far_photo["id"]
    top_near_photo = cdi.update_photo(camera_settings_link_id=top_near_photo_camera_settings_link_id, photo=top_near_photo_bytes)
    top_near_photo_id = top_near_photo["id"]
    
    return {"message": f"successfully saved images to database. Photo IDs are {side_far_photo_id, side_near_photo_id, top_far_photo_id, top_near_photo_id}"}


@router.get("/homography_pinpointing_test")
def homography_pinpointing_test_api():
    
    
    return {"message": None}