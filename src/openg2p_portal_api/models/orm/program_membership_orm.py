from typing import List

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModelWithId
from sqlalchemy import ForeignKey, Integer, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ProgramMembershipORM(BaseORMModelWithId):
    __tablename__ = "g2p_program_membership"

    partner_id: Mapped[int] = mapped_column(Integer())
    program_id: Mapped[int] = mapped_column(ForeignKey("g2p_program.id"))
    latest_registrant_info_status: Mapped[str] = mapped_column(String())

    program = relationship("ProgramORM", back_populates="membership")

    @classmethod
    async def get_memberships(cls, program_id: int) -> List["ProgramMembershipORM"]:
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(cls).where(cls.program_id == program_id).order_by(cls.id.asc())
            )

            result = await session.execute(stmt)

            response = list(result.scalars())
        return response
