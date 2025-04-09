from fastapi import Response, APIRouter

from src.camera_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb
from src.database.CRUD import CRISP_database_interaction as cdi
from src.classes.Camera import PhotoContext, CalibrationImageSettings
from src.create_homographies import *
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from src.homography_pinpointing import perform_homography_pinpointing_between_camera_pair_for_GUI
import os
import pickle
from src.single_camera_analysis import get_beam_angle_and_bragg_peak_pixel, get_beam_center_coords
from src.scintillation_light_pinpointing import *
from fastapi.exceptions import HTTPException
from src.fitting_functions import plot_physical_units_ODR_bortfeld


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

def add_mock_cameras_api():
    first_camera_id = cdi.add_camera(username="first_camera", ip_address=1, password=1, model=1)
    first_pi = Pi(inputted_username="first_camera",
                inputted_ip_address=1,
                inputted_password=1,
                inputted_camera_model=1)
    second_camera_id = cdi.add_camera(username="second_camera", ip_address=2, password=2, model=2)
    second_pi = Pi(inputted_username="second_camera",
                    inputted_ip_address=2,
                    inputted_password=2,
                    inputted_camera_model=2)

    return {"message": "cameras added"}


def add_mock_homography_images_api():
    
    # Arbitrary settings choice because only interested in the images
    # Use raspi4b3 for the username/camera ID
    
    added_settings = cdi.add_settings(frame_rate=5, lens_position=0.5, gain=1)
    settings_id = added_settings["id"] # Do I need to make a uique one for each settings?
    
    first_camera_id = cdi.get_camera_id_from_username("first_camera")
    second_camera_id = cdi.get_camera_id_from_username("second_camera")
    
    side_far_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=first_camera_id, settings_id=settings_id) # same args so same link?
    side_near_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=first_camera_id, settings_id=settings_id)
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
    
    top_far_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=second_camera_id, settings_id=settings_id) # same args so same link?
    top_near_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=second_camera_id, settings_id=settings_id)
    top_far_photo_camera_settings_link_id = top_far_photo_camera_settings_link["id"]
    top_near_photo_camera_settings_link_id = top_near_photo_camera_settings_link["id"]
    
    with open("/code/src/calibration_testing_19_11_24/top_arducam_front_chessboard_calibration_20_by_5_spacing_10mm.jpeg", "rb") as img_file:
        top_near_photo_bytes = img_file.read()
    with open("/code/src/calibration_testing_19_11_24/top_arducam_back_chessboard_calibration_20_by_5_spacing_10mm.jpeg", "rb") as img_file:
        top_far_photo_bytes = img_file.read()
    
    top_far_photo = cdi.update_photo(camera_settings_link_id=top_far_photo_camera_settings_link_id, photo=top_far_photo_bytes)
    top_far_photo_id = top_far_photo["id"]
    top_near_photo = cdi.update_photo(camera_settings_link_id=top_near_photo_camera_settings_link_id, photo=top_near_photo_bytes)
    top_near_photo_id = top_near_photo["id"]
    
    return {"message": f"successfully saved images to database. Photo IDs are {side_far_photo_id, side_near_photo_id, top_far_photo_id, top_near_photo_id}"}


@router.get("/test_homography_images")
def test_homography_images_api():
    image_ids = [
        "1",
        "2",
        "3",
        "4",
    ]
    
    save_dir = "/code/local_saved_images"
    os.makedirs(save_dir, exist_ok=True)
    
    saved_images = []
    
    for image_id in image_ids:
        image_data = cdi.get_photo_from_id(image_id)  # Assuming this function retrieves the photo
        file_path = os.path.join(save_dir, f"{image_id}.jpeg")
        
        with open(file_path, "wb") as img_file:
            img_file.write(image_data)  # Assuming image_data["photo"] contains the binary image data
        saved_images.append(file_path)
    
    return {"message": "Images saved locally", "saved_images": saved_images}


@router.get("/view_homography_image/{image_id}")
def view_image(image_id: str):
    file_path = os.path.join("/code/local_saved_images", f"{image_id}.jpeg")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/jpeg")
    return {"error": "Image not found"}

@router.get("/view_grid_image")
def view_image(camera_id: int, plane_type: str):
    file_path = f"/code/temp_images/camera_{camera_id}_homography_{plane_type}.jpeg"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/jpeg")
    return {"error": "Image not found"}


