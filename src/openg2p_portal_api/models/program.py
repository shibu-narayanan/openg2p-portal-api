from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProgramList(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    description: Optional[str] = None
    has_applied: Optional[bool] = None
    is_portal_form_mapped: Optional[bool] = None
    last_application_status: Optional[str] = None
    is_multiple_form_submission: Optional[bool] = None


    class Config:
        orm_mode = True