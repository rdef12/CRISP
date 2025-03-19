from pydantic import BaseModel

class ExperimentCreateRequest(BaseModel):
    experiment_name: str
    setup_id: int