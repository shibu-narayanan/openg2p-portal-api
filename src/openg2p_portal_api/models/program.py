from typing import List, Optional

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

    self_service_portal_form: Optional[int] = Field(default=None, exclude=True)
    is_portal_form_mapped: Optional[bool] = None
    is_multiple_form_submission: Optional[bool] = None
    membership: Optional[List[ProgramMembership]] = []
    has_applied: Optional[bool] = None

    @validator("is_portal_form_mapped", pre=True, always=True)
    def is_portal_form(cls, v, values):
        return bool(values.get("self_service_portal_form"))

    @validator("has_applied", pre=True, always=True)
    def has_applied(cls, v, values):
        # TODO: Iterate over program_membership_ids and check whether the user is present or not.
        return False
