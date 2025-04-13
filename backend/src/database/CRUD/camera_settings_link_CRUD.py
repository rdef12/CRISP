from src.database.database import engine
from sqlmodel import Session, select
from sqlalchemy.orm.exc import NoResultFound
from src.database.models import CameraAnalysis, CameraSettingsLink, BeamRun, CameraSetupLink, OpticalAxisEnum, Photo, Experiment


# Create

def add_camera_settings_link(camera_id: int, settings_id: int): # Need to enforce this as impossible for beam runs or maybe enforce this as first step then have to add beam run link
    try:
        camera_setup_link = CameraSettingsLink(camera_id=camera_id, settings_id=settings_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(camera_setup_link)
        session.commit()
        return {"message": f"Camera added to setup.",
                "id": camera_setup_link.id}

def add_camera_settings_link_with_beam_run(camera_id: int, settings_id: int, beam_run_id: int):
    try:
        camera_setup_link = CameraSettingsLink(camera_id=camera_id, settings_id=settings_id, beam_run_id=beam_run_id)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(camera_setup_link)
        session.commit()
        return {"message": f"Camera added to setup.",
                "id": camera_setup_link.id}

# def add_camera_settings_link_with_beam_run_and_number_of_images(camera_id: int, settings_id: int, beam_run_id: int, number_of_images: int, take_raw_images: bool):
#     try:
#         camera_setup_link = CameraSettingsLink(camera_id=camera_id, settings_id=settings_id, beam_run_id=beam_run_id, number_of_images=number_of_images, take_raw_images=take_raw_images)
#     except TypeError as e:
#         raise TypeError(f"TypeError: {e}") from e
#     except ValueError as e:
#         raise ValueError(f"ValueError: {e}") from e
#     with Session(engine) as session:
#         session.add(camera_setup_link)
#         session.commit()
#         return {"message": f"Camera added to setup.",
#                 "id": camera_setup_link.id}


# Read

def get_camera_settings_link_id(camera_id: int, settings_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).where(CameraSettingsLink.camera_id == camera_id).where(CameraSettingsLink.settings_id == settings_id)
        result = session.exec(statement).one()
        if result:
            return result.id
        else:
            raise ValueError(f"Camera settings link with camera_id: {camera_id} and settings_id {settings_id} cannot be a found.")
        

def get_camera_and_settings_ids(camera_settings_link_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).where(CameraSettingsLink.id == camera_settings_link_id)
        result = session.exec(statement).one()
        if result:
            return {"camera_id": result.camera_id, "settings_id": result.settings_id}
        else:
            raise ValueError(f"Camera settings link with id: {camera_settings_link_id} cannot be a found.")


def get_cameras_and_settings_from_beam_run_id(beam_run_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        result = session.exec(statement).all()
        if result:
            return [{"camera_id": r.camera_id, "settings_id": r.settings_id} for r in result]
        else:
            raise ValueError(f"Camera settings link with beam_run_id: {beam_run_id} cannot be a found.")


# def get_optimal_settings_id_for_camera(camera_id: int, ESS_beam_energy: float, beam_current: float):
#     with Session(engine) as session:
#         statement = (select(CameraSettingsLink)
#                      .where(CameraSettingsLink.camera_id == camera_id)
#                      .where(BeamRun.ESS_beam_energy == ESS_beam_energy)
#                      .where(BeamRun.beam_current == beam_current)
#                      .where(CameraSettingsLink.is_optimal == True)
#                      .where(BeamRun.is_test == True))
#         result = session.exec(statement).one()
#         if result:
#             return {"camera_id": result.camera_id, "settings_id": result.settings_id}
#         else:
#             raise ValueError(f"Optimal settings for camera_id: {camera_id} with ESS_beam_energy: {ESS_beam_energy} and beam_current: {beam_current} cannot be a found.")

def get_camera_settings_by_id(camera_settings_link_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).where(CameraSettingsLink.id == camera_settings_link_id)
        result = session.exec(statement).one()
        return result

def get_camera_settings_by_photo_id(photo_id: int):
    with Session(engine) as session:
        statement = select(CameraSettingsLink).join(Photo).where(Photo.id == photo_id)
        camera_settings = session.exec(statement).one()
        return camera_settings

def get_settings_id_by_camera_settings_id(camera_settings_id: int):
    with Session(engine) as session:
        camera_settings = session.get(CameraSettingsLink, camera_settings_id)
        settings_id = camera_settings.settings_id
        return settings_id
    
def get_beam_run_id_by_camera_settings_link_id(camera_settings_link_id: int):
    with Session(engine) as session:
        camera_settings = session.get(CameraSettingsLink, camera_settings_link_id)
        beam_run_id = camera_settings.beam_run_id
        return beam_run_id
    
def get_take_raw_images(camera_settings_link_id: int):
    with Session(engine) as session:
        camera_settings = session.get(CameraSettingsLink, camera_settings_link_id)
        take_raw_images = camera_settings.take_raw_images
        return take_raw_images
    
def get_number_of_images_to_capture_by_camera_settings_link_id(camera_settings_link_id: int):
    with Session(engine) as session:
        camera_settings = session.get(CameraSettingsLink, camera_settings_link_id)
        number_of_images = camera_settings.number_of_images
        return number_of_images
    
def get_successfully_captured_photo_ids_by_camera_settings_link_id(camera_settings_link_id: int):
    with Session(engine) as session:
        # Bytes must be present to be included
        statement = select(Photo.id).where(Photo.camera_settings_link_id == camera_settings_link_id).where(Photo.photo.isnot(None))
        photo_id_list = session.exec(statement).all()
        return photo_id_list
    
def get_num_of_successfully_captured_images_by_camera_settings_link_id(camera_settings_link_id: int):
    """
    Query photos table for all entries with camera_settings_link_id and return the number with Photo not None
    
    To get the number of images successfully taken, look for how many photos 
    (photo_bytes must not be None) in Photo table with the camera_setttings_link_id
    If simply using BeamRun's num_of_images_to_capture, cannot guarantee all taken/transferred to db
    successfully
    """
    with Session(engine) as session:
        # Bytes must be present to be included
        statement = select(Photo).where(Photo.camera_settings_link_id == camera_settings_link_id).where(Photo.photo.isnot(None))
        result = session.exec(statement).all()
        return len(result)

def get_camera_settings_with_complete_analyses(beam_run_id: int):
    with Session(engine) as session:
        all_camera_settings_statement = select(CameraSettingsLink).where(CameraSettingsLink.beam_run_id == beam_run_id)
        all_camera_settings = session.exec(all_camera_settings_statement)
        completed_camera_settings = []
        for camera_settings in all_camera_settings:
            camera_analysis_statement = select(CameraAnalysis).where(CameraAnalysis.camera_settings_id == camera_settings.id)
            try:
                camera_analysis = session.exec(camera_analysis_statement).one()
            except NoResultFound:
                continue
            analysis_is_complete = (camera_analysis.beam_angle is not None
                                    and camera_analysis.unc_beam_angle is not None
                                    and camera_analysis.bragg_peak_pixel is not None
                                    and camera_analysis.unc_bragg_peak_pixel is not None)
            if analysis_is_complete:
                completed_camera_settings += [camera_settings]
        return completed_camera_settings

def separate_camera_settings_by_position(camera_settings_list: list[CameraSettingsLink]) -> tuple[list[CameraSettingsLink]]:
    with Session(engine) as session:
        side_cameras = []
        top_cameras = []
        for camera_settings in camera_settings_list:
            beam_run = session.get(BeamRun, camera_settings.beam_run_id)
            experiment = session.get(Experiment, beam_run.experiment_id)
            setup_id = experiment.setup_id
            camera_id = camera_settings.camera_id
            setup_camera_statement = (select(CameraSetupLink)
                                      .where(CameraSetupLink.camera_id == camera_id)
                                      .where(CameraSetupLink.setup_id == setup_id))
            setup_camera = session.exec(setup_camera_statement).one()
            optical_axis = setup_camera.optical_axis
            print(f"\n\n Optical axis: {optical_axis} \n\n optical axis type: {type(optical_axis)} \n\n OPticalenum.x type {type(OpticalAxisEnum.x)}\n\n")
            if optical_axis == OpticalAxisEnum.x:
                side_cameras += [camera_settings]
            elif optical_axis == OpticalAxisEnum.y:
                top_cameras += [camera_settings]
            else:
                pass
        return top_cameras, side_cameras

# Update

# def flag_optimal_settings(beam_run_id: int, camera_id: int, settings_id: int):
#     try:
#         with Session(engine) as session:
#             statement = (select(CameraSettingsLink)
#                          .where(BeamRun.id == beam_run_id)
#                          .where(CameraSettingsLink.camera_id == camera_id)
#                          .where(CameraSettingsLink.settings_id == settings_id))
#             result = session.exec(statement).one()
#             result.is_optimal = True
#             session.commit()
#             return {"message": f"Camera settings link with beam_run_id: {beam_run_id}, camera_id: {camera_id} and settings_id: {settings_id} - set to optimal"}
#     except NoResultFound:
#         raise ValueError(f"No camera settings link found for beam_run_id={beam_run_id} and camera_id={camera_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")


# def update_is_optimal(beam_run_id: int, camera_id: int, settings_id: int, is_optimal: bool):
#     try:
#         with Session(engine) as session:
#             statement = select(CameraSettingsLink).join(BeamRun).where(BeamRun.id == beam_run_id).where(CameraSettingsLink.camera_id == camera_id).where(CameraSettingsLink.settings_id == settings_id)
#             result = session.exec(statement).one()
#             result.is_optimal = is_optimal
#             session.commit()
#             return {"message": f"Camera settings link with beam_run_id: {beam_run_id} and camera_id: {camera_id} updated with settings_id: {settings_id}"}
#     except NoResultFound:
#         raise ValueError(f"No camera settings link found for beam_run_id={beam_run_id} and camera_id={camera_id}.")
#     except Exception as e:
#         raise RuntimeError(f"An error occurred: {str(e)}")

def update_is_optimal(photo_id: int):
    try:
        with Session(engine) as session:
            optimal_camera_settings_statement = (select(CameraSettingsLink)
                                                 .join(Photo)
                                                 .where(Photo.id == photo_id))
            optimal_camera_settings = session.exec(optimal_camera_settings_statement).one()

            beam_run_statement = (select(BeamRun)
                                         .join(CameraSettingsLink)
                                         .where(CameraSettingsLink.id == optimal_camera_settings.id))
            beam_run = session.exec(beam_run_statement).one()

            all_related_camera_settings_statement = (select(CameraSettingsLink)
                                                     .join(BeamRun)
                                                     .join(Experiment)
                                                     .where(BeamRun.ESS_beam_energy == beam_run.ESS_beam_energy)
                                                     .where(BeamRun.beam_current == beam_run.beam_current)
                                                     .where(Experiment.id == beam_run.experiment_id))
            all_related_camera_settings = session.exec(all_related_camera_settings_statement).all()
            for camera_settings in all_related_camera_settings:
                camera_settings.is_optimal = False
            optimal_camera_settings.is_optimal = True
            session.commit()
            return {"message": f"Camera settings {optimal_camera_settings.id} set to optimal"}
    except NoResultFound:
        raise ValueError(f"No camera settings link found for camera_settings_id {camera_settings.id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def update_is_optimal_by_camera_settings_id(camera_settings_id: int):
    try:
        with Session(engine) as session:
            optimal_camera_settings = session.get(CameraSettingsLink, camera_settings_id)
            beam_run = session.get(BeamRun, optimal_camera_settings.beam_run_id)
            beam_run_statement = (select(BeamRun)
                                  .join(CameraSettingsLink)
                                  .where(CameraSettingsLink.id == camera_settings_id))
            beam_run = session.exec(beam_run_statement).one()
            beam_run_id = beam_run.id
            experiment_id = beam_run.experiment_id
            all_related_camera_settings_statement = (select(CameraSettingsLink)
                                                     .join(BeamRun)
                                                     .join(Experiment)
                                                     .where(CameraSettingsLink.camera_id == optimal_camera_settings.camera_id)
                                                     .where(BeamRun.ESS_beam_energy == beam_run.ESS_beam_energy)
                                                     .where(BeamRun.beam_current == beam_run.beam_current)
                                                     .where(Experiment.id == beam_run.experiment_id))
            all_related_camera_settings = session.exec(all_related_camera_settings_statement).all()
            # all_related_test_beam_runs_statement = (select(BeamRun)
            #                                                        .where(BeamRun.is_test == True)
            #                                                        .where(BeamRun.ESS_beam_energy == beam_run.ESS_beam_energy)
            #                                                        .where(BeamRun.beam_current == beam_run.beam_current)
            #                                                        .where(BeamRun.experiment_id == beam_run.experiment_id))
            # all_related_test_beam_runs = session.exec(all_related_test_beam_runs_statement).all()
            # all_related_camera_settings = []
            # for related_test_beam_run in all_related_test_beam_runs:
            #     related_camera_settings_statement = (select(CameraSettingsLink)
            #                                          .where(CameraSettingsLink.beam_run_id == related_test_beam_run.id)
            #                                          .where(CameraSettingsLink.camera_id == optimal_camera_settings.camera_id))
            #     related_camera_settings = session.exec(related_camera_settings_statement).all()
            #     all_related_camera_settings.extend(related_camera_settings)
            for camera_settings in all_related_camera_settings:
                camera_settings.is_optimal = False
            optimal_camera_settings.is_optimal = True
            session.commit()
            return {"message": f"Camera settings {optimal_camera_settings.id} set to optimal"}
    except NoResultFound:
        raise ValueError(f"No camera settings link found for camera_settings_id {camera_settings.id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

def update_no_optimal_in_run(photo_ids: int):
    with Session(engine) as session:
        for photo_id in photo_ids:
            statement = select(CameraSettingsLink).join(Photo).where(Photo.id == photo_id)
            camera_settings = session.exec(statement).one()
            camera_settings.is_optimal = False
        session.commit()
        return {"message": f"Photos with ids: {photo_ids} all set to not optimal camera settings"}

def update_number_of_images(camera_settings_link_id: int, number_of_images: int):
    try:
        with Session(engine) as session:
            statement = select(CameraSettingsLink).where(CameraSettingsLink.id == camera_settings_link_id)
            result = session.exec(statement).one()
            result.number_of_images = number_of_images
            session.commit()
            return {"message": f"Number of images updated for camera settings link with id = {camera_settings_link_id}."}
    except NoResultFound:
        raise ValueError(f"No camera settings link found with id = {camera_settings_link_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")
    
def update_take_raw_images(camera_settings_link_id: int, take_raw_images: bool):
    try:
        with Session(engine) as session:
            statement = select(CameraSettingsLink).where(CameraSettingsLink.id == camera_settings_link_id)
            result = session.exec(statement).one()
            result.take_raw_images = take_raw_images
            session.commit()
            return {"message": f"Take raw images updated for camera settings link with id = {camera_settings_link_id}."}
    except NoResultFound:
        raise ValueError(f"No camera settings link found with id = {camera_settings_link_id}.")
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# Delete
