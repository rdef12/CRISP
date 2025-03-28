from fastapi import Response, APIRouter

from src.camera_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb
from src.database.CRUD import CRISP_database_interaction as cdi
from src.classes.Camera import PhotoContext, CalibrationImageSettings
from src.create_homographies import *
from fastapi.responses import JSONResponse
from src.homography_pinpointing import perform_homography_pinpointing_between_camera_pair_for_GUI

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
                
        photo_id = 1
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
    
    photo_id = 1
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


from datetime import datetime
import pytz
@router.put("/create_homography_test_setup_table")
def create_homography_test_setup_table_api():
    datetime_of_creation = datetime.now(pytz.utc)
    setup_id = cdi.add_setup(setup_name="homography_test",
                             date_created=datetime_of_creation,
                             date_last_edited=datetime_of_creation)["id"]
    print(setup_id)
    return {"message": "Setup created!"}


@router.put("/add_two_cams_for_homography_test")
def add_two_cams_for_homography_test_api():
    
    setup_id = 1 # can check this is so
    
    # This only works if there are two cams with IDs 1 and 2 to actually add to DB.
    # So need to create camera/pi entries? 
    # # can do through the GUI with mock names
    cdi.add_camera_to_setup(1, 1)["id"] # id=1 for side cam
    cdi.add_camera_to_setup(1, 2)["id"] # id=2 for top cam
    
    return {"message": "Two cameras added!"}

# Just execute in /docs to fill in the table with vals in this handler
# Done this way so I don't need to enter into setup entries each time - and can't see refractive index
@router.put("/populate_setup_table")
def populate_setup_table_api():
    
    setup_id = 1
    patch_request = rb.SetupPatchRequest(
        block_x_dimension= 38.8,
        block_x_dimension_unc= 0.1,
        block_y_dimension = 99.8,
        block_y_dimension_unc =0.1,
        block_z_dimension = 249.5,
        block_z_dimension_unc = 0.5,
        block_refractive_index = 1.66,
        block_refractive_index_unc = 0
    )
    message = cdi.patch_setup(setup_id, patch_request)
    return {"message": "Setup patched!"}


@router.put("/populate_camera_setup_tables")
def populate_camera_setup_tables_api():
    """
    cam 1 Define as side Arducam
    cam 2 defined as top HQ
    """
    setup_id = 1
    side_camera_id = 1
    top_camera_id = 2
    # both +'ve side of origin along OA
    cdi.update_camera_depth_direction(side_camera_id, setup_id, 1) 
    cdi.update_camera_depth_direction(top_camera_id, setup_id, 1)
    
    cdi.update_camera_optical_axis(side_camera_id, setup_id, "x")
    cdi.update_camera_optical_axis(top_camera_id, setup_id, "y")
    return {"message": "OA and depth direction added"}


@router.put("/populate_camera_setup_table_homography_config")
def populate_camera_setup_table_homography_config_api():
    """
    run this before trying to build matrices - that script reads these in from db
    """
    # FAR FACE TOP CAM
    cdi.update_far_face_calibration_pattern_size(2, 1, [20, 5])
    cdi.update_far_face_calibration_pattern_type(2, 1, "chessboard")
    cdi.update_far_face_calibration_spacing(2, 1, [10, 10])
    cdi.update_far_face_calibration_spacing_unc(2, 1, [0.1, 0.1]) # check this was used last sem
    
    # NEAR FACE TOP CAM
    cdi.update_near_face_calibration_pattern_size(2, 1, [20, 5])
    cdi.update_near_face_calibration_pattern_type(2, 1, "chessboard")
    cdi.update_near_face_calibration_spacing(2, 1, [10, 10])
    cdi.update_near_face_calibration_spacing_unc(2, 1, [0.1, 0.1]) # check this was used last sem
    
    # FAR FACE SIDE CAM
    cdi.update_far_face_calibration_pattern_size(1, 1, [20, 10])
    cdi.update_far_face_calibration_pattern_type(1, 1, "chessboard")
    cdi.update_far_face_calibration_spacing(1, 1, [10, 10])
    cdi.update_far_face_calibration_spacing_unc(1, 1, [0.1, 0.1]) # check this was used last sem
    
    # NEAR FACE SIDE CAM
    cdi.update_near_face_calibration_pattern_size(1, 1, [20, 10])
    cdi.update_near_face_calibration_pattern_type(1, 1, "chessboard")
    cdi.update_near_face_calibration_spacing(1, 1, [10, 10])
    cdi.update_near_face_calibration_spacing_unc(1, 1, [0.1, 0.1]) # check this was used last sem
    
    return {"message": "done"}


@router.put("/populate_camera_setup_table_homography_matrices")
def populate_camera_setup_table_homography_matrices_api():
    """
    Must use first_username and second_username on GUI homepage
    
    photo order
    1) side far
    2) side near
    3) top far
    4) top near
    
    TODO - Need to check what transformations are actually needed!
    """
    
    # FAR SIDE CAM
    far_side_photo_bytes = cdi.get_photo_from_id(1)
    side_transforms = ImagePointTransforms(horizontal_flip=False,
                                      vertical_flip=False,
                                      swap_axes=False)
    perform_homography_calibration("first_camera", 1, "far", side_transforms, photo_bytes=far_side_photo_bytes)
    
    # NEAR SIDE CAM
    near_side_photo_bytes = cdi.get_photo_from_id(2)
    perform_homography_calibration("first_camera", 1, "near", side_transforms, photo_bytes=near_side_photo_bytes)
    
    
    # FAR TOP CAM
    far_top_photo_bytes = cdi.get_photo_from_id(3)
    top_transforms = ImagePointTransforms(horizontal_flip=False,
                                      vertical_flip=False,
                                      swap_axes=False)
    perform_homography_calibration("second_camera", 1, "far", top_transforms, photo_bytes=far_top_photo_bytes)
    
    # NEAR TOP CAM
    near_top_photo_bytes = cdi.get_photo_from_id(4)
    perform_homography_calibration("second_camera", 1, "near", top_transforms, photo_bytes=near_top_photo_bytes)
    return {"message": "done"}


@router.put("/initialize_full_homography_setup")
def initialize_homography_setup():
    """
    TODO - add prints to show progress along pipeline
    """
    create_homography_test_setup_table_api()
    add_two_cams_for_homography_test_api()
    populate_setup_table_api()
    populate_camera_setup_tables_api()
    populate_camera_setup_table_homography_config_api()
    populate_camera_setup_table_homography_matrices_api()
    return {"message": "Homography setup initialized successfully!"}



@router.get("/homography_pinpointing_test")
def homography_pinpointing_test_api():
    setup_id = 1
    side_camera_id = 1
    top_camera_id = 2
    perform_homography_pinpointing_between_camera_pair_for_GUI(setup_id, top_camera_id, side_camera_id)
    return {"message": "SUCCESS"}