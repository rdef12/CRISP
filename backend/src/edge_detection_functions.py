import cv2
import numpy as np
import matplotlib.pyplot as plt


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

  edges = cv2.Canny(img, lower, upper)

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


def find_beam_contour_extremes(image, horizontal_pixel_width, vertical_pixel_width, show_image: bool=False):
    """
    Binary/greyscale image assumed as input. In our case, it is for the blue channel of the image.
    """
    
    edges = detect_edges(image) # Could look at changing aperture size to smoothen edges further still

    if show_image:
      plt.figure()
      plt.title("Edge Detection Output")
      plt.imshow(edges, cmap='gray')
      plt.show()
    
    # Morphological Operations - dilation and erosion?
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if show_image:
      plt.imshow(image)
      plt.title("All contours")
      for contour in contours:
        coords = np.array([pt[0] for pt in contour])
        plt.scatter(coords[:, 0], coords[:, 1], s=1, color='red')
      plt.show()

    valid_contours = []
    valid_minimum_perimeter = int(0.9 * min(horizontal_pixel_width, vertical_pixel_width)) # Still somewhat arbitrary - but now derived from scintillator dimensions
    for contour in contours:
        perimeter = cv2.arcLength(contour, False) # I think false here means the contour can be open
        
        if perimeter > valid_minimum_perimeter: 
            valid_contours.append(contour)
            
    if show_image:
      plt.imshow(image)
      plt.title("Valid contours")
      for contour in valid_contours:
        coords = np.array([pt[0] for pt in contour])
        plt.scatter(coords[:, 0], coords[:, 1], s=1, color='red')
      plt.show()

    if valid_contours:
        all_points = np.vstack(valid_contours) # Collect all x, y points from all valid contours
        x_coords, y_coords = all_points[:, 0, 0], all_points[:, 0, 1]
    else:
        print("No valid beam contour found! Will try using contours without blemish detection")
        exit()
    
    x_min, x_max = np.min(x_coords), np.max(x_coords)
    y_min, y_max = np.min(y_coords), np.max(y_coords)
      
    return np.array([x_min, x_max]), np.array([y_min, y_max])

