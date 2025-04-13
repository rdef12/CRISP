from sqlmodel import Session, select, PickleType
from sqlalchemy.orm.exc import NoResultFound

from src.database.database import engine
from src.database.models import CameraAnalysisPlot
import numpy as np
from typing import Literal, Optional, List
import pickle

# Create

def add_camera_analysis_plot(camera_analysis_id: int, plot_type: str, 
                             plot_figure: str, figure_format: str, 
                             parameter_labels: Optional[List[str]]=None,
                             parameter_values: Optional[List[float]]=None,
                             parameter_uncertainties: Optional[List[float]]=None, 
                             chi_squared: Optional[float]=None,
                             number_of_data_points: Optional[int]=None,
                             description: Optional[str]=None):
    try:
        if parameter_labels and parameter_values and len(parameter_labels) != len(parameter_values):
            raise ValueError("Length of parameter_labels must match length of parameter_values.")
        if parameter_values and parameter_uncertainties and len(parameter_values) != len(parameter_uncertainties):
            raise ValueError("Length of parameter_values must match length of parameter_uncertainties.")
        
        camera_analysis_plot = CameraAnalysisPlot(camera_analysis_id=camera_analysis_id, plot_type=plot_type,
                                                  plot_figure=plot_figure, figure_format=figure_format, 
                                                  parameter_labels=parameter_labels, parameter_values=parameter_values,
                                                  parameter_uncertainties=parameter_uncertainties,
                                                  chi_squared=chi_squared, number_of_data_points=number_of_data_points, 
                                                  description=description)
    except TypeError as e:
        raise TypeError(f"TypeError: {e}") from e
    except ValueError as e:
        raise ValueError(f"ValueError: {e}") from e
    with Session(engine) as session:
        session.add(camera_analysis_plot)
        session.commit()
        return {"message": f"Camera analysis plot added to camera analysis with id {camera_analysis_id}.",
                "id": camera_analysis_plot.id}
        
# Read

def get_camera_analysis_plot_by_id(camera_analysis_plot_id: int) -> CameraAnalysisPlot:
    with Session(engine) as session:
        return session.get(CameraAnalysisPlot, camera_analysis_plot_id)
    
def get_all_plot_types_by_camera_analysis_id(camera_analysis_id: int) -> dict:
    with Session(engine) as session:
        statement = select(CameraAnalysisPlot.id, CameraAnalysisPlot.plot_type).where(
            CameraAnalysisPlot.camera_analysis_id == camera_analysis_id
        )
        results = session.exec(statement).all()
        return {result.id: result.plot_type for result in results}

def get_plot_figure_by_camera_analysis_id_and_plot_name(camera_analysis_id: int, plot_name: str) -> bytes:
    with Session(engine) as session:
        statement = select(CameraAnalysisPlot.plot_figure).where(
            CameraAnalysisPlot.camera_analysis_id == camera_analysis_id,
            CameraAnalysisPlot.plot_type == plot_name
        )
        result = session.exec(statement).one()
        if result:
            return result
        else:
            raise NoResultFound(f"No plot found for camera_analysis_id {camera_analysis_id} and plot_name {plot_name}.")
        

def get_all_plot_figures_and_formats_by_camera_analysis_id(camera_analysis_id: int):
    with Session(engine) as session:
        statement = select(CameraAnalysisPlot).where(
            CameraAnalysisPlot.camera_analysis_id == camera_analysis_id
        )
        results = session.exec(statement).all()
        # List of dicts returned
        return [{"figure": result.plot_figure, "format": result.figure_format} for result in results]


# Delete

def delete_all_plots_by_camera_analysis_id(camera_analysis_id: int):
    with Session(engine) as session:
        statement = select(CameraAnalysisPlot).where(
            CameraAnalysisPlot.camera_analysis_id == camera_analysis_id
        )
        results = session.exec(statement).all()
        if not results:
            return {"message": f"No plots already exist for camera analysis with id {camera_analysis_id}."}
        for result in results:
            session.delete(result)
        session.commit()
    return {"message": f"All plots deleted for camera analysis with id {camera_analysis_id}."}


def delete_physical_bortfeld_plots_by_camera_analysis_id(camera_analysis_id: int):
    with Session(engine) as session:
        statement = select(CameraAnalysisPlot).where(
            CameraAnalysisPlot.camera_analysis_id == camera_analysis_id,
            CameraAnalysisPlot.plot_type == "physical_bortfeld_fit"
        )
        results = session.exec(statement).all()
        if not results:
            return {"message": f"No physical Bortfeld plots found for camera analysis with id {camera_analysis_id}."}
        for result in results:
            session.delete(result)
        session.commit()
    return {"message": f"All physical Bortfeld plots deleted for camera analysis with id {camera_analysis_id}."}
    