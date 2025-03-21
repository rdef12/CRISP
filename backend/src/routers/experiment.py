from datetime import datetime
from fastapi import Response, APIRouter
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.models import Camera, Experiment
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

@router.get("/{experiment_id}")
async def get_experiment(experiment_id: int, response: Response) -> rb.ExperimentalSetupRequest:
    experiment = cdi.get_experiment_by_id(experiment_id)
    setup = cdi.get_setup_by_experiment_id(experiment_id) #TODO add cameras in the setup to this body in future
    cameras = cdi.get_cameras_in_setup(setup.id)
    response.headers["Content-Range"] = str(len(cameras))
    experiment_body = rb.ExperimentalSetupRequest(id=experiment.id,
                                                  name=experiment.name,
                                                  date_started=experiment.date_started,
                                                  setup_id=experiment.setup_id,
                                                  setup=setup,
                                                  cameras=cameras)
    return experiment_body

@router.get("/cameras/{experiment_id}")
async def get_cameras(experiment_id: int, response: Response) -> list[Camera]:
    cameras = cdi.get_cameras_in_experiment(experiment_id)
    response.headers["Content-Range"] = str(len(cameras))
    return cameras





# @router.get("/scintillator-edges/{setup_camera_id}")
# async def read_setup_camera(setup_camera_id: int) -> rb.SetupCameraScintillatorEdgeRequest:
#     setup_camera = cdi.get_setup_camera_by_id(setup_camera_id)
#     settings = cdi.get_settings_by_setup_camera_id_scintillator_edges(setup_camera_id)
#     print(f"\n\n Settings: {settings} \n\n")

#     setup_camera_body = rb.SetupCameraScintillatorEdgeRequest(id=setup_camera.id,
#                                                               camera_id=setup_camera.id,
#                                                               setup_id=setup_camera.setup_id,
#                                                               scintillator_edges_photo_camera_settings_id=setup_camera.scintillator_edges_photo_camera_settings_id,
#                                                               settings=settings,
#                                                               horizontal_start=setup_camera.horizontal_scintillator_start,
#                                                               horizontal_end=setup_camera.horizontal_scintillator_end,
#                                                               vertical_start=setup_camera.vertical_scintillator_start,
#                                                               vertical_end=setup_camera.vertical_scintillator_end)
#     return setup_camera_body