from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import String, and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from .program_orm import ProgramORM


class FormORM(BaseORMModel):
    __tablename__ = "formio_builder"

    id: Mapped[int] = mapped_column(primary_key=True)
    schema: Mapped[str] = mapped_column(String())

    @classmethod
    async def get_program_form(cls, programid: int = None):
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(cls, ProgramORM.id, ProgramORM.name, ProgramORM.description)
                .outerjoin(
                    ProgramORM, ProgramORM.self_service_portal_form == FormORM.id
                )
                .where(
                    and_(
                        ProgramORM.id == programid,
                        cls.id == ProgramORM.self_service_portal_form,
                    )
                )
                .order_by(cls.id.asc())
            )

            result = await session.execute(stmt)
        return result
