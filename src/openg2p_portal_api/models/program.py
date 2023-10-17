from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator


class ProgramMembership(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    partner_id: Optional[int] = None
    latest_registrant_info_status: Optional[str] = None


class Program(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: Optional[str] = None
    active: Optional[bool] = None
    description: Optional[str] = None
    self_service_portal_form: Optional[int] = Field(..., exclude=True)
    is_portal_form_mapped: Optional[bool] = None
    is_multiple_form_submission: Optional[bool] = None

    program_membership_ids: Optional[List[ProgramMembership]] = []

    has_applied: Optional[bool] = None
    last_application_status: Optional[str] = None

    @validator("is_portal_form_mapped", pre=True, always=True)
    def is_portal_form(cls, v, values):
        return bool(values.get("self_service_portal_form"))

    @validator("has_applied", pre=True, always=True)
    def has_applied(cls, v, values):
        # TODO: Iterate over program_membership_ids and check whether the user is present or not.
        return False
