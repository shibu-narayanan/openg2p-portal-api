from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProgramForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    form_id: Optional[int] = Field(default=None, alias="id")
    json_schema: Optional[str] = Field(default=None, alias="schema")
    program_id: Optional[int] = None
    submission_data: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
