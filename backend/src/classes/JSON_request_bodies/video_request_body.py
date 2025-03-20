from pydantic import BaseModel, Field
from typing import Optional, List, Literal


# Directly related to possible args in video_script.py argparser
class VideoSettings(BaseModel):
    directory_name: str = Field(..., example="images", description="Name of the directory to save images to")
    num_of_images: int = Field(..., gt=0, example=10, description="Number of images to take") # 1 is default
    colour: Literal["all", "r", "g", "b"] = Field("all", example="red", description="Colour filter to apply") # all is default
    gain: int = Field(1, gt=0, example=1)
    log: bool = Field(False, example=True, description="Whether to produce log file in image directory or not")
    format: Literal["png", "jpg", "raw", "jpeg"] = Field("jpeg", example="png")
    bit_depth: Literal[8, 16] = Field(8, example=8, description="Bit depth of the image") # 8 is default
    frame_rate: int = Field(20, gt=0, example=30, description="Frame rate of the video") # 20 is default