import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from src.edge_detection_functions import find_beam_contour_extremes
import io
from src.database.CRUD import CRISP_database_interaction as cdi

# SIDE_SCINTILLATOR_HORIZONTAL_ROI = [875, 3500]
# SIDE_SCINTILLATOR_VERTICAL_ROI = [530, 1650]

# TOP_SCINTILLATOR_HORIZONTAL_ROI = [700, 3100]
# TOP_SCINTILLATOR_VERTICAL_ROI = [990, 1400]

def get_scintillator_pixel_dimensions(scintillator_horizontal_roi, scintillator_vertical_roi):
    
    horizontal_pixel_width = abs(scintillator_horizontal_roi[1] - scintillator_horizontal_roi[0])
    vertical_pixel_width = abs(scintillator_vertical_roi[1] - scintillator_vertical_roi[0])
    return horizontal_pixel_width, vertical_pixel_width

    
def roi_determination_inside_scintillator(camera_analysis_id, image, scintillator_horizontal_roi, scintillator_vertical_roi,
                                          use_edge_detection: bool=True, verbose_output: bool=False,
                                          show_plots: bool=False, fraction: float=0.15, save_to_database: bool=False):
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
    # print("\n\nHorizontal pixel width: ", horizontal_pixel_width)
    # print("\n\nVertical pixel width: ", vertical_pixel_width)
    
    if verbose_output:
        background_brightness_value = np.min(image)
        print("Background brightness = {}\n".format(background_brightness_value) + "Minimum f = {}".format(background_brightness_value/peak_brightness_value))

    peak_brightness_value = np.max(image)
    mask = image > peak_brightness_value * fraction
    binary_image = (mask.astype(np.uint8)) * 255
    
    _, image_bytes = cv.imencode('.png', binary_image)  # Encode the image as a PNG
    cdi.add_camera_analysis_plot(camera_analysis_id, f"binary_beam", image_bytes, "png",
                                 description=f"Binary thresholded averaged image")
    
    if use_edge_detection:
        x_bounds, y_bounds = find_beam_contour_extremes(camera_analysis_id, binary_image, horizontal_pixel_width, vertical_pixel_width, show_image=show_plots,
                                                        save_to_database=save_to_database)
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

def get_image_with_roi(image, horizontal_roi, vertical_roi, show_plot: bool=False):
    blue_image = cv.merge([np.zeros_like(image), np.zeros_like(image), image])
    
    # plt.imshow(rgb_image)
    # plt.axvline(horizontal_roi[0], color='red')
    # plt.axvline(horizontal_roi[1], color='red')
    # plt.axhline(vertical_roi[0], color='red')
    # plt.axhline(vertical_roi[1], color='red')
    
    fig, ax = plt.subplots()
    ax.imshow(blue_image)

    # Define rectangle parameters
    x = horizontal_roi[0]
    y = vertical_roi[0]
    width = horizontal_roi[1] - horizontal_roi[0]
    height = vertical_roi[1] - vertical_roi[0]

    # Create and add the rectangle patch
    rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='red', facecolor='none')
    ax.add_patch(rect)
    
    if show_plot:
        plt.show()

    buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
    plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
    plt.close()
    buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
    return buf.read()

def get_automated_roi(camera_analysis_id, image, scintillator_horizontal_roi, scintillator_vertical_roi, show_images: bool=False,
                      fraction: float=0.15, save_to_database: bool=False):
    """
    Expects an image with a single colour channel inputted (includes greyscale)
    """
    
    try:
        # 5 pixel padding added around the user defined region of interests - visible scintillator edges will interfere with beam edge detection
        scintillator_horizontal_roi = [scintillator_horizontal_roi[0] + 5, scintillator_horizontal_roi[1] - 5]
        scintillator_vertical_roi = [scintillator_vertical_roi[0] + 5, scintillator_vertical_roi[1] - 5]
        
        # print("\n\nScintillator horizontal ROI: ", scintillator_horizontal_roi)
        # print("\n\nScintillator vertical ROI: ", scintillator_vertical_roi)
        scintillator_region = image[scintillator_vertical_roi[0]:scintillator_vertical_roi[-1], scintillator_horizontal_roi[0]:scintillator_horizontal_roi[-1]]
        
        x_bounds, y_bounds = roi_determination_inside_scintillator(camera_analysis_id, scintillator_region, scintillator_horizontal_roi, scintillator_vertical_roi, 
                                                                   show_plots=show_images, fraction=fraction, save_to_database=save_to_database)
        # print("\n\nx bounds: ", x_bounds)
        # print("\n\ny bounds: ", y_bounds)
        
        original_image_x_bounds = x_bounds + scintillator_horizontal_roi[0] 
        original_image_y_bounds = y_bounds + scintillator_vertical_roi[0]
        
        automated_roi_restricted_region = image[original_image_y_bounds[0]:original_image_y_bounds[1], original_image_x_bounds[0]:original_image_x_bounds[1]]
    
        # inRange here gets all pixels between 0 and 1 pixel intensity
        low_intensity_mask = cv.inRange(automated_roi_restricted_region, 0, 1/255) # image normalised by inRange
        if low_intensity_mask is not None:
            scintillator_mask = cv.bitwise_not(low_intensity_mask)
            # Find rows that contain only 255s (i.e., no low intensity at all)
            valid_rows = np.where(np.all(scintillator_mask == 255, axis=1))[0]

            if len(valid_rows) > 0:
                y_start, y_end = valid_rows[0], valid_rows[-1] + 1
                cropped = automated_roi_restricted_region[y_start:y_end, :]
            else:
                raise ValueError("No valid rows found in the scintillator mask.")
            
            original_image_y_bounds[0] += y_start
            original_image_y_bounds[1] = original_image_y_bounds[0] + (y_end - y_start)
    
        base64_roi_image = get_image_with_roi(image, original_image_x_bounds, original_image_y_bounds, show_plot=show_images)
        
        return (original_image_x_bounds, original_image_y_bounds), base64_roi_image
    except Exception as e:
        print(f"Error in get_automated_roi: {e}")
        raise Exception("Error in get_automated_roi") from e
