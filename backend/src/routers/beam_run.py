from datetime import datetime
from fastapi import HTTPException, Response, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pytz
from sqlmodel import Session, select
from src.fitting_functions import plot_physical_units_ODR_bortfeld
from src.single_camera_analysis import get_beam_center_coords
from src.scintillation_light_pinpointing import compute_weighted_bragg_peak_depth, convert_beam_center_coords_to_penetration_depths, pinpoint_bragg_peak
from src.database.models import BeamRun, CameraSettingsLink, CameraSetupLink, Experiment, Photo, Settings, Setup
from src.database.database import engine
from sqlalchemy.exc import NoResultFound



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
    is_test=True
    beam_run = cdi.add_beam_run(experiment_id,
                                   beam_run_number,
                                   datetime_of_creation,
                                   ESS_beam_energy,
                                   beam_current,
                                   is_test)
    return beam_run

@router.post("/real/{experiment_id}")
def add_real_beam_run(experiment_id: int, beam_run_body: rb.CreateBeamRun):
    beam_run_number = beam_run_body.beam_run_number
    datetime_of_creation = datetime.now(pytz.utc)
    ESS_beam_energy = beam_run_body.ESS_beam_energy
    beam_current = beam_run_body.beam_current
    is_test=False
    beam_run = cdi.add_beam_run(experiment_id,
                                   beam_run_number,
                                   datetime_of_creation,
                                   ESS_beam_energy,
                                   beam_current,
                                   is_test)
    with Session(engine) as session:
        camera_setups_in_experiment_statement = select(CameraSetupLink).join(Setup).join(Experiment).where(Experiment.id == experiment_id)

        camera_setups_in_experiment = session.exec(camera_setups_in_experiment_statement).all()
        camera_ids_in_experiment = set()
        for camera_setup in camera_setups_in_experiment:
            camera_ids_in_experiment.add(camera_setup.camera_id)
        camera_ids_in_experiment = list(camera_ids_in_experiment)
        print(f"{ESS_beam_energy=}")
        print(f"{beam_current=}")
        print(f"{experiment_id=}")



        for camera_id in camera_ids_in_experiment:
            print(f"Camera id {camera_id}")
            optimal_settings_statement = (select(Settings)
                                         .join(CameraSettingsLink)
                                         .join(BeamRun)
                                         .join(Experiment)
                                         .where(BeamRun.ESS_beam_energy == ESS_beam_energy)
                                         .where(BeamRun.beam_current == beam_current)
                                         .where(BeamRun.is_test == True)
                                         .where(CameraSettingsLink.camera_id == camera_id)
                                         .where(CameraSettingsLink.is_optimal == True)
                                         .where(Experiment.id == experiment_id))

            try:
                optimal_settings = session.exec(optimal_settings_statement).one()
                cdi.add_camera_settings_link_with_beam_run(camera_id, optimal_settings.id, beam_run.id)
            except NoResultFound:
                print(f"No optimal settings found for camera {camera_id}")
        
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
        camera_settings_id = cdi.add_camera_settings_link_with_beam_run(camera_id,
                                                                                             settings_id,
                                                                                             beam_run_id)["id"]
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
                                         lens_position=settings.lens_position)

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
        camera_settings_id = cdi.add_camera_settings_link_with_beam_run(camera_id,
                                                                                             settings_id,
                                                                                             beam_run_id)["id"]
    return rb.CreateBeamRunSettingsRealResponse(id=camera_id)


# @router.post("/real/{beam_run_id}/number-of-images/camera/{camera_id}")
# def add_number_of_images_and_take_raw(beam_run_id: int, camera_id: int, real_settings_body: rb.UpdateNumberOfImagesAndRaw):
#     with Session(engine) as session:
#         camera_settings_statement = (select(CameraSettingsLink)
#                                      .where(CameraSettingsLink.camera_id == camera_id)
#                                      .where(CameraSettingsLink.beam_run_id == beam_run_id))
#         camera_settings = session.exec(camera_settings_statement).one()
#         camera_settings.number_of_images = real_settings_body.number_of_images
#         camera_settings.take_raw_images = real_settings_body.take_raw_images
#         session.commit()
#     return 
@router.get("/real/{beam_run_id}/number-of-images/camera/{camera_id}")
def get_real_settings_(beam_run_id: int, camera_id: int) -> rb.GetNumberOfImagesAndRaw:
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id)
                                     .where(CameraSettingsLink.camera_id == camera_id))
        camera_settings = session.exec(camera_settings_statement).one()
        return rb.GetNumberOfImagesAndRaw(id=camera_id,
                                          number_of_images=camera_settings.number_of_images,
                                          take_raw_images=camera_settings.take_raw_images)

