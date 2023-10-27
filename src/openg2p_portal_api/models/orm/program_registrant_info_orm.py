from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import JSON, ForeignKey, Integer, String, and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column


class ProgramRegistrantInfoORM(BaseORMModel):
    __tablename__ = "g2p_program_registrant_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("g2p_program.id"))
    program_registrant_info: Mapped[dict] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(String())
    program_membership_id: Mapped[int] = mapped_column(Integer())
    registrant_id: Mapped[int] = mapped_column(Integer())


class ProgramRegistrantInfoDraftORM(BaseORMModel):
    __tablename__ = "g2p_program_registrant_info_draft"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("g2p_program.id"))
    registrant_id: Mapped[int] = mapped_column(Integer())
    program_registrant_info: Mapped[dict] = mapped_column(JSON)

    @classmethod
    async def get_draft_reg_info_by_id(cls, program_id: int, registrant_id: int):
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls).where(
                and_(cls.program_id == program_id, cls.registrant_id == registrant_id)
            )
            result = await session.execute(stmt)
        return result.scalar()
