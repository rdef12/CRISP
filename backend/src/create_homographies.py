import cv2
import numpy as np
from src.calibration_functions import *
from src.distortion_correction import *
from src.viewing_functions import *
from src.homography_errors import generate_homography_covariance_matrix

# FRONT_CALIBRATION_IMAGE_PATH = "pinpointing_test_images/side_arducam_front_chessboard_calibration_20_by_10_spacing_10mm.jpeg"
# REAR_CALIBRATION_IMAGE_PATH = "pinpointing_test_images/side_arducam_back_chessboard_calibration_20_by_10_spacing_10mm.jpeg"

FRONT_CALIBRATION_IMAGE_PATH = "pinpointing_test_images/top_arducam_front_chessboard_calibration_20_by_5_spacing_10mm.jpeg"
REAR_CALIBRATION_IMAGE_PATH = "pinpointing_test_images/top_arducam_back_chessboard_calibration_20_by_5_spacing_10mm.jpeg"

DISTORTION_CALIBRATION_PATH = "distortion_calibration_data/top_hq_camera_calibration.pkl"

X_GRID_UNC = 0.1 # mm
Y_GRID_UNC = 0.1 # mm

def save_homography_data(data_file_path: str, homography_matrix: np.ndarray[float, float],
                         homography_covariance: np.ndarray[float, float]):
    
        with open(data_file_path, "w") as f:
            np.savetxt(f, homography_matrix, delimiter=",", header="Homography Matrix")
            f.write("\n")
            np.savetxt(f, homography_covariance, delimiter=",", header="Homography Covariance")
            return None
        
        
def load_homography_data(data_file_path: str):
    
    with open(data_file_path, "r") as f:
        lines = f.readlines()
    split_indices = [i for i, line in enumerate(lines) if line.strip() == ""] # Find empty line

    homography_matrix = np.loadtxt(lines[1:split_indices[0]], delimiter=",")
    homography_position_covariance = np.loadtxt(lines[split_indices[0] + 2:], delimiter=",")

    return homography_matrix, homography_position_covariance


def build_calibration_plane_homography(image_path: str, calibration_pattern: str, 
                                        calibration_grid_size: tuple[int, int], pattern_spacing: float, 
                                        grid_uncertainties: tuple[int, int], correct_for_distortion: bool=False,
                                        distortion_calibration_path: str|None=None,
                                        show_recognised_chessboard: bool=False,
                                        save_file_path: str|None=None):
        
        if correct_for_distortion and distortion_calibration_path is None:
            raise ValueError("distortion_calibration_path must be provided when correct_for_distortion=True")
        if correct_for_distortion:
            camera_matrix, dist = load_camera_calibration(distortion_calibration_path)
            frame_size = determine_frame_size(image_path=image_path)
            image = undistort_image(camera_matrix, dist, frame_size, image_path=image_path)
        else:
            image = cv2.imread(image_path)
            
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

        real_grid_positions = generate_real_grid_positions(calibration_grid_size, pattern_spacing)
        match calibration_pattern:
            case "chessboard":
                image_grid_positions, ret = find_image_grid_positions_chessboard(grey_image, calibration_grid_size)
            case "symmetric_circles":
                image_grid_positions, ret = find_image_grid_positions_circles(grey_image, calibration_grid_size)
            case _:
                raise Exception("No calibration pattern called {} defined".format(calibration_pattern))

        # RUDIMENTARY reverse of real grid points based on where first image point is.
        # Reverses image grid positions array if first x coord bigger than last x coord
        if image_grid_positions[0, 0, 0] > image_grid_positions[-1, 0, 0]:
            image_grid_positions = image_grid_positions[::-1]
            
        if show_recognised_chessboard:
            first_position = tuple(image_grid_positions[0].ravel().astype(int))
            cv2.circle(image, first_position, radius=40, color=(0, 255, 0), thickness=-1)
            print("{0} origin is at the pixel {1} (marked with a green circle)".format(real_grid_positions[0], first_position))
            overlay_identified_grid("Overlayed grid", image, image_grid_positions, calibration_grid_size, ret)

        homography_matrix, _ = cv2.findHomography(image_grid_positions, real_grid_positions)
        grid_uncertainties_array = np.full((len(image_grid_positions), 2), grid_uncertainties)
        homography_covariance = generate_homography_covariance_matrix(image_grid_positions, homography_matrix, grid_uncertainties_array)
        
        if save_file_path is not None:
            save_homography_data(save_file_path, homography_matrix, homography_covariance)
            
        return homography_matrix, homography_covariance, image_grid_positions
    
    
def main():
    """
    NOTE - All the camera properties are entered manually here. In reality, these arguments would need
    sourcing from the camera/setup table of the database.
    """
    
    # build_calibration_plane_homography(FRONT_CALIBRATION_IMAGE_PATH, "chessboard", (20, 5), 10, (X_GRID_UNC, Y_GRID_UNC), save_file_path="homography_data/front_plane_top_hq_homography.csv",
    #                                    correct_for_distortion=True, distortion_calibration_path=DISTORTION_CALIBRATION_PATH,
    #                                    show_recognised_chessboard=True)
    # build_calibration_plane_homography(REAR_CALIBRATION_IMAGE_PATH,  "chessboard", (20, 5), 10, (X_GRID_UNC, Y_GRID_UNC), save_file_path="homography_data/rear_plane_top_hq_homography.csv",
    #                                    correct_for_distortion=True, distortion_calibration_path=DISTORTION_CALIBRATION_PATH,
    #                                    show_recognised_chessboard=True)
    
    build_calibration_plane_homography(FRONT_CALIBRATION_IMAGE_PATH, "chessboard", (20, 5), 10, (X_GRID_UNC, Y_GRID_UNC), save_file_path="homography_data/front_plane_top_arducam_homography.csv",
                                       show_recognised_chessboard=True)
    build_calibration_plane_homography(REAR_CALIBRATION_IMAGE_PATH,  "chessboard", (20, 5), 10, (X_GRID_UNC, Y_GRID_UNC), save_file_path="homography_data/rear_plane_top_arducam_homography.csv",
                                       show_recognised_chessboard=True)
    
    return None
    

if __name__ == "__main__":
    main()