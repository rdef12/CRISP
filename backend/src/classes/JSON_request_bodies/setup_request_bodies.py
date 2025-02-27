from pydantic import BaseModel

class SetupCreateRequest(BaseModel):
    setup_name: str