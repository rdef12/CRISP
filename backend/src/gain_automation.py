import cv2
import numpy as np
from src.camera_functions import load_image_byte_string_to_opencv
from src.database.CRUD import CRISP_database_interaction as cdi
from enum import Enum

class ColourChannel(Enum):
    BLUE = 0
    GREEN = 1
    RED = 2
    GREYSCALE = 3

class OverlayColour(Enum):
    RED = (0,0,255)
    GREEN = (0,255,0)
    BLUE = (255,0,0)
    WHITE = (255,255,255)
    

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
    print(f"\n\n\n              shape of saturation mask: {saturation_mask.shape}\n\n\n")
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
        blue_channel_image =image[:, :, 0] #TODO For generality this should be a variable
        horizontal_start, horizontal_end, vertical_start, vertical_end = cdi.get_scintillator_edges_by_photo_id(photo_id)
        blue_channel_image = restrict_to_region_of_interest(blue_channel_image, horizontal_start, horizontal_end, vertical_start, vertical_end)
        
        is_saturated[count, 0] = determine_saturation(blue_channel_image, threshold=threshold)
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


def overlay_saturated_points(image: np.ndarray, saturation_mask: np.ndarray, radius: int, colour_channel: ColourChannel):
    overlay_colour = OverlayColour.RED.value
    if colour_channel == ColourChannel.RED:
        overlay_colour = OverlayColour.GREEN.value
    overlay = image.copy()
    ys, xs = np.where(saturation_mask)
    for x, y in zip(xs, ys):
        cv2.circle(overlay, (x, y), radius, overlay_colour, thickness=-1)  # Filled red circle (BGR)
    return overlay


def overlay_scintillator_edges(image: np.ndarray,
                               horizontal_start: int,
                               horizontal_end: int,
                               vertical_start: int,
                               vertical_end: int,
                               colour_channel: ColourChannel):
    # overlay_colour = ColourChannel.RED.value
    # if colour_channel == ColourChannel.RED:
    #     overlay_colour = ColourChannel.GREEN.value
    
    overlay = image.copy()

    # cv2.rectangle(overlay,
    #               (horizontal_start, vertical_start),
    #               (horizontal_end - 1, vertical_end - 1),
    #               overlay_colour,  # Green in BGR
    #               50)  # Thickness
        # Top line (spans full width of the image)
    thickness = 10
    overlay_colour = (255,255,255)
    cv2.line(overlay, (0, vertical_start), (image.shape[1], vertical_start), overlay_colour, thickness)  # Top line
    
    # Right line (spans full height of the image)
    cv2.line(overlay, (horizontal_end, 0), (horizontal_end, image.shape[0]), overlay_colour, thickness)  # Right line
    
    # Bottom line (spans full width of the image)
    cv2.line(overlay, (0, vertical_end), (image.shape[1], vertical_end), overlay_colour, thickness)  # Bottom line
    
    # Left line (spans full height of the image)
    cv2.line(overlay, (horizontal_start, 0), (horizontal_start, image.shape[0]), overlay_colour, thickness)  # Left line
    
    return overlay


def identify_saturated_points_within_scintillator_edges(image: np.ndarray,
                                                        horizontal_start: int,
                                                        horizontal_end: int,
                                                        vertical_start: int,
                                                        vertical_end: int,
                                                        colour_channel: ColourChannel) -> np.ndarray:
    if colour_channel == ColourChannel.BLUE:
        image = image[:,:,0]
    elif colour_channel == ColourChannel.GREEN:
        image = image[:,:,1]
    elif colour_channel == ColourChannel.RED:
        image = image[:,:,2]
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    saturation_mask = mark_saturation(image)
    roi_mask = np.zeros_like(saturation_mask, dtype=bool)
    roi_mask[vertical_start:vertical_end, horizontal_start:horizontal_end] = True
    saturation_mask &= roi_mask
    return image, saturation_mask


def show_saturated_points(image: np.ndarray,
                          horizontal_start: int,
                          horizontal_end: int,
                          vertical_start: int,
                          vertical_end: int,
                          colour_channel: ColourChannel) -> np.ndarray:
    skeleton_image = np.zeros_like(image)
    image, saturation_mask = identify_saturated_points_within_scintillator_edges(image,
                                                                          horizontal_start,
                                                                          horizontal_end,
                                                                          vertical_start,
                                                                          vertical_end,
                                                                          colour_channel)
    MAXIMUM_PIXEL_BRIGHTNESS = 255
    threshold = 5
    saturation_brightness = MAXIMUM_PIXEL_BRIGHTNESS - threshold
    saturation_mask = image >= saturation_brightness
    is_saturated = True
    if np.all(saturation_mask == False):
        is_saturated = False
    
    if colour_channel == ColourChannel.RED:
        skeleton_image[:,:,0] = 0 #blue channel
        skeleton_image[:,:,1] = 0 #green channel
        skeleton_image[:,:,2] = image #red channel
    
    elif colour_channel == ColourChannel.GREEN:
        skeleton_image[:,:,0] = 0 #blue channel
        skeleton_image[:,:,1] = image #green channel
        skeleton_image[:,:,2] = 0 #red channel

    elif colour_channel == ColourChannel.BLUE:
        skeleton_image[:,:,0] = image #blue channel
        skeleton_image[:,:,1] = 0 #green channel
        skeleton_image[:,:,2] = 0 #red channel

    else:
        skeleton_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    skeleton_image = overlay_scintillator_edges(skeleton_image,
                                       horizontal_start,
                                       horizontal_end,
                                       vertical_start,
                                       vertical_end,
                                       colour_channel)
    radius = 2
    skeleton_image = overlay_saturated_points(skeleton_image, saturation_mask, radius, colour_channel)
 
    success, image_bytes = cv2.imencode('.jpg', skeleton_image)
    if success:
        return is_saturated, image_bytes.tobytes()
    else:
        raise ValueError("Error encoding the image")