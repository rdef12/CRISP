import cv2
import numpy as np
import matplotlib.pyplot as plt
from src.database.CRUD import CRISP_database_interaction as cdi
import io


def calculate_threshold(img):
  """
  Author: Rutuparn Pawar/InputBlackBoxOutput on GitHub
  Calculates Otsu Thresholds
  """
  hist, bin_edges = np.histogram(img, bins=256)
  bin_mids = (bin_edges[:-1] + bin_edges[1:]) / 2.

  weight1 = np.cumsum(hist)
  weight2 = np.cumsum(hist[::-1])[::-1]
  mean1 = np.cumsum(hist * bin_mids) / weight1
  mean2 = (np.cumsum((hist * bin_mids)[::-1]) / weight2[::-1])[::-1]

  inter_class_variance = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2
  index_of_max_val = np.argmax(inter_class_variance)

  return bin_mids[:-1][index_of_max_val]

def detect_edges(img):
  """
  Author: Rutuparn Pawar/InputBlackBoxOutput on GitHub
  Canny edge detection with Otsu thresholds.
  """
  t = calculate_threshold(img)
  lower = int(max(0, t * 0.5))
  upper = int(min(255, t))
  # print(f"Lower threshold: {lower}, Upper threshold: {upper}")

  edges = cv2.Canny(img, lower, upper, apertureSize=5) # apertureSize = 3 is the default value
  return edges


def auto_digital_gain_calculation(image):
  """
  Divide 255 by the brightest pixel value within the image.
  
  Using this as the digital gain does not allow the beam's contour to be identified,
  therefore for digital gain to be useful in edge detection, the light distribution
  must be saturated around the Bragg peak region of the image.
  
  Seems then that this hack needs to be replaced by something like adaptive thresholding.
  """
  
  brightest_pixel_value = np.max(image)
  digital_gain = 255 / brightest_pixel_value
  print(f"Gain determined is {digital_gain}")
  return digital_gain


def find_beam_contour_extremes(camera_analysis_id, image, horizontal_pixel_width, vertical_pixel_width, show_image: bool=False,
                               save_to_database: bool=False):
    """
    Binary/greyscale image assumed as input. In our case, it is for the blue channel of the image.
    """
    
    if show_image:
      plt.hist(image.ravel(), bins=256)
      t = calculate_threshold(image)
      plt.axvline(x=t, color='r', label='Otsu threshold')
      plt.axvline(x=int(max(0, t * 0.5)), color='g', label='Lower threshold')
      plt.axvline(x=int(min(255, t)), color='orange', label='Upper threshold')
      plt.title("Pixel Intensities with thresholds for Canny edge detection")
      plt.show()
      plt.close()
    
    edges = detect_edges(image) # Could look at changing aperture size to smoothen edges further still

    if show_image:
      plt.figure()
      plt.title("Edge Detection Output")
      plt.imshow(edges, cmap='gray')
      plt.show()
    
    # Morphological Operations - dilation and erosion?
    
    # kernel = np.ones((3, 3), np.uint8)
    kernel = np.ones((5, 5), np.uint8)
    # kernel = np.ones((21, 21), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if show_image:
      plt.imshow(image)
      plt.title("All contours")
      for contour in contours:
        coords = np.array([pt[0] for pt in contour])
        plt.scatter(coords[:, 0], coords[:, 1], s=1, color='red')
      plt.show()

    valid_contours = {} # key = perimeter, value = contour
    
    # This doesn't really work because the bumpy contours get very long relative to this "minimum" value
    valid_minimum_perimeter = int(0.95 * min(horizontal_pixel_width, vertical_pixel_width)) # Still somewhat arbitrary - but now derived from scintillator dimensions
    for contour in contours:
        perimeter = cv2.arcLength(contour, False) # I think false here means the contour can be open
        if perimeter > valid_minimum_perimeter: 
            valid_contours[perimeter] = contour
            
    longest_perimeter = max(valid_contours.keys())
    longest_contour = valid_contours[longest_perimeter]
    
    # epsilon = 0.5 * longest_perimeter # epsilon = how close the approximation is to the original contour
    # longest_contour = cv2.approxPolyDP(longest_contour, epsilon, True) # smoothened out
            
    if show_image or save_to_database:
      plt.imshow(image)
      plt.title("Valid contours")
      for contour in valid_contours.values():
        coords = np.array([pt[0] for pt in contour])
        if contour is longest_contour:
          plt.scatter(coords[:, 0], coords[:, 1], s=1, color='green', label='Longest contour')
          continue
        plt.scatter(coords[:, 0], coords[:, 1], s=1, color='red')
      plt.legend()
      if show_image:
        plt.show()
        plt.close()
      elif save_to_database:
        buf = io.BytesIO()  # Create an in-memory binary stream (buffer)
        plt.savefig(buf, format="svg", dpi=600)  # Save the current plot to the buffer
        plt.close()
        buf.seek(0)  # Reset the buffer's position to the beginning - else will read from the end
        plot_bytes = buf.read()
        cdi.add_camera_analysis_plot(camera_analysis_id, f"beam_contour_plot", plot_bytes, "svg",
                                     description=f"Plot showing the identified beam contours extracted by edge detection")
      
    
    # if longest_contour is None:
    #     raise Exception("No valid beam contour found!")
    # x_coords, y_coords = longest_contour[:, 0, 0], longest_contour[:, 0, 1]

    if valid_contours:
      all_points = np.vstack([contour.reshape(-1, 2) for contour in valid_contours.values()]) # Collect all x, y points from all valid contours
      x_coords, y_coords = all_points[:, 0], all_points[:, 1]
    else:
        print("No valid beam contour found! Will try using contours without blemish detection")
        raise Exception("No valid beam contour found!")
    
    x_min, x_max = np.min(x_coords), np.max(x_coords)
    y_min, y_max = np.min(y_coords), np.max(y_coords)
    
    return np.array([x_min, x_max]), np.array([y_min, y_max])

