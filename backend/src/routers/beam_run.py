from datetime import datetime
from fastapi import Response, APIRouter
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.database.models import BeamRun, CameraSettingsLink, CameraSetupLink, Experiment, Photo, Settings, Setup
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
    
# @router.post("/real/{experiment_id}")
# def add_real_beam_run(experiment_id: int, beam_run_body: rb.CreateBeamRun):
#     beam_run_number = beam_run_body.beam_run_number
#     datetime_of_creation = datetime.now(pytz.utc)
#     ESS_beam_energy = beam_run_body.ESS_beam_energy
#     beam_current = beam_run_body.beam_current
#     beam_current_unc = beam_run_body.beam_current_unc
#     is_test=False
#     beam_run = cdi.add_beam_run(experiment_id,
#                                    beam_run_number,
#                                    datetime_of_creation,
#                                    ESS_beam_energy,
#                                    beam_current,
#                                    beam_current_unc,
#                                    is_test)
#     return beam_run

@router.post("/test/{experiment_id}")
def add_real_beam_run(experiment_id: int, beam_run_body: rb.CreateBeamRun):
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

@router.post("/real/{experiment_id}")
def add_real_beam_run(experiment_id: int, beam_run_body: rb.CreateBeamRun):
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
    DEFAULT_NUMBER_OF_IMAGES = 60
    with Session(engine) as session:
        cameras_in_experiment_statement = select(CameraSetupLink).join(Setup).join(Experiment).where(Experiment.id == experiment_id)

        cameras_in_experiment = session.exec(cameras_in_experiment_statement).all()
        for camera in cameras_in_experiment:
            optimal_settings_statment = (select(Settings)
                                         .join(CameraSettingsLink)
                                         .join(BeamRun)
                                         .where(BeamRun.ESS_beam_energy == ESS_beam_energy)
                                         .where(BeamRun.beam_current == beam_current)
                                         .where(BeamRun.is_test == True)
                                         .where(CameraSettingsLink.camera_id == camera.id)
                                         .where(CameraSettingsLink.is_optimal == True))
            try:
                optimal_settings = session.exec(optimal_settings_statment).one()
                cdi.add_camera_settings_link_with_beam_run_and_number_of_images(camera.id,
                                                                                optimal_settings.id,
                                                                                beam_run.id,
                                                                                DEFAULT_NUMBER_OF_IMAGES)
            except:
                pass
        
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
                session.delete(camera_settings)
            session.commit()


    for gain in gain_range:
        settings_id = cdi.add_settings(test_settings_body.frame_rate, preset_lens_position, float(gain))["id"]
        camera_settings_id = cdi.add_camera_settings_link_with_beam_run(camera_id, settings_id, beam_run_id)["id"]
    return rb.CreateBeamRunSettingsTestResponse(id=camera_id, time_to_take_photos=9) #TODO #TODO set the time to take photos properly


@router.post("/real/{beam_run_id}/camera/{camera_id}")
def add_real_settings(beam_run_id: int, camera_id: int, real_settings_body: rb.CreateBeamRunSettingsReal):

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

        settings_id = cdi.add_settings(real_settings_body.frame_rate, preset_lens_position, real_settings_body.gain)["id"]
        camera_settings_id = cdi.add_camera_settings_link_with_beam_run_and_number_of_images(camera_id,
                                                                                             settings_id,
                                                                                             beam_run_id,
                                                                                             real_settings_body.number_of_images)["id"]
    return rb.CreateBeamRunSettingsRealResponse(id=camera_id) #TODO #TODO set the time to take photos properly


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
    
@router.get("/real/{beam_run_id}/camera/{camera_id}")
def get_real_settings_(beam_run_id: int, camera_id: int) -> rb.GetBeamRunSettingsReal:
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        camera_settings = session.exec(camera_settings_statement).one()
        settings = session.get(Settings, camera_settings.settings_id)
        return rb.GetBeamRunSettingsReal(id=camera_id,
                                         frame_rate=settings.frame_rate,
                                         gain=settings.gain,
                                         lens_position=settings.lens_position,
                                         number_of_images=camera_settings.number_of_images)

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
    return rb.CreateBeamRunSettingsTestResponse(id=camera_id, time_to_take_photos=9) #TODO time to take photos no longer needed, dealt with in frontend


