from typing import Optional
from pydantic import BaseModel

from src.database.models import Camera, CameraSettingsLink, Photo, Settings

class CreateBeamRun(BaseModel):
    beam_run_number: int
    ESS_beam_energy: float
    beam_current: float

class BeamRunCameraSettingsLink(BaseModel):
    id: int
    camera_id: int
    settings_is: int
    is_optimal: int
    camera: Camera
    settings: Settings
    photos: list[Photo] #TODO Will this have to be optional?


class GetBeamRun(BaseModel):
    id: int
    beam_run_number: int
    ESS_beam_energy: float
    beam_current: float
    camera_settings: list[BeamRunCameraSettingsLink]


class GetTestBeamRunSettingsCompleted(BaseModel):
    id: int
    unset_camera_ids: list[int]


class GetTestBeamRunDataTaken(BaseModel):
    id: int
    data_taken: bool


class CreateBeamRunSettingsTest(BaseModel):
    frame_rate: int
    lowest_gain: float
    highest_gain: float
    gain_increment: float

class CreateBeamRunSettingsReal(BaseModel):
    frame_rate: int
    gain: float



class UpdateNumberOfImagesAndRaw(BaseModel):
    number_of_images: int
    take_raw_images: bool

class UpdateNumberOfImagesAndRawResponse(BaseModel):
    id: int

class GetNumberOfImagesAndRaw(BaseModel):
    id: int
    number_of_images: Optional[int]
    take_raw_images: Optional[bool]

class GetBeamRunSettingsTest(BaseModel):
    id: int # camera_id
    frame_rate: int
    lowest_gain: float
    highest_gain: float
    gain_increment: float

class GetBeamRunSettingsReal(BaseModel):
    id: int # camera_id
    frame_rate: int
    gain: float
    lens_position: float



class CreateBeamRunSettingsTestResponse(BaseModel):
    id: int #camera_id
    time_to_take_photos: int #seconds

class CreateBeamRunSettingsRealResponse(BaseModel):
    id: int #camera_id

class PostMSICDataPayload(BaseModel):
    MSIC_energy: Optional[float] = None
    MSIC_energy_uncertainty: Optional[float] = None
    MSIC_current: Optional[float] = None
    MSIC_current_uncertainty: Optional[float] = None

class GetMSICDataResponse(BaseModel):
    id: int
    MSIC_energy: Optional[float] = None
    MSIC_energy_uncertainty: Optional[float] = None
    MSIC_current: Optional[float] = None
    MSIC_current_uncertainty: Optional[float] = None


class GetCompleteAnalysisCameraSettingsResponse(BaseModel):
    id: int
    camera_id: int
    camera_username: str    


class GetBraggPeakResponse(BaseModel):
    id: int

    bragg_peak_x: Optional[float] = None
    bragg_peak_y: Optional[float] = None
    bragg_peak_z: Optional[float] = None
    bragg_peak_x_unc: Optional[float] = None
    bragg_peak_y_unc: Optional[float] = None
    bragg_peak_z_unc: Optional[float] = None
    bragg_peak_depth: Optional[float] = None
    bragg_peak_depth_unc: Optional[float] = None
