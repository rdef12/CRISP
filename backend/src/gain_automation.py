import numpy as np
from src.camera_functions import load_image_byte_string_to_opencv
from src.database.CRUD import CRISP_database_interaction as cdi

def restrict_to_region_of_interest(image: np.ndarray,
                                   horizontal_start: int,
                                   horizontal_end: int,
                                   vertical_start: int,
                                   vertical_end: int) -> np.ndarray:
    if horizontal_start is None:
        horizontal_start = 0
    if horizontal_end is None:
        horizontal_end = image.shape[1]
    if vertical_start is None:
        vertical_start = 0
    if vertical_end is None:
        vertical_end = image.shape[0]
    scintillator_horizontal_roi = [horizontal_start + 5, horizontal_end - 5]
    scintillator_vertical_roi = [vertical_start + 5, vertical_end - 5]
    
    scintillator_region = image[scintillator_vertical_roi[0]:scintillator_vertical_roi[-1],
                                scintillator_horizontal_roi[0]:scintillator_horizontal_roi[-1]]
    return scintillator_region

def determine_saturation(image: np.ndarray, threshold: int=5) -> bool:
    MAXIMUM_PIXEL_BRIGHTNESS = 255
    saturation_brightness = MAXIMUM_PIXEL_BRIGHTNESS - threshold
    saturation_mask = image >= saturation_brightness
    if np.all(saturation_mask == False):
        return False
    return True

def mark_saturation(image: np.ndarray, threshold: int=5) -> np.ndarray:
    MAXIMUM_PIXEL_BRIGHTNESS = 255
    saturation_brightness = MAXIMUM_PIXEL_BRIGHTNESS - threshold
    saturation_mask = image >= saturation_brightness
    return saturation_mask


def determine_optimal_settings(photo_ids: list[int], threshold: int=5) -> int:
    is_saturated = np.empty((len(photo_ids), 3), dtype=object)
    for count, photo_id in enumerate(photo_ids):
        photo = cdi.get_photo_from_id(photo_id)
        gain = cdi.get_gain_from_photo_id(photo_id)
        image = load_image_byte_string_to_opencv(photo)
        horizontal_start, horizontal_end, vertical_start, vertical_end = cdi.get_scintillator_edges_by_photo_id(photo_id)
        image = restrict_to_region_of_interest(image, horizontal_start, horizontal_end, vertical_start, vertical_end)
        
        is_saturated[count, 0] = determine_saturation(image, threshold=threshold)
        is_saturated[count, 1] = gain
        is_saturated[count, 2] = photo_id
    false_saturation_indices = np.where(is_saturated[:, 0] == False)[0]
    if false_saturation_indices.size == 0:
        return None
    lowest_gain_index = false_saturation_indices[np.argmax(is_saturated[false_saturation_indices, 1])]
    optimal_settings_photo_id = is_saturated[lowest_gain_index, 2]
    return optimal_settings_photo_id

def set_optimal_settings(photo_ids: int, threshold: int=5):
    # camera_settings = cdi.get_camera_settings_by_photo_id(photo_ids[0])
    optimal_photo_id = determine_optimal_settings(photo_ids, threshold=threshold)
    if optimal_photo_id is None:
        cdi.update_no_optimal_in_run(photo_ids)
        return
    cdi.update_is_optimal(optimal_photo_id)
    return
    