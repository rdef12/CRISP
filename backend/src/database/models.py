from typing import Optional, List, Literal
from datetime import datetime
import numpy as np
from enum import Enum

# Used for typehinting - cannot use Literal type as an SQL column
class OpticalAxisEnum(str, Enum):
    x = "x"
    y = "y"
    z = "z"

class DepthDirectionEnum(int, Enum):
    POSITIVE = 1
    NEGATIVE = -1
    
class ImageBeamDirectionEnum(str, Enum):
    TOP = "top"
    RIGHT = "right"
    BOTTOM = "bottom"
    LEFT = "left"
    
class ColourChannelEnum(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    GRAY = "gray"
    GREY = "grey"

# from sqlmodel import Field, SQLModel, PickleType, JSON, Column, ARRAY, Integer, LargeBinary, Relationship
from sqlmodel import Field, SQLModel, PickleType, JSON, LargeBinary, Relationship
from sqlalchemy import Column, ARRAY, Float, Integer, String, Text

class Setup(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    date_created: datetime
    date_last_edited: datetime
# Block parameters
    block_x_dimension: Optional[float]
    block_x_dimension_unc: Optional[float]
    block_y_dimension: Optional[float]
    block_y_dimension_unc: Optional[float]
    block_z_dimension: Optional[float]
    block_z_dimension_unc: Optional[float]
    block_refractive_index: Optional[float]
    block_refractive_index_unc: Optional[float]
    # e_log_entry: Optional[bytes] #How is this going to be stored, surely theres a better way than just a string?

    experiments: list["Experiment"] = Relationship(back_populates="setup")
    camera_links: list["CameraSetupLink"] = Relationship(back_populates="setup")


class CameraSetupLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_id: Optional[int] = Field(default=None, foreign_key="camera.id")
    setup_id: Optional[int] = Field(default=None, foreign_key="setup.id")

    camera: "Camera" = Relationship(back_populates="setup_links")
    setup: "Setup" = Relationship(back_populates="camera_links")

    #Calibration parameters
# General homography
    optical_axis: Optional[OpticalAxisEnum] = Field(default=None)
    depth_direction: Optional[DepthDirectionEnum] = Field(default=None) # used to specify which side of the origin the cam is along optical axis
    image_beam_direction: Optional[ImageBeamDirectionEnum] = Field(default=None) # used to orient images before applying analysis
    
# Far face homography
    #Calibration pattern type here too?
    far_face_calibration_pattern_size: Optional[List[int]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    far_face_calibration_pattern_type: Optional[str] = Field(default=None)
    far_face_calibration_spacing: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    far_face_calibration_spacing_unc: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    far_face_calibration_photo_camera_settings_id: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
    far_face_homography_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType)
    far_face_homography_covariance_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType)
    # far_face_calibratoin_photo_settings_id: Optional[int] = Field(default=None, foreign_key="settings.id") # Add back filling bit to settings
    # far_face_calibration_photo: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    # far_face_calibration_photo_id: Optional[int] = Field(default=None, foreign_key="photo.id")

    
    # NOTE - below replaced with calibraiton board thickness and Z/non-Z shifts
    # far_x_offset: Optional[float] = Field(default=None)
    # far_x_offset_unc: Optional[float] = Field(default=None)
    # far_y_offset: Optional[float] = Field(default=None)
    # far_y_offset_unc: Optional[float] = Field(default=None)
    # far_z_offset: Optional[float] = Field(default=None)
    # far_z_offset_unc: Optional[float] = Field(default=None)
    far_face_z_shift: Optional[float] = Field(default=None)
    far_face_z_shift_unc: Optional[float] = Field(default=None)
    far_face_non_z_shift: Optional[float] = Field(default=None)
    far_face_non_z_shift_unc:  Optional[float] = Field(default=None)
    far_face_calibration_board_thickness:  Optional[float] = Field(default=None)
    far_face_calibration_board_thickness_unc: Optional[float] = Field(default=None)
    
# Near face homography
    near_face_calibration_pattern_size: Optional[List[int]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    near_face_calibration_pattern_type: Optional[str] = Field(default=None)
    near_face_calibration_spacing: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    near_face_calibration_spacing_unc: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    # near_face_calibratoin_photo_settings_id: Optional[int] = Field(default=None, foreign_key="settings.id") # Add back filling bit to setting
    near_face_calibration_photo_camera_settings_id: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
    # near_face_calibration_photo: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    # near_face_calibration_photo_id: Optional[int] = Field(default=None, foreign_key="photo.id")
    near_face_homography_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType) # How do you show 2d shape? (3x3 array)
    near_face_homography_covariance_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType) # How do you show 2d shape? (9x9 array)
    near_face_z_shift: Optional[float] = Field(default=None)
    near_face_z_shift_unc: Optional[float] = Field(default=None)
    near_face_non_z_shift: Optional[float] = Field(default=None)
    near_face_non_z_shift_unc: Optional[float] = Field(default=None)
    near_face_calibration_board_thickness: Optional[float] = Field(default=None)
    near_face_calibration_board_thickness_unc: Optional[float] = Field(default=None)
    
