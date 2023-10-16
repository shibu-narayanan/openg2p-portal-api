from typing import Optional

from pydantic import BaseModel, ConfigDict


class Program(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    description: Optional[str] = None
    has_applied: Optional[bool] = None
    is_portal_form_mapped: Optional[bool] = None
    last_application_status: Optional[str] = None
    is_multiple_form_submission: Optional[bool] = None