@router.put("/real/{beam_run_id}/number-of-images/camera/{camera_id}")
def update_number_of_images_and_take_raw(beam_run_id: int, camera_id: int, real_settings_body: rb.UpdateNumberOfImagesAndRaw):
    with Session(engine) as session:
        camera_settings_statement = (select(CameraSettingsLink)
                                     .where(CameraSettingsLink.camera_id == camera_id)
                                     .where(CameraSettingsLink.beam_run_id == beam_run_id))
        camera_settings = session.exec(camera_settings_statement).one()
        camera_settings.number_of_images = real_settings_body.number_of_images
        camera_settings.take_raw_images = real_settings_body.take_raw_images
        session.commit()
    return rb.UpdateNumberOfImagesAndRawResponse(id=camera_id)






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
    

@router.get("/real/settings-completed/{beam_run_id}")
def get_test_beam_run_details(beam_run_id: int, response: Response):
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        all_camera_settings_set = session.exec(camera_settings_statement).all()
        cameras_set_ids = set()
        for camera_settings in all_camera_settings_set:
            number_of_images = camera_settings.number_of_images
            take_raw_images = camera_settings.take_raw_images
            if number_of_images is not None and take_raw_images is not None:
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

@router.get("/MSIC/{beam_run_id}")
def get_MSIC_data(beam_run_id: int):
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        return rb.GetMSICDataResponse(id=beam_run_id,
                                      MSIC_energy=beam_run.MSIC_beam_energy,
                                      MSIC_energy_uncertainty=beam_run.MSIC_beam_energy_unc,
                                      MSIC_current=beam_run.MSIC_beam_current,
                                      MSIC_current_uncertainty=beam_run.MSIC_beam_current_unc
                                      )

@router.put("/MSIC/{beam_run_id}")
def update_MSIC_data(beam_run_id: int, payload: rb.PostMSICDataPayload):
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)
        if payload.MSIC_energy is not None:
            beam_run.MSIC_beam_energy = payload.MSIC_energy
        if payload.MSIC_energy_uncertainty is not None:
            beam_run.MSIC_beam_energy_unc = payload.MSIC_energy_uncertainty
        if payload.MSIC_current is not None:
            beam_run.MSIC_beam_current = payload.MSIC_current
        if payload.MSIC_current_uncertainty is not None:
            beam_run.MSIC_beam_current_unc = payload.MSIC_current_uncertainty
        session.commit()
        return JSONResponse(content={"id": beam_run_id})


@router.get("/{position}/analysis-complete/{beam_run_id}")
def get_side_cameras_with_complete_analysis(beam_run_id: int, position: str, response: Response):
    camera_settings_with_complete_analyses = cdi.get_camera_settings_with_complete_analyses(beam_run_id)
    top_camera_settings_list, side_camera_settings_list = cdi.separate_camera_settings_by_position(camera_settings_with_complete_analyses)
    camera_settings_list = None
    if position == "side":
        camera_settings_list = side_camera_settings_list
    elif position == "top":
        camera_settings_list = top_camera_settings_list
    elif position == "both":
        camera_settings_list = side_camera_settings_list + top_camera_settings_list
    else:
        raise HTTPException(status_code=400, detail="Position must be 'top' or 'side'.")
    camera_list_response = []
    for camera_settings in camera_settings_list:
        camera_id = camera_settings.camera_id
        camera_username = cdi.get_camera_by_id(camera_id).username
        camera_response = rb.GetCompleteAnalysisCameraSettingsResponse(id=camera_settings.id,
                                                                       camera_id=camera_id,
                                                                       camera_username=camera_username)
        camera_list_response += [camera_response]
    response.headers["Content-Range"] = str(len(camera_list_response))
    return camera_list_response