@router.get("/view_line_plot")
def view_image():
    file_path = "/code/src/plots/3d_lines_plot.png"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    return {"error": "Image not found"}


from datetime import datetime
import pytz
def create_homography_test_setup_table_api():
    datetime_of_creation = datetime.now(pytz.utc)
    setup_id = cdi.add_setup(setup_name="homography_test",
                             date_created=datetime_of_creation,
                             date_last_edited=datetime_of_creation)["id"]
    return {"message": "Setup created!"}


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


def populate_camera_setup_table_homography_config_api():
    """
    run this before trying to build matrices - that script reads these in from db
    
    TODO - origin shift properties!
    """
    # FAR FACE TOP CAM
    cdi.update_far_face_calibration_pattern_size(2, 1, [20, 5])
    cdi.update_far_face_calibration_pattern_type(2, 1, "chessboard")
    cdi.update_far_face_calibration_spacing(2, 1, [10, 10])
    cdi.update_far_face_calibration_spacing_unc(2, 1, [0.1, 0.1]) # check this was used last sem
    cdi.update_far_face_calibration_board_thickness(2, 1, 0.8)
    cdi.update_far_face_calibration_board_thickness_unc(2, 1, 0.1)
    
    # cdi.update_far_face_z_shift(2, 1, 10.7) # first estimate
    # cdi.update_far_face_non_z_shift(2, 1, 9.6) # first estimate
    # cdi.update_far_face_z_shift_unc(2, 1, 0.1) # first estimate
    # cdi.update_far_face_non_z_shift_unc(2, 1, 0.1) # first estimate
    
    cdi.update_far_face_z_shift(2, 1, 10.5) # first estimate
    cdi.update_far_face_non_z_shift(2, 1, 4) # first estimate
    cdi.update_far_face_z_shift_unc(2, 1, 0.5) # first estimate
    cdi.update_far_face_non_z_shift_unc(2, 1, 0.5) # first estimate
    
    # cdi.update_far_face_z_shift(2, 1, 10) # first estimate
    # cdi.update_far_face_non_z_shift(2, 1, 4.3) # first estimate
    # cdi.update_far_face_z_shift_unc(2, 1, 0.5) # first estimate
    # cdi.update_far_face_non_z_shift_unc(2, 1, 0.5) # first estimate
    
    # NEAR FACE TOP CAM
    cdi.update_near_face_calibration_pattern_size(2, 1, [20, 5])
    cdi.update_near_face_calibration_pattern_type(2, 1, "chessboard")
    cdi.update_near_face_calibration_spacing(2, 1, [10, 10])
    cdi.update_near_face_calibration_spacing_unc(2, 1, [0.1, 0.1]) # check this was used last sem
    cdi.update_near_face_calibration_board_thickness(2, 1, 0.8)
    cdi.update_near_face_calibration_board_thickness_unc(2, 1, 0.1)
    
    # cdi.update_near_face_z_shift(2, 1, 10.7) # first estimate
    # cdi.update_near_face_non_z_shift(2, 1, 9.6) # first estimate
    # cdi.update_near_face_z_shift_unc(2, 1, 0.1) # first estimate
    # cdi.update_near_face_non_z_shift_unc(2, 1, 0.1) # first estimate
    
    cdi.update_near_face_z_shift(2, 1, 10.5) # first estimate
    cdi.update_near_face_non_z_shift(2, 1, 4) # first estimate
    cdi.update_near_face_z_shift_unc(2, 1, 0.5) # first estimate
    cdi.update_near_face_non_z_shift_unc(2, 1, 0.5) # first estimate
    
    # cdi.update_near_face_z_shift(2, 1, 10) # first estimate
    # cdi.update_near_face_non_z_shift(2, 1, 4.3) # first estimate
    # cdi.update_near_face_z_shift_unc(2, 1, 0.5) # first estimate
    # cdi.update_near_face_non_z_shift_unc(2, 1, 0.5) # first estimate
    
    # FAR FACE SIDE CAM
    cdi.update_far_face_calibration_pattern_size(1, 1, [20, 10])
    cdi.update_far_face_calibration_pattern_type(1, 1, "chessboard")
    cdi.update_far_face_calibration_spacing(1, 1, [10, 10])
    cdi.update_far_face_calibration_spacing_unc(1, 1, [0.1, 0.1]) # check this was used last sem
    cdi.update_far_face_calibration_board_thickness(1, 1, 2.8)
    cdi.update_far_face_calibration_board_thickness_unc(1, 1, 0.1)
    cdi.update_far_face_z_shift(1, 1, 10.5) # first estimate
    cdi.update_far_face_non_z_shift(1, 1, 5.8) # first estimate
    cdi.update_far_face_z_shift_unc(1, 1, 0.1) # first estimate
    cdi.update_far_face_non_z_shift_unc(1, 1, 0.1) # first estimate
    
    # NEAR FACE SIDE CAM
    cdi.update_near_face_calibration_pattern_size(1, 1, [20, 10])
    cdi.update_near_face_calibration_pattern_type(1, 1, "chessboard")
    cdi.update_near_face_calibration_spacing(1, 1, [10, 10])
    cdi.update_near_face_calibration_spacing_unc(1, 1, [0.1, 0.1]) # check this was used last sem
    cdi.update_near_face_calibration_board_thickness(1, 1, 2.8)
    cdi.update_near_face_calibration_board_thickness_unc(1, 1, 0.1)
    cdi.update_near_face_z_shift(1, 1, 10.5) # first estimate
    cdi.update_near_face_non_z_shift(1, 1, 5.8) # first estimate
    cdi.update_near_face_z_shift_unc(1, 1, 0.1) # first estimate
    cdi.update_near_face_non_z_shift_unc(1, 1, 0.1) # first estimate
    
    return {"message": "done"}