@router.put("/real/{beam_run_id}/camera/{camera_id}")
def update_real_settings(beam_run_id: int, camera_id: int, real_settings_body: rb.CreateBeamRunSettingsReal):   
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

        settings_id = cdi.add_settings(real_settings_body.frame_rate, preset_lens_position, real_settings_body.gain)["id"]
        camera_settings_id = cdi.add_camera_settings_link_with_beam_run_and_number_of_images(camera_id,
                                                                                             settings_id,
                                                                                             beam_run_id,
                                                                                             real_settings_body.number_of_images)["id"]
    return rb.CreateBeamRunSettingsRealResponse(id=camera_id)





@router.get("/test/settings-completed/{beam_run_id}")
def get_test_beam_run_details(beam_run_id: int, response: Response):
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        all_camera_settings_set = session.exec(camera_settings_statement).all()
        cameras_set_ids = set()
        for camera_settings in all_camera_settings_set:
            cameras_set_ids.add(camera_settings.camera_id)

        experiment_id = beam_run.experiment_id
        experiment = session.get(Experiment, experiment_id)
        setup_id = experiment.setup_id
        setup_camera_statement = select(CameraSetupLink).where(CameraSetupLink.setup_id == setup_id)
        all_setup_camera_links = session.exec(setup_camera_statement).all()
        all_cameras_in_setup_ids = set()
        for setup_camera_link in all_setup_camera_links:
            all_cameras_in_setup_ids.add(setup_camera_link.camera_id)
        
        unset_cameras_ids = all_cameras_in_setup_ids.difference(cameras_set_ids)
        unset_cameras_ids = list(unset_cameras_ids)
        response.headers["Content-Range"] = str(len(unset_cameras_ids))

        return rb.GetTestBeamRunSettingsCompleted(id=beam_run_id,
                                                  unset_camera_ids=unset_cameras_ids)
    

@router.get("/settings-completed/{beam_run_id}")
def get_test_beam_run_details(beam_run_id: int, response: Response):
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        all_camera_settings_set = session.exec(camera_settings_statement).all()
        cameras_set_ids = set()
        for camera_settings in all_camera_settings_set:
            cameras_set_ids.add(camera_settings.camera_id)

        experiment_id = beam_run.experiment_id
        experiment = session.get(Experiment, experiment_id)
        setup_id = experiment.setup_id
        setup_camera_statement = select(CameraSetupLink).where(CameraSetupLink.setup_id == setup_id)
        all_setup_camera_links = session.exec(setup_camera_statement).all()
        all_cameras_in_setup_ids = set()
        for setup_camera_link in all_setup_camera_links:
            all_cameras_in_setup_ids.add(setup_camera_link.camera_id)
        
        unset_cameras_ids = all_cameras_in_setup_ids.difference(cameras_set_ids)
        unset_cameras_ids = list(unset_cameras_ids)
        response.headers["Content-Range"] = str(len(unset_cameras_ids))

        return rb.GetTestBeamRunSettingsCompleted(id=beam_run_id,
                                                  unset_camera_ids=unset_cameras_ids)


# @router.post("/test/take-data/{beam_run_id}")
# def take_test_beam_run_images(beam_run_id: int):
#     with Session(engine) as session:    
#         beam_run = session.get(BeamRun, beam_run_id)
#         camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
#         all_camera_settings = session.exec(camera_settings_statement).all()
#         for camera_settings


@router.get("/data-taken/{beam_run_id}")
def get_is_data_taken(beam_run_id: int) -> rb.GetTestBeamRunDataTaken:
    with Session(engine) as session:
        test_photos_statement = select(Photo).join(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        test_photos = session.exec(test_photos_statement).all()
        if len(test_photos) > 0:
            return rb.GetTestBeamRunDataTaken(id=beam_run_id, data_taken=True)
        return rb.GetTestBeamRunDataTaken(id=beam_run_id, data_taken=False)



# @router.get("/test/data-taken/{beam_run_id}")
# def get_is_data_taken(beam_run_id: int) -> rb.GetTestBeamRunDataTaken:
#     with Session(engine) as session:
#         test_photos_statement = select(Photo).join(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
#         test_photos = session.exec(test_photos_statement).all()
#         if len(test_photos) > 0:
#             return rb.GetTestBeamRunDataTaken(id=beam_run_id, data_taken=True)
#         return rb.GetTestBeamRunDataTaken(id=beam_run_id, data_taken=False)
