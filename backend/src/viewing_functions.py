import numpy as np
import cv2
import matplotlib.pyplot as plt

def show_image_in_window(window_name: str, image: np.ndarray):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

def overlay_identified_grid(window_name: str, image: np.ndarray[int, int], image_grid_positions: np.ndarray[float, float], grid_size: tuple[int, int], ret):
    cv2.drawChessboardCorners(image, grid_size, image_grid_positions, ret)
    show_image_in_window(window_name, image)
    cv2.imwrite("31_10_24_marked_calibration_grid_test.jpg", image)
    return

def plot_chessboard_corners(real_grid_positions):
    
    real_grid_positions = real_grid_positions.reshape(-1, 2)
    plt.scatter(real_grid_positions[:, 0], real_grid_positions[:, 1])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show(block=True)