# Others
    scintillator_edges_photo_camera_settings_id: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
    # horizontal_scintillator_limits: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer))) # How do you show 2d shape? (4x1 of 2x2 array)
    horizontal_scintillator_start: Optional[int]
    horizontal_scintillator_end: Optional[int]
    vertical_scintillator_start: Optional[int]
    vertical_scintillator_end: Optional[int]
    # vertical_scintillator_limits: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer))) # How do you show 2d shape? (4x1 of 2x2 array)#TODO these should be int type surely
# Distortion calibration
    do_distortion_calibration: Optional[bool] = Field(default=None)
    # distortion_calibration_pattern_size: Optional[List[int]] = Field(default=None, sa_column=Column(ARRAY(Integer))) # Removed by Robin for ease
    distortion_calibration_pattern_size_z_dim: Optional[int] = Field(default=None)
    distortion_calibration_pattern_size_non_z_dim: Optional[int] = Field(default=None)
    distortion_calibration_pattern_type: Optional[str] = Field(default=None)
    distortion_calibration_pattern_spacing: Optional[float] = Field(default=None) # in mm
    camera_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType)
    distortion_coefficients: Optional[bytes] = Field(default=None, sa_column=PickleType)
    distortion_calibration_camera_settings_link: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
# Others
    lens_position: Optional[float] = Field(default=None)
    # e_log_entry: #How is this going to be stored, surely theres a better way than just a string?



class Experiment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    date_started: datetime
#Links
    setup_id: int = Field(default=None, foreign_key="setup.id")
    setup: Setup = Relationship(back_populates="experiments")

    beam_runs: list["BeamRun"] = Relationship(back_populates="experiment")


# class BeamRunNumber(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     beam_run_number: int
#     datetime_of_run: datetime
#     ESS_beam_energy: float
#     # ESS_beam_energy_unc: float #????
#     MSIC_beam_energy: Optional[float] = Field(default=None)
#     MSIC_beam_energy_unc: Optional[float] = Field(default=None)
#     beam_current: float
#     beam_current_unc: float
#     #Any other beam parameters?

#     experiment_id: int = Field(default=None, foreign_key="experiment.id")
#     experiment: Experiment = Relationship(back_populates="beam_runs")

#     test_beam_runs: list["TestBeamRun"] = Relationship(back_populates="beam_run_number")
#     real_beam_runs: list["RealBeamRun"] = Relationship(back_populates="beam_run_number")


# class TestBeamRun(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     # datetime_of_run: datetime
#     # ESS_beam_energy: float
#     # # ESS_beam_energy_unc: float #????
#     # MSIC_beam_energy: float
#     # MSIC_beam_energy_unc: float
#     # beam_current: float
#     # beam_current_unc: float
#     # #Any other beam parameters?
# #Links
#     beam_run_number_id: int = Field(default=None, foreign_key="beamrunnumber.id")
#     beam_run_number: BeamRunNumber = Relationship(back_populates="test_beam_runs")

#     test_beam_run_photos: list["TestBeamRunPhoto"] = Relationship(back_populates="test_beam_run")


# class TestBeamRunPhoto(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     is_optimal_gain: Optional[bool] = Field(default=None)
#     photo: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
#     photo_metadata: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary)) #Does this need to be large?

# #Links
#     test_beam_run_id: int = Field(default=None, foreign_key="testbeamrun.id")
#     test_beam_run: TestBeamRun = Relationship(back_populates="test_beam_run_photos")

#     camera_id: int = Field(default=None, foreign_key="camera.id")
#     camera: "Camera" = Relationship(back_populates="test_beam_run_photos")

