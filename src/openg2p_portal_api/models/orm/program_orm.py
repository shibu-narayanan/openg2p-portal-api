from typing import List

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModelWithId
from sqlalchemy import Integer, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .program_membership_orm import ProgramMembershipORM


class ProgramORM(BaseORMModelWithId):
    __tablename__ = "g2p_program"

    name: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    self_service_portal_form: Mapped[int] = mapped_column(Integer())
    is_multiple_form_submission: Mapped[str] = mapped_column()

    membership = relationship("ProgramMembershipORM", back_populates="program")

    # has_applied: Mapped[bool] = mapped_column()
    # last_application_status: Mapped[str] = mapped_column(String())

    @classmethod
    async def get_all_programs(cls) -> List["ProgramORM"]:
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(cls, ProgramMembershipORM.partner_id)
                .outerjoin(
                    ProgramMembershipORM,
                    ProgramORM.id == ProgramMembershipORM.program_id,
                )
                .order_by(cls.id.asc())
            )
            result = await session.execute(stmt)
            response = list(result.scalars())

        return response
