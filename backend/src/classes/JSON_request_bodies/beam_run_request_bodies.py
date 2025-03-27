from pydantic import BaseModel

class CreateBeamRun(BaseModel):
    beam_run_number: int
    ESS_beam_energy: float
    beam_current: float
    beam_current_unc: float

class CreateBeamRunSettingsTest(BaseModel):
    frame_rate: int
    lowest_gain: float
    highest_gain: float
    gain_increment: float

class GetBeamRunSettingsTest(BaseModel):
    id: int # camera_id
    frame_rate: int
    lowest_gain: float
    highest_gain: float
    gain_increment: float

class CreateBeamRunSettingsTestResponse(BaseModel):
    id: int #camera_id
    time_to_take_photos: int #seconds