def populate_camera_setup_table_homography_matrices_api():
    """
    photo order
    1) side far
    2) side near
    3) top far
    4) top near
    
    TODO - Need to check what transformations are actually needed!
    """
    
    # FAR SIDE CAM
    far_side_photo_bytes = cdi.get_photo_from_id(1)
    far_side_transform = ImagePointTransforms(horizontal_flip=False,
                                      vertical_flip=False,
                                      swap_axes=False)
    perform_homography_calibration("first_camera", 1, "far", far_side_transform, photo_bytes=far_side_photo_bytes, save_overlayed_grid=True)
    
    # NEAR SIDE CAM
    near_side_transform = ImagePointTransforms(horizontal_flip=True,
                                               vertical_flip=True,
                                               swap_axes=False)
    near_side_photo_bytes = cdi.get_photo_from_id(2)
    perform_homography_calibration("first_camera", 1, "near", near_side_transform, photo_bytes=near_side_photo_bytes, save_overlayed_grid=True)
    
    
    # FAR TOP CAM
    far_top_photo_bytes = cdi.get_photo_from_id(3)
    top_transforms = ImagePointTransforms(horizontal_flip=True,
                                      vertical_flip=False,
                                      swap_axes=False)
    perform_homography_calibration("second_camera", 1, "far", top_transforms, photo_bytes=far_top_photo_bytes, save_overlayed_grid=True)
    
    # NEAR TOP CAM
    near_top_photo_bytes = cdi.get_photo_from_id(4)
    perform_homography_calibration("second_camera", 1, "near", top_transforms, photo_bytes=near_top_photo_bytes, save_overlayed_grid=True)
    return {"message": "done"}


@router.put("/initialize_full_homography_setup")
def initialize_homography_setup():
    """
    TODO - add prints to show progress along pipeline
    """
    add_mock_cameras_api()
    add_mock_homography_images_api()
    create_homography_test_setup_table_api()
    add_two_cams_for_homography_test_api()
    populate_setup_table_api()
    populate_camera_setup_tables_api()
    populate_camera_setup_table_homography_config_api()
    populate_camera_setup_table_homography_matrices_api()
    
    return {"message": "Homography setup initialized successfully!"}



@router.get("/homography_pinpointing_test")
def homography_pinpointing_test_api():
    """
    1) use docs to execute initialize_full_homography_setup
    2) use docs to execute homography_pinpointing_test
    """
    setup_id = 1
    side_camera_id = 1
    top_camera_id = 2
    perform_homography_pinpointing_between_camera_pair_for_GUI(setup_id, top_camera_id, side_camera_id)
    return {"message": "pinpointing complete"}


