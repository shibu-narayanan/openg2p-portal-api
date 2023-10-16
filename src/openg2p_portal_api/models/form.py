from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProgramForm(BaseModel):
    model_config = ConfigDict(extra="allow")

    program_id: Optional[int] = None
    form_id: Optional[int] = None
    form_json: Optional[str] = None
    submission_data: Optional[str] = None
    program_name: Optional[str] = None
    program_description: Optional[str] = None
