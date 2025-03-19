from calibration_functions import generate_real_grid_positions
from distortion_correction import plot_chessboard_corners

GRID_SIZE = (20, 5)
SPACING = [2,3]

obj_points = generate_real_grid_positions(GRID_SIZE, SPACING)
plot_chessboard_corners(obj_points)