#     settings_id: int = Field(default=None, foreign_key="settings.id")
#     settings: "Settings" = Relationship(back_populates="test_beam_run_photos")


# class RealBeamRun(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     # datetime_of_run: datetime
#     # ESS_beam_energy: float
#     # # ESS_beam_energy_unc: float #????
#     # MSIC_beam_energy: float
#     # MSIC_beam_energy_unc: float
#     # beam_current: float
#     # beam_current_unc: float
#     # #Any other beam parameters?
# #Results from analysis
# #Links
#     beam_run_number_id: int = Field(default=None, foreign_key="beamrunnumber.id")
#     beam_run_number: BeamRunNumber = Relationship(back_populates="real_beam_runs")

#     real_beam_run_settings_and_cameras: list["RealBeamRunSettingsAndCamera"] = Relationship(back_populates="real_beam_run")


# class RealBeamRunSettingsAndCamera(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     real_beam_run_id: int = Field(default=None, foreign_key="realbeamrun.id")
#     real_beam_run: "RealBeamRun" = Relationship(back_populates="real_beam_run_settings_and_cameras")

#     camera_id: int = Field(default=None, foreign_key="camera.id")
#     camera: "Camera" = Relationship(back_populates="real_beam_run_settings_and_cameras")

#     settings_id: int = Field(default=None, foreign_key="settings.id")
#     settings: "Settings" = Relationship(back_populates="real_beam_run_settings_and_cameras")

#     real_beam_run_photos: list["RealBeamRunPhoto"] = Relationship(back_populates="real_beam_run_settings_and_cameras")



# class RealBeamRunPhoto(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     photo: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
#     photo_metadata: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary)) #Does this need to be large?

# #Links
#     real_beam_run_settings_and_cameras_id: int = Field(default=None, foreign_key="realbeamrunsettingsandcamera.id")
#     real_beam_run_settings_and_cameras: "RealBeamRunSettingsAndCamera" = Relationship(back_populates="real_beam_run_photos")


# class Settings(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     #Camera settings (needs to expand to full list)
#     frame_rate: int
#     lens_position: float
#     gain: float

#     test_beam_run_photos: list["TestBeamRunPhoto"] = Relationship(back_populates="settings")
#     real_beam_run_settings_and_cameras: list["RealBeamRunSettingsAndCamera"] = Relationship(back_populates="settings")

###################################################################################################################################

class Camera(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    ip_address: str
    password: str
    model: str #e.g. AR, HQ, etc

    # beam_run_camera_settings: list["BeamRunCameraSettings"] = Relationship(back_populates="camera")
    setup_links: list["CameraSetupLink"] = Relationship(back_populates="camera")
    settings_links: list["CameraSettingsLink"] = Relationship(back_populates="camera")


class Settings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    #Camera settings (needs to expand to full list)
    frame_rate: int
    lens_position: float
    gain: float

    camera_links: list["CameraSettingsLink"] = Relationship(back_populates="settings")
    # beam_run_camera_settings: list["BeamRunCameraSettings"] = Relationship(back_populates="settings")


class CameraSettingsLink(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_id: int = Field(default=None, foreign_key="camera.id")
    settings_id: int = Field(default=None, foreign_key="settings.id")

    # beam_run_id: Optional
    is_optimal: Optional[bool] = Field(default=None) # Set true/false when associated with a test beam run left Null otherwise
    number_of_images: Optional[int] = Field(default=None)
    take_raw_images: Optional[bool] = Field(default=None)

    camera: "Camera" = Relationship(back_populates="settings_links")
    settings: "Settings" = Relationship(back_populates="camera_links")

    photos: List["Photo"] = Relationship(back_populates="camera_settings_link")

    # beam_runs: List["BeamRun"] = Relationship(back_populates="camera_settings_link")
    beam_run_id: Optional[int] = Field(default=None, foreign_key="beamrun.id")
    beam_run: "BeamRun" = Relationship(back_populates="camera_settings_links")


class Photo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_settings_link_id: int = Field(default=None, foreign_key="camerasettingslink.id")
    photo: bytes = Field(default=None, sa_column=Column(LargeBinary))
    photo_metadata: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary)) #TODO Temporarily optional for testing

    camera_settings_link: CameraSettingsLink = Relationship(back_populates="photos")


class BeamRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    beam_run_number: int
    datetime_of_run: datetime
    ESS_beam_energy: float
    beam_current: float
    # ESS_beam_energy_unc: float #????
    MSIC_beam_energy: Optional[float] = Field(default=None)
    MSIC_beam_energy_unc: Optional[float] = Field(default=None)
    MSIC_beam_current: Optional[float] = Field(default=None)
    MSIC_beam_current_unc: Optional[float] = Field(default=None)

    #Any other beam parameters?

    is_test: bool
    
    # num_of_images_to_capture: Optional[int] = Field(default=None)
    # take_raw_images: Optional[bool] = Field(default=None)
    bragg_peak_3d_position: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    unc_bragg_peak_3d_position: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    
    beam_incident_3d_position: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    unc_beam_incident_3d_position: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    beam_path_vector: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    unc_beam_path_vector: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    
    bragg_peak_depth: Optional[float] = Field(default = None)
    unc_bragg_peak_depth: Optional[float] = Field(default = None)

    experiment_id: int = Field(default=None, foreign_key="experiment.id")
    experiment: Experiment = Relationship(back_populates="beam_runs")

    # camera_settings_link_id: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
    # camera_settings_link: Optional["CameraSettingsLink"] = Relationship(back_populates="beam_runs")
    camera_settings_links: List["CameraSettingsLink"] = Relationship(back_populates="beam_run")
    
    #camera_analyses: List["CameraAnalysis"] = Relationship(back_populates="beam_run")

#     beam_run_camera_settings: list["BeamRunCameraSettings"] = Relationship(back_populates="beam_run_number")

class CameraAnalysis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # beam_run_id: int = Field(default=None, foreign_key="beamrun.id") # not optional
    # beam_run: "BeamRun" = Relationship(back_populates="camera_analyses")
    camera_settings_id: int = Field(default=None, foreign_key="camerasettingslink.id") # not optional
    
    colour_channel: ColourChannelEnum = Field(default=None) # not optional
    average_image: Optional[bytes] = Field(default=None, sa_column=PickleType)
    beam_angle: Optional[float] = Field(default=None)
    unc_beam_angle: Optional[float] = Field(default=None)
    bragg_peak_pixel: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    unc_bragg_peak_pixel: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    range: Optional[float] = Field(default=None)
    range_uncertainty: Optional[float] = Field(default=None)

    camera_analysis_plots: List["CameraAnalysisPlot"] = Relationship(back_populates="camera_analysis")


class CameraAnalysisPlot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    camera_analysis_id: int = Field(default=None, foreign_key="cameraanalysis.id")

    plot_type: str
    plot_figure: bytes = Field(default=None, sa_column=Column(LargeBinary)) # Not base64!!!
    figure_format: str = Field(default=None) # SVG usually but PNG for OpenCV overlays
    parameter_labels: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    parameter_values: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
    parameter_uncertainties: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))

    chi_squared: Optional[float] = Field(default=None)
    number_of_data_points: Optional[int] = Field(default=None)

    description: Optional[str] = Field(default=None)

    camera_analysis: CameraAnalysis = Relationship(back_populates="camera_analysis_plots")

# class BeamRunPlots(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     beam_run_id: int = Field(default=None, foreign_key="cameraanalysis.id")

#     plot_type: str
#     plot_figure: bytes = Field(default=None, sa_column=Column(LargeBinary))
#     parameter_labels: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
#     parameter_values: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))
#     parameter_uncertainties: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Float)))

#     chi_squared: Optional[float] = Field(default=None)
#     number_of_data_points: Optional[int] = Field(default=None)

#     description: Optional[str] = Field(default=None)

#     camera_analysis: CameraAnalysis = Relationship(back_populates="camera_analysis_plots")

    # class BeamRunCameraSettings(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     beam_run_number_id: int = Field(default=None, foreign_key="beamrunnumber.id")
#     camera_id: int = Field(default=None, foreign_key="camera.id")
#     settings_id: int = Field(default=None, foreign_key="settings.id")

#     is_optimal: Optional[bool] = Field(default=None)

#     photos: list["Photo"] = Relationship(back_populates="beam_run_camera_settings")


# class Photo(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     photo: bytes = Field(default=None, sa_column=Column(LargeBinary))
#     photo_metadata: bytes = Field(default=None, sa_column=Column(LargeBinary))

#     beam_run_camera_settings_id: int = Field(default=None, foreign_key="beamruncamerasettings.id")