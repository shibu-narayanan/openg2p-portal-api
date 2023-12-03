from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class ProgramMembership(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    partner_id: Optional[int] = None
    program_id: Optional[int] = None
    state: Optional[str] = None


class ProgramBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    name: Optional[str] = None
    description: Optional[str] = None


class Program(ProgramBase):
    model_config = ConfigDict(from_attributes=True)

    state: Optional[str] = None
    has_applied: Optional[bool] = None
    self_service_portal_form: Optional[int] = Field(default=None, exclude=True)
    is_portal_form_mapped: Optional[bool] = False
    is_multiple_form_submission: Optional[bool] = False
    last_application_status: Optional[str] = None

    @validator("is_portal_form_mapped", pre=True, always=True)
    def is_portal_form(cls, v, values):
        return bool(values.get("self_service_portal_form"))