def add_homography_images_with_hq_api():
    
    # Arbitrary settings choice because only interested in the images
    # Use raspi4b3 for the username/camera ID
    
    added_settings = cdi.add_settings(frame_rate=5, lens_position=0.5, gain=1)
    settings_id = added_settings["id"] # Do I need to make a uique one for each settings?
    
    first_camera_id = cdi.get_camera_id_from_username("first_camera") # SIDE ARDUCAM
    second_camera_id = cdi.get_camera_id_from_username("second_camera") # TOP HQ
    
    side_far_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=first_camera_id, settings_id=settings_id) # same args so same link?
    side_near_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=first_camera_id, settings_id=settings_id)
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
    
    top_far_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=second_camera_id, settings_id=settings_id) # same args so same link?
    top_near_photo_camera_settings_link = cdi.add_camera_settings_link(camera_id=second_camera_id, settings_id=settings_id)
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


def populate_hq_distortion_params_api():
    
    setup_id = 1 
    top_hq_cam_id = 2
    with open("/code/src/calibration_testing_19_11_24/top_hq_distortion_data/top_hq_camera_calibration.pkl", "rb") as data:
        camera_matrix, distortion_coefficients = pickle.load(data)
    
    camera_matrix = pickle.dumps(camera_matrix)
    distortion_coefficients = pickle.dumps(distortion_coefficients)
    
    setup_camera_id = cdi.get_setup_camera_id(top_hq_cam_id, setup_id)
    cdi.update_distortion_calibration_pattern_size_z_dim(setup_camera_id, 1) # mock input
    cdi.update_distortion_calibration_pattern_size_non_z_dim(setup_camera_id, 1) # mock input
    cdi.update_distortion_calibration_pattern_type(setup_camera_id, "chessboard") # NOT USED YET
    cdi.update_distortion_calibration_pattern_spacing(setup_camera_id,  1) # mock input
    cdi.update_camera_matrix(top_hq_cam_id, setup_id, camera_matrix)
    cdi.update_distortion_coefficients(top_hq_cam_id, setup_id, distortion_coefficients)
    return {"message": "done"}


def populate_camera_setup_table_for_beam_analysis_api():
    """
    photo order
    1) side far
    2) side near
    3) top far
    4) top near
    """
    # FAR SIDE CAM
    far_side_photo_bytes = cdi.get_photo_from_id(1)
    far_side_transform = ImagePointTransforms(horizontal_flip=False,
                                      vertical_flip=False,
                                      swap_axes=False)
    perform_homography_calibration("first_camera", 1, "far", far_side_transform, photo_bytes=far_side_photo_bytes, save_overlayed_grid=True)
    
    # NEAR SIDE CAM
    near_side_transform = ImagePointTransforms(horizontal_flip=True,
                                               vertical_flip=True,
                                               swap_axes=False)
    near_side_photo_bytes = cdi.get_photo_from_id(2)
    perform_homography_calibration("first_camera", 1, "near", near_side_transform, photo_bytes=near_side_photo_bytes, save_overlayed_grid=True)
    
    
    # FAR TOP CAM
    far_top_photo_bytes = cdi.get_photo_from_id(3)
    top_transforms = ImagePointTransforms(horizontal_flip=True,
                                      vertical_flip=False,
                                      swap_axes=False)
    perform_homography_calibration("second_camera", 1, "far", top_transforms, photo_bytes=far_top_photo_bytes, save_overlayed_grid=True)
    
    # NEAR TOP CAM
    near_top_photo_bytes = cdi.get_photo_from_id(4)
    perform_homography_calibration("second_camera", 1, "near", top_transforms, photo_bytes=near_top_photo_bytes, save_overlayed_grid=True)
    
    # Beam directions updated
    cdi.update_image_beam_direction(1, 1, "left") # side camera
    cdi.update_image_beam_direction(2, 1, "left") # top camera
    return {"message": "done"}


