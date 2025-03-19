from pydantic import BaseModel

class CreateBeamRun(BaseModel):
    beam_run_number: int
    ESS_beam_energy: float
    beam_current: float
    beam_current_unc: float