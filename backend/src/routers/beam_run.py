from datetime import datetime
from fastapi import Response, APIRouter
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.models import BeamRun, Experiment
from src.database.database import engine


from src.network_functions import *
from src.camera_functions import *
from src.connection_functions import *
from src.classes.JSON_request_bodies import request_bodies as rb

from src.database.CRUD import CRISP_database_interaction as cdi

router = APIRouter(
    prefix="/beam-run",
    tags=["beam-run"],
)


@router.get("/{experiment_id}")
def get_beam_runs(experiment_id: int, response: Response) -> list[BeamRun]:
    with Session(engine) as session:
        statement = select(BeamRun).where(BeamRun.experiment_id == experiment_id)
        results = session.exec(statement).all()
        results = results if results else []
        response.headers["Content-Range"] = str(len(results))
        return results
    
@router.post("/real/{experiment_id}")
def add_beam_run(experiment_id: int, beam_run_body: rb.CreateBeamRun):
    beam_run_number = beam_run_body.beam_run_number
    datetime_of_creation = datetime.now(pytz.utc)
    ESS_beam_energy = beam_run_body.ESS_beam_energy
    beam_current = beam_run_body.beam_current
    beam_current_unc = beam_run_body.beam_current_unc
    is_test=False
    beam_run = cdi.add_beam_run(experiment_id,
                                   beam_run_number,
                                   datetime_of_creation,
                                   ESS_beam_energy,
                                   beam_current,
                                   beam_current_unc,
                                   is_test)
    return beam_run

@router.post("/test/{experiment_id}")
def add_beam_run(experiment_id: int, beam_run_body: rb.CreateBeamRun):
    beam_run_number = beam_run_body.beam_run_number
    datetime_of_creation = datetime.now(pytz.utc)
    ESS_beam_energy = beam_run_body.ESS_beam_energy
    beam_current = beam_run_body.beam_current
    beam_current_unc = beam_run_body.beam_current_unc
    is_test=True
    beam_run = cdi.add_beam_run(experiment_id,
                                   beam_run_number,
                                   datetime_of_creation,
                                   ESS_beam_energy,
                                   beam_current,
                                   beam_current_unc,
                                   is_test)
    return beam_run


    