from pydantic import BaseModel
from typing import Optional

class SetupCreateRequest(BaseModel):
    setup_name: str

class SetupPatchRequest(BaseModel):
    name: str = None
# Block parameters
    block_x_dimension: Optional[float] = None
    block_x_dimension_unc: Optional[float] = None
    block_y_dimension: Optional[float] = None
    block_y_dimension_unc: Optional[float] = None
    block_z_dimension: Optional[float] = None
    block_z_dimension_unc: Optional[float] = None
    block_refractive_index: Optional[float] = None
    block_refractive_index_unc: Optional[float] = None