def upload_averaged_image_api():
    
    # beam_energy = 90
    beam_energy = 150
    # beam_energy = 180
    SIDE_AR_CAM_ID = 1
    TOP_HQ_CAM_ID = 2

    current_time = datetime.now(pytz.utc)
    setup_id = 1
    experiment_id = cdi.add_experiment("beam_analysis_testing", current_time, setup_id)["id"]
    beam_run_id = cdi.add_beam_run(experiment_id=experiment_id, beam_run_number=1,
                                   datetime_of_run=current_time, 
                                   ESS_beam_energy=beam_energy, beam_current=100, 
                                   is_test=False).id
    
    # Make two test csl ids for the main run on the two cams
    
    side_AR_settings_id = cdi.add_settings(frame_rate=20, lens_position=5, gain=5)["id"]
    top_HQ__settings_id = cdi.add_settings(frame_rate=20, lens_position=5, gain=5)["id"]
    
    side_AR_camera_settings_link_id = cdi.add_camera_settings_link_with_beam_run(SIDE_AR_CAM_ID, side_AR_settings_id, beam_run_id)["id"]
    top_HQ_camera_settings_link_id = cdi.add_camera_settings_link_with_beam_run(TOP_HQ_CAM_ID, top_HQ__settings_id, beam_run_id)["id"]
    side_AR_analysis_id = cdi.add_camera_analysis(side_AR_camera_settings_link_id, "blue")["id"]
    top_HQ_analysis_id = cdi.add_camera_analysis(top_HQ_camera_settings_link_id, "blue")["id"]
    
    # 90 MEV
    # num_of_hq_images_in_average = 64
    # num_of_ar_images_in_average = 53
    
    # 150 MEV
    num_of_hq_images_in_average = 348
    num_of_ar_images_in_average = 67
    
    # 180 MEV
    # num_of_hq_images_in_average = 172
    # num_of_ar_images_in_average = 78
    
    # Adding mock images to test if cdi.get_num_of_successfully_captured_images_by_camera_settings_link_id() is working
    mock_bytestring = pickle.dumps("lol")
    for i in range(num_of_ar_images_in_average):
        cdi.add_photo(camera_settings_link_id=side_AR_camera_settings_link_id, photo=mock_bytestring)
    for i in range(num_of_hq_images_in_average):
        cdi.add_photo(camera_settings_link_id=top_HQ_camera_settings_link_id, photo=mock_bytestring)
    
    # FLOAT-16 PICKLED AVERAGED NUMPY ARRAYS
    with open("/code/src/beam_averaged_images/150_mev_A1_averaged_image_float16.pkl", "rb") as file:
        pickled_side_AR__average_image = file.read()
    cdi.update_average_image(side_AR_analysis_id, pickled_side_AR__average_image)
    
    with open("/code/src/beam_averaged_images/150_mev_HQ2_averaged_image_float16.pkl", "rb") as file:
        pickled_top_HQ_average_image = file.read()
    cdi.update_average_image(top_HQ_analysis_id, pickled_top_HQ_average_image)
    return None


def populate_scintillator_edges_api():
    """
    SIDE_ARDUCAM_SCINTILLATOR_EDGES = [(875, 3500), (530, 1650)]
    TOP_HQ_SCINTILLATOR_EDGES = [(700, 3100), (990, 1400)] # Edges in undistorted image
    """
    
    side_ar_cam_id = 1
    top_hq_cam_id = 2
    setup_id = 1
    side_ar_setup_camera_id = cdi.get_setup_camera_id(side_ar_cam_id, setup_id)
    top_hq_setup_camera_id = cdi.get_setup_camera_id(top_hq_cam_id, setup_id)
    
    side_ar_horizontal_scintillator_edges = [875, 3500]
    side_ar_vertical_scintillator_edges = [530, 1650]
    top_hq_horizontal_scintillator_edges = [700, 3100]
    top_hq_vertical_scintillator_edges = [990, 1400]
    
    cdi.update_horizontal_scintillator_scintillator_start(side_ar_setup_camera_id, side_ar_horizontal_scintillator_edges[0])
    cdi.update_horizontal_scintillator_scintillator_end(side_ar_setup_camera_id, side_ar_horizontal_scintillator_edges[1])
    cdi.update_vertical_scintillator_scintillator_start(side_ar_setup_camera_id, side_ar_vertical_scintillator_edges[0])
    cdi.update_vertical_scintillator_scintillator_end(side_ar_setup_camera_id, side_ar_vertical_scintillator_edges[1])
    cdi.update_horizontal_scintillator_scintillator_start(top_hq_setup_camera_id, top_hq_horizontal_scintillator_edges[0])
    cdi.update_horizontal_scintillator_scintillator_end(top_hq_setup_camera_id, top_hq_horizontal_scintillator_edges[1])
    cdi.update_vertical_scintillator_scintillator_start(top_hq_setup_camera_id, top_hq_vertical_scintillator_edges[0])
    cdi.update_vertical_scintillator_scintillator_end(top_hq_setup_camera_id, top_hq_vertical_scintillator_edges[1])
    return None


