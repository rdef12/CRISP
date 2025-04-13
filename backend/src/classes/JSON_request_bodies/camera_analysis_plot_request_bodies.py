from typing import List, Optional
from pydantic import BaseModel

from src.database.models import CameraAnalysis, CameraAnalysisPlot

class CameraAnalysisPlotGetResponse(BaseModel):
    id: int
    plot_type: str
    plot_figure: str
    figure_format: str
    parameter_labels: Optional[List[str]] = None
    parameter_values: Optional[List[float]] = None
    parameter_uncertainties: Optional[List[float]] = None
    chi_squared: Optional[float]
    number_of_data_points: Optional[int]
    description: Optional[str] = None