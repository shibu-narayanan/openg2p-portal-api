from openg2p_fastapi_common.models import BaseORMModelWithTimes
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column


class ProgramORM(BaseORMModelWithTimes):
    __tablename__ = "g2p_program"

    name: Mapped[str] = mapped_column(String())
    status: Mapped[bool] = mapped_column(Boolean())
    description: Mapped[str] = mapped_column(String())
    has_applied: Mapped[bool] = mapped_column(Boolean())
    is_portal_form_mapped: Mapped[bool] = mapped_column(Boolean())
    last_application_status: Mapped[str] = mapped_column(String())
    is_multiple_form_submission: Mapped[str] = mapped_column(Boolean())