@router.post("/bragg-peak/{beam_run_id}")
def update_bragg_peak_depth(beam_run_id: int):
    camera_settings_with_complete_analyses = cdi.get_camera_settings_with_complete_analyses(beam_run_id)
    top_camera_settings_list, side_camera_settings_list = cdi.separate_camera_settings_by_position(camera_settings_with_complete_analyses)
    if len(top_camera_settings_list) < 1 or len(side_camera_settings_list) < 1:
        raise HTTPException(status_code=503, detail=f"Not enough cameras. Only analyses for {len(top_camera_settings_list)} top cameras and {len(side_camera_settings_list)} side cameras.")
    
    side_camera_analysis_ids = cdi.get_camera_analysis_ids_by_camera_settings_list(side_camera_settings_list)
    top_camera_analysis_ids = cdi.get_camera_analysis_ids_by_camera_settings_list(top_camera_settings_list)
    print(f"\n\n\n SIDE CAMERA ANALYSIS IDS: {side_camera_analysis_ids}\n")
    print(f"\n TOP CAMERA ANALYSIS IDS: {top_camera_analysis_ids}\n")
    pinpoint_results = pinpoint_bragg_peak(side_camera_analysis_ids + top_camera_analysis_ids)
    bragg_peak_depth, unc_bragg_peak_depth = compute_weighted_bragg_peak_depth(beam_run_id, side_camera_analysis_ids, top_camera_analysis_ids)
    cdi.update_bragg_peak_depth(beam_run_id, float(bragg_peak_depth))
    cdi.update_unc_bragg_peak_depth(beam_run_id, float(unc_bragg_peak_depth))
    return JSONResponse(content={"id": beam_run_id})

@router.get("/bragg-peak/{beam_run_id}")
def get_bragg_peak(beam_run_id: int):
    with Session(engine) as session:
        beam_run = session.get(BeamRun, beam_run_id)

        bragg_peak_x = None
        bragg_peak_y = None
        bragg_peak_z = None
        bragg_peak_x_unc = None
        bragg_peak_y_unc = None
        bragg_peak_z_unc = None

        bragg_peak_3d_position = beam_run.bragg_peak_3d_position
        if bragg_peak_3d_position is not None:
            bragg_peak_x, bragg_peak_y, bragg_peak_z = bragg_peak_3d_position


        unc_bragg_peak_3d_position = beam_run.unc_bragg_peak_3d_position
        if unc_bragg_peak_3d_position is not None:
            bragg_peak_x_unc, bragg_peak_y_unc, bragg_peak_z_unc = unc_bragg_peak_3d_position

        return rb.GetBraggPeakResponse(id=beam_run_id,
                                       bragg_peak_x=bragg_peak_x,
                                       bragg_peak_y=bragg_peak_y,
                                       bragg_peak_z=bragg_peak_z,
                                       bragg_peak_x_unc=bragg_peak_x_unc,
                                       bragg_peak_y_unc=bragg_peak_y_unc,
                                       bragg_peak_z_unc=bragg_peak_z_unc,
                                       bragg_peak_depth=beam_run.bragg_peak_depth,
                                       bragg_peak_depth_unc=beam_run.unc_bragg_peak_depth)


# @router.post("/range/{beam_run_id}")
# def do_range_analysis(beam_run_id: int):
#     side_cam_beam_center_coords, unc_side_cam_beam_center_coords, \
#     total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi = get_beam_center_coords(beam_run_id, side_camera_analysis_id)
    
#     distances_travelled_inside_scintillator, \
#     unc_distances_travelled_inside_scintillator = convert_beam_center_coords_to_penetration_depths(side_camera_analysis_id,
#                                                                                                 side_cam_beam_center_coords,
#                                                                                                 unc_side_cam_beam_center_coords,
#                                                                                                 [beam_center_incident_position, beam_direction_vector],
#                                                                                                 [unc_beam_center_incident_position, unc_beam_direction_vector])
    
#     plot_physical_units_ODR_bortfeld(side_camera_analysis_id, distances_travelled_inside_scintillator, unc_distances_travelled_inside_scintillator, 
#                                     total_brightness_along_vertical_roi, unc_total_brightness_along_vertical_roi)
        