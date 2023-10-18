from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProgramForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    json_schema: Optional[str] = Field(..., alias="schema")
    program_id: Optional[int] = None
    submission_data: Optional[str] = None
    program_name: Optional[str] = None
    program_description: Optional[str] = None
