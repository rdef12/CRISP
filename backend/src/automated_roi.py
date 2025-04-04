import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from src.edge_detection_functions import find_beam_contour_extremes

# SIDE_SCINTILLATOR_HORIZONTAL_ROI = [875, 3500]
# SIDE_SCINTILLATOR_VERTICAL_ROI = [530, 1650]

# TOP_SCINTILLATOR_HORIZONTAL_ROI = [700, 3100]
# TOP_SCINTILLATOR_VERTICAL_ROI = [990, 1400]

def get_scintillator_pixel_dimensions(scintillator_horizontal_roi, scintillator_vertical_roi):
    
    horizontal_pixel_width = abs(scintillator_horizontal_roi[1] - scintillator_horizontal_roi[0])
    vertical_pixel_width = abs(scintillator_vertical_roi[1] - scintillator_vertical_roi[0])
    return horizontal_pixel_width, vertical_pixel_width

    
def roi_determination_inside_scintillator(image, scintillator_horizontal_roi, scintillator_vertical_roi,
                                          use_edge_detection: bool=True, verbose_output: bool=False,
                                          show_plots: bool=False, fraction: float=0.15):
    """
    NOTE - Greyscale image expected as input. In our case, this is from the blue channel of the
    original averaged image.
    
    1) Find maximum brightness (approximately the Bragg peak pixel brightness)
    2) Produce binary image by looking where brightness > fraction * peak brightness
    3) Look at the extreme x, y values in that domain to define the ROI - or look at extremes in edge
    detected beam contour
    
    NOTE - CRUCIALLY, we would not expect this threshold method to work IF the Bragg peak is saturated - therefore
    take the failure of this method for 90 MeV data with a grain of salt.
    """
    
    horizontal_pixel_width, vertical_pixel_width = get_scintillator_pixel_dimensions(scintillator_horizontal_roi, scintillator_vertical_roi)
    
    if verbose_output:
        background_brightness_value = np.min(image)
        print("Background brightness = {}\n".format(background_brightness_value) + "Minimum f = {}".format(background_brightness_value/peak_brightness_value))

    peak_brightness_value = np.max(image)
    mask = image > peak_brightness_value * fraction
    binary_image = (mask.astype(np.uint8)) * 255
    
    plt.imshow(binary_image)
    plt.show()
    
    if use_edge_detection:
        x_bounds, y_bounds = find_beam_contour_extremes(binary_image, horizontal_pixel_width, vertical_pixel_width, show_image=show_plots)
    else:
        columns, rows = np.where(mask)
        x_bounds = np.array([rows.min(), rows.max()])
        y_bounds = np.array([columns.min(), columns.max()])
    
    # To deal with case where only the frontier contour is identified, use the start of the horizontal ROI as 
    # that determined by the user for the incident scintillator face
    x_bounds[0] = 0
    
    if show_plots:
        plt.imshow(image)
        plt.imshow(mask, alpha=0.3)
        plt.axvline(x_bounds[0], color='red')
        plt.axvline(x_bounds[1], color='red')
        plt.axhline(y_bounds[0], color='red')
        plt.axhline(y_bounds[1], color='red')
        plt.show()
    
    return x_bounds, y_bounds

def display_image_with_roi(image, horizontal_roi, vertical_roi):
    rgb_image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    plt.imshow(rgb_image)
    plt.axvline(horizontal_roi[0], color='red')
    plt.axvline(horizontal_roi[1], color='red')
    plt.axhline(vertical_roi[0], color='red')
    plt.axhline(vertical_roi[1], color='red')
    plt.show()
    return

def get_automated_roi(image, scintillator_horizontal_roi, scintillator_vertical_roi, show_images: bool=False,
                      fraction: float=0.15):
    """
    Expects an image with a single colour channel inputted (includes greyscale)
    """
    
    # 5 pixel padding added around the user defined region of interests - visible scintillator edges will interfere with beam edge detection
    scintillator_horizontal_roi = [scintillator_horizontal_roi[0] + 5, scintillator_horizontal_roi[1] - 5]
    scintillator_vertical_roi = [scintillator_vertical_roi[0] + 5, scintillator_vertical_roi[1] - 5]
    
    if show_images:
        display_image_with_roi(image, scintillator_horizontal_roi, scintillator_vertical_roi)
    
    scintillator_region = image[scintillator_vertical_roi[0]:scintillator_vertical_roi[-1], scintillator_horizontal_roi[0]:scintillator_horizontal_roi[-1]]
    
    x_bounds, y_bounds = roi_determination_inside_scintillator(scintillator_region, scintillator_horizontal_roi, scintillator_vertical_roi, 
                                                              show_plots=show_images, fraction=fraction)
    
    print(x_bounds, y_bounds)
    original_image_x_bounds = x_bounds + scintillator_horizontal_roi[0] 
    original_image_y_bounds = y_bounds + scintillator_vertical_roi[0]
    
    if show_images:
        display_image_with_roi(image, original_image_x_bounds, original_image_y_bounds)
    
    return original_image_x_bounds, original_image_y_bounds
