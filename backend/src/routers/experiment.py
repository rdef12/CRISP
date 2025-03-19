from datetime import datetime
from fastapi import Response, APIRouter
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.models import Experiment
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb

from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/experiment",
    tags=["experiment"],
)

@router.get("")
def get_experiments_api(response: Response) -> list[Experiment]:
    experiments = cdi.get_all_experiments()
    response.headers["Content-Range"] = str(len(experiments))
    return experiments

@router.post("")
async def create_experiment(experiment_body: rb.ExperimentCreateRequest):
    datetime_of_creation = datetime.now(pytz.utc)
    experiment_name = experiment_body.experiment_name
    setup_id = experiment_body.setup_id
    experiment_id = cdi.add_experiment(experiment_name,
                                       datetime_of_creation,
                                       setup_id)["id"]
    return {"message": f"Experiment with name {experiment_name} successfully added.",
            "id": experiment_id}