from typing import Optional, List
from datetime import datetime
import numpy as np

from sqlmodel import Field, SQLModel, PickleType, JSON, Column, ARRAY, Integer, LargeBinary, Relationship
# from sqlalchemy.dialects import postgresql #ARRAY contains requires dialect specific type

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
# Far face
    #Calibration pattern type here too?
    far_face_calibration_pattern_size: Optional[List[int]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    far_face_calibration_pattern_type: Optional[str] = Field(default=None)
    far_face_calibration_spacing: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    far_face_calibration_spacing_unc: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    # far_face_calibratoin_photo_settings_id: Optional[int] = Field(default=None, foreign_key="settings.id") # Add back filling bit to settings
    # far_face_calibration_photo_camera_settings_link: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
    # far_face_calibration_photo: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    far_face_calibration_photo_id: Optional[int] = Field(default=None, foreign_key="photo.id")

    far_face_homography_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType)
    far_face_homography_covariance_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType)
    far_x_offset: Optional[float] = Field(default=None)
    far_x_offset_unc: Optional[float] = Field(default=None)
    far_y_offset: Optional[float] = Field(default=None)
    far_y_offset_unc: Optional[float] = Field(default=None)
    far_z_offset: Optional[float] = Field(default=None)
    far_z_offset_unc: Optional[float] = Field(default=None)
# Near face
    near_face_calibration_pattern_size: Optional[List[int]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    near_face_calibration_pattern_type: Optional[str] = Field(default=None)
    near_face_calibration_spacing: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    near_face_calibration_spacing_unc: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    # near_face_calibratoin_photo_settings_id: Optional[int] = Field(default=None, foreign_key="settings.id") # Add back filling bit to setting
    # near_face_calibration_photo_camera_settings_link: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
    # near_face_calibration_photo: Optional[bytes] = Field(default=None, sa_column=Column(LargeBinary))
    near_face_calibration_photo_id: Optional[int] = Field(default=None, foreign_key="photo.id")
    near_face_homography_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType) # How do you show 2d shape? (3x3 array)
    near_face_homography_covariance_matrix: Optional[bytes] = Field(default=None, sa_column=PickleType) # How do you show 2d shape? (9x9 array)
    near_x_offset: Optional[float] = Field(default=None)
    near_x_offset_unc: Optional[float] = Field(default=None)
    near_y_offset: Optional[float] = Field(default=None)
    near_y_offset_unc: Optional[float] = Field(default=None)
    near_z_offset: Optional[float] = Field(default=None)
    near_z_offset_unc: Optional[float] = Field(default=None)
# Others
    scintillator_edges_photo_id: Optional[int] = Field(default=None, foreign_key="photo.id")
    horizontal_scintillator_limits: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer))) # How do you show 2d shape? (4x1 of 2x2 array)
    vertical_scintillator_limits: Optional[List[float]] = Field(default=None, sa_column=Column(ARRAY(Integer))) # How do you show 2d shape? (4x1 of 2x2 array)
    # e_log_entry: #How is this going to be stored, surely theres a better way than just a string?


# class Camera(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     username: str
#     hostname: str
#     password: str
#     model: str #e.g. AR, HQ, etc

#     test_beam_run_photos: list["TestBeamRunPhoto"] = Relationship(back_populates="camera")
#     real_beam_run_settings_and_cameras: list["RealBeamRunSettingsAndCamera"] = Relationship(back_populates="camera")
#     setup_links: list["CameraSetupLink"] = Relationship(back_populates="camera")


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
    # ESS_beam_energy_unc: float #????
    MSIC_beam_energy: Optional[float] = Field(default=None)
    MSIC_beam_energy_unc: Optional[float] = Field(default=None)
    beam_current: float
    beam_current_unc: float
    #Any other beam parameters?

    is_test: Optional[bool] = Field(default=None)

    experiment_id: int = Field(default=None, foreign_key="experiment.id")
    experiment: Experiment = Relationship(back_populates="beam_runs")

    # camera_settings_link_id: Optional[int] = Field(default=None, foreign_key="camerasettingslink.id")
    # camera_settings_link: Optional["CameraSettingsLink"] = Relationship(back_populates="beam_runs")
    camera_settings_links: List["CameraSettingsLink"] = Relationship(back_populates="beam_run")




#     beam_run_camera_settings: list["BeamRunCameraSettings"] = Relationship(back_populates="beam_run_number")

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
