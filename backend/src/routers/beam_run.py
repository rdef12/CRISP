from datetime import datetime
from fastapi import Response, APIRouter
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.models import BeamRun, CameraSettingsLink, CameraSetupLink, Experiment, Settings
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

@router.post("/test/{beam_run_id}/camera/{camera_id}")
def add_test_settings(beam_run_id: int, camera_id: int, test_settings_body: rb.CreateBeamRunSettingsTest):
    gain_range = np.arange(test_settings_body.lowest_gain,
                           test_settings_body.highest_gain + test_settings_body.gain_increment, #So that highest gain is included
                           test_settings_body.gain_increment)
    preset_lens_position = None
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        experiment_id = beam_run.experiment_id
        setup_id = session.get(Experiment, experiment_id).setup_id
        setup_camera_statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        setup_camera = session.exec(setup_camera_statement).one()
        preset_lens_position = setup_camera.lens_position

        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        all_camera_settings = session.exec(camera_settings_statement).all()
        if len(all_camera_settings) > 0:
            for camera_settings in all_camera_settings:
                print(f"\n\n EXTERMINTAAAAAAAAAAAATE - {camera_settings} \n\n")
                session.delete(camera_settings)
            session.commit()


    for gain in gain_range:
        settings_id = cdi.add_settings(test_settings_body.frame_rate, preset_lens_position, float(gain))["id"]
        camera_settings_id = cdi.add_camera_settings_link_with_beam_run(camera_id, settings_id, beam_run_id)["id"]
    return rb.CreateBeamRunSettingsTestResponse(id=camera_id, time_to_take_photos=9) #TODO #TODO set the time to take photos properly


@router.get("/test/{beam_run_id}/camera/{camera_id}")
def get_test_settings_inputs(beam_run_id: int, camera_id: int) -> rb.GetBeamRunSettingsTest:
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        all_camera_settings = session.exec(camera_settings_statement).all()
        gains = np.zeros(len(all_camera_settings))
        frame_rates = np.zeros(len(all_camera_settings))
        for count, camera_settings in enumerate(all_camera_settings):
            settings_id = camera_settings.settings_id
            settings = session.get(Settings, settings_id)
            gains[count] = settings.gain
            frame_rates[count] = settings.frame_rate
        minimum_gain = np.min(gains)
        maximum_gain = np.max(gains)
        frame_rate = frame_rates[0] #TODO could add a check that all framerates are the same and clean up invalid entries?
        gain_increment = gains[1] - gains[0] #TODO could do similar here
        return rb.GetBeamRunSettingsTest(id=camera_id,
                                         frame_rate=frame_rate,
                                         lowest_gain=minimum_gain,
                                         highest_gain=maximum_gain,
                                         gain_increment=gain_increment)
    
@router.put("/test/{beam_run_id}/camera/{camera_id}")
def update_test_settings(beam_run_id: int, camera_id: int, test_settings_body: rb.CreateBeamRunSettingsTest):   
    gain_range = np.arange(test_settings_body.lowest_gain,
                           test_settings_body.highest_gain + test_settings_body.gain_increment, #So that highest gain is included
                           test_settings_body.gain_increment)
    preset_lens_position = None

    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        experiment_id = beam_run.experiment_id
        setup_id = session.get(Experiment, experiment_id).setup_id
        setup_camera_statement = select(CameraSetupLink).where(CameraSetupLink.camera_id == camera_id).where(CameraSetupLink.setup_id == setup_id)
        setup_camera = session.exec(setup_camera_statement).one()
        preset_lens_position = setup_camera.lens_position

        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        all_camera_settings = session.exec(camera_settings_statement).all()
        if len(all_camera_settings) > 0:
            for camera_settings in all_camera_settings:
                session.delete(camera_settings)
            session.commit()

    for gain in gain_range:
        settings_id = cdi.add_settings(test_settings_body.frame_rate, preset_lens_position, float(gain))["id"]
        camera_settings_id = cdi.add_camera_settings_link_with_beam_run(camera_id, settings_id, beam_run_id)["id"]
    return rb.CreateBeamRunSettingsTestResponse(id=camera_id, time_to_take_photos=9)