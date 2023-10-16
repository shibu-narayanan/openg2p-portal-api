from typing import List, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModelWithTimes
from sqlalchemy import ForeignKey, Integer, String, Boolean, and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload


class Program(BaseORMModelWithTimes):
    __tablename__ = 'g2p.program' 

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(String())
    status: Mapped[bool]  = mapped_column(Boolean())
    description: Mapped[str] = mapped_column(String())
    has_applied: Mapped[bool] = mapped_column(Boolean())
    is_portal_form_mapped: Mapped[bool] = mapped_column(Boolean())
    last_application_status: Mapped[str] = mapped_column(String())
    is_multiple_form_submission: Mapped[str] = mapped_column(Boolean())

