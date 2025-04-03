from pydantic import BaseModel

from src.database.models import Camera, CameraSettingsLink, Photo, Settings

class CreateBeamRun(BaseModel):
    beam_run_number: int
    ESS_beam_energy: float
    beam_current: float
    beam_current_unc: float

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
    beam_current_unc: float
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
    number_of_images: int

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
    number_of_images: int


class CreateBeamRunSettingsTestResponse(BaseModel):
    id: int #camera_id
    time_to_take_photos: int #seconds

class CreateBeamRunSettingsRealResponse(BaseModel):
    id: int #camera_id