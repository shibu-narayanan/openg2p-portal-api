from typing import List

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModelWithId
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

# from .formio_builder_orm import FormORM


class ProgramORM(BaseORMModelWithId):
    __tablename__ = "g2p_program"

    name: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    is_multiple_form_submission: Mapped[str] = mapped_column()

    membership = relationship("ProgramMembershipORM", back_populates="program")

    self_service_portal_form: Mapped[int] = mapped_column(
        ForeignKey("formio_builder.id")
    )
    form = relationship("FormORM", back_populates="program")

    @classmethod
    async def get_all_programs(cls) -> List["ProgramORM"]:
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(cls).options(selectinload(cls.membership)).order_by(cls.id.asc())
            )
            result = await session.execute(stmt)
            response = list(result.scalars())

        return response

    @classmethod
    async def get_all_by_program_id(cls, programid: int):
        response = None
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(cls)
                .filter(cls.id == programid)
                .options(selectinload(cls.membership))
            )
            result = await session.execute(stmt)
            response = result.scalar()

        return response

    @classmethod
    async def get_program_form(cls, programid: int = None):
        response = None
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(cls).filter(cls.id == programid).options(selectinload(cls.form))
            )
            result = await session.execute(stmt)
            response = result.scalar()

        return response