@router.put("/initialize_beam_analysis_setup")
def initialize_beam_analysis_setup_api():
    """
    TO CHANGE PER ENERGY:
    1) Uploaded average image 
    2) Beam energy parameter
    3) Number of images in average
    
    """
    add_mock_cameras_api()
    add_homography_images_with_hq_api()
    create_homography_test_setup_table_api()
    add_two_cams_for_homography_test_api()
    populate_setup_table_api()
    populate_camera_setup_tables_api()
    populate_scintillator_edges_api()
    populate_hq_distortion_params_api()
    populate_camera_setup_table_homography_config_api()
    populate_camera_setup_table_for_beam_analysis_api()
    upload_averaged_image_api()
    return {"message": "Homography setup initialized successfully!"}


@router.get("/test_beam_analysis")
def test_beam_analysis_api():
    
    try:
        side_camera_analysis_id = 1
        top_camera_analysis_id = 2
        side_camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(side_camera_analysis_id)
        beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(side_camera_settings_link_id)

        first_results = get_beam_angle_and_bragg_peak_pixel(side_camera_analysis_id)
        print("\n\n\nFINISHED\n\n\n")
        print(f"\n\nBeam angle: {first_results['beam_angle']} +/- {first_results['beam_angle_error']}")
        print(f"\n\nBragg peak pixel: {first_results['bragg_peak_pixel']} +/- {first_results['bragg_peak_pixel_error']}")
        
        second_results = get_beam_angle_and_bragg_peak_pixel(top_camera_analysis_id)
        print(f"\n\nBeam angle: {second_results['beam_angle']} +/- {second_results['beam_angle_error']}")
        print(f"\n\nBragg peak pixel: {second_results['bragg_peak_pixel']} +/- {second_results['bragg_peak_pixel_error']}")
        
        cdi.update_beam_angle(side_camera_analysis_id, float(first_results["beam_angle"]))
        cdi.update_unc_beam_angle(side_camera_analysis_id, float(first_results["beam_angle_error"]))
        # NOTE - Float trick below needed because np.float64 cannot be stored in DB
        cdi.update_bragg_peak_pixel(side_camera_analysis_id, [float(x) for x in first_results["bragg_peak_pixel"].flatten()])
        cdi.update_unc_bragg_peak_pixel(side_camera_analysis_id, [float(x) for x in first_results["bragg_peak_pixel_error"].flatten()])
        
        cdi.update_beam_angle(top_camera_analysis_id, float(second_results["beam_angle"]))
        cdi.update_unc_beam_angle(top_camera_analysis_id, float(second_results["beam_angle_error"]))
        cdi.update_bragg_peak_pixel(top_camera_analysis_id, [float(x) for x in second_results["bragg_peak_pixel"].flatten()])
        cdi.update_unc_bragg_peak_pixel(top_camera_analysis_id, [float(x) for x in second_results["bragg_peak_pixel_error"].flatten()])
        
        # PINPOINTING STAGE
        side_cam_bragg_peak_pixel, side_cam_bragg_peak_pixel_error = first_results["bragg_peak_pixel"], first_results["bragg_peak_pixel_error"]
        top_cam_bragg_peak_pixel, top_cam_bragg_peak_pixel_error = second_results["bragg_peak_pixel"], second_results["bragg_peak_pixel_error"]
        pinpoint_results = pinpoint_bragg_peak([side_camera_analysis_id, top_camera_analysis_id])
        bragg_peak_3d_position, unc_bragg_peak_3d_position = pinpoint_results["bragg_peak_position"], pinpoint_results["bragg_peak_position_error"]
        
        cdi.update_bragg_peak_3d_position(beam_run_id, [float(x) for x in bragg_peak_3d_position.flatten()])
        cdi.update_unc_bragg_peak_3d_position(beam_run_id, [float(x) for x in unc_bragg_peak_3d_position.flatten()])
        
        # PENETRATION DEPTH STAGE
        print(f"\n\nBragg peak 3D position: {bragg_peak_3d_position} +/- {unc_bragg_peak_3d_position}")
        bragg_peak_depth, unc_bragg_peak_depth = compute_bragg_peak_depth(beam_run_id, 
                                                                        side_camera_analysis_id,
                                                                        top_camera_analysis_id)
        
        print(f"\n\nBragg peak depth: {bragg_peak_depth} +/- {unc_bragg_peak_depth}")
        
        print(f"Saved plot keys: {first_results['plot_byte_strings'].keys()}")
        plots = list(first_results["plot_byte_strings"].values()) + list(second_results["plot_byte_strings"].values())
        img_tags = ""
        for plot_base64 in plots:
            img_tags += f'<img src="data:image/svg+xml;base64,{plot_base64}" width="200px"><br>' # SVG Plots
        html_content = f"<html><body>{img_tags}</body></html>"
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test_beam_reconstruction")
def test_beam_reconstruction_api():
    try:
        plot_bytes = []
        side_camera_analysis_id = 1
        top_camera_analysis_id = 2
        side_camera_settings_link_id = cdi.get_camera_settings_link_id_by_camera_analysis_id(side_camera_analysis_id)
        beam_run_id = cdi.get_beam_run_id_by_camera_settings_link_id(side_camera_settings_link_id)

        # METHOD 1
        # beam_center_incident_position, unc_beam_center_incident_position, \
        # beam_direction_vector, unc_beam_direction_vector = build_directional_vector_of_beam_center_for_camera_pair(side_camera_analysis_id, top_camera_analysis_id)
        
        # METHOD 2 - produces weighted beam path vector
        beam_center_incident_position, unc_beam_center_incident_position, \
        beam_direction_vector, unc_beam_direction_vector = build_weighted_directional_vector_of_beam_center([side_camera_analysis_id], [top_camera_analysis_id])
        
        # Get beam center coords in side cam image
        side_cam_beam_center_coords, unc_side_cam_beam_center_coords, \
        total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi = get_beam_center_coords(beam_run_id, side_camera_analysis_id)
        
        distances_travelled_inside_scintillator, \
        unc_distances_travelled_inside_scintillator = convert_beam_center_coords_to_penetration_depths(side_camera_analysis_id,
                                                                                                    side_cam_beam_center_coords,
                                                                                                    unc_side_cam_beam_center_coords,
                                                                                                    [beam_center_incident_position, beam_direction_vector],
                                                                                                    [unc_beam_center_incident_position, unc_beam_direction_vector])
        # Unc in range needs amending
        # TODO - put range computations in a separate function?
        
        bragg_peak_depth, unc_bragg_peak_depth = compute_bragg_peak_depth(beam_run_id, 
                                                                        side_camera_analysis_id,
                                                                        top_camera_analysis_id)
        
        plot_bytes += [plot_physical_units_ODR_bortfeld(bragg_peak_depth, distances_travelled_inside_scintillator, unc_distances_travelled_inside_scintillator, 
                                                      total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi, left_fit_window=1000, right_fit_window=200)]
        
        #### TOP CAM VERSION OF ANALYSIS ######
    
        top_cam_beam_center_coords, unc_top_cam_beam_center_coords, \
        total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi = get_beam_center_coords(beam_run_id, top_camera_analysis_id)
        
        distances_travelled_inside_scintillator, \
        unc_distances_travelled_inside_scintillator = convert_beam_center_coords_to_penetration_depths(top_camera_analysis_id,
                                                                                                    top_cam_beam_center_coords,
                                                                                                    unc_top_cam_beam_center_coords,
                                                                                                    [beam_center_incident_position, beam_direction_vector],
                                                                                                    [unc_beam_center_incident_position, unc_beam_direction_vector])
        # Unc in range needs amending
        # TODO - put range computations in a separate function?
        
        # TODO - don't exit code if distance of closest approach exceeds valid distance - just omit from data because failed pinpointing
        # TODO - if error bar is sufficiently large, exclude from data - where pinpointing method has failed
        # TODO - unc_penetration_depth looks far too big - look for errors
        
        plot_bytes += [plot_physical_units_ODR_bortfeld(bragg_peak_depth, distances_travelled_inside_scintillator, unc_distances_travelled_inside_scintillator, 
                                                      total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi, left_fit_window=800, right_fit_window=100)] # TODO - need to have an asymmetric window

        img_tags = ""
        for plot_base64 in plot_bytes:
            img_tags += f'<img src="data:image/svg+xml;base64,{plot_base64}" width="500px"><br>' # SVG Plots
        html_content = f"<html><body>{img_tags}</body></html>"
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))