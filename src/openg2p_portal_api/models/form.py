from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProgramForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    schema: Optional[str] = None
    program_id: Optional[int] = None
    submission_data: Optional[str] = None
    program_name: Optional[str] = None
    program_description: Optional[str] = None
