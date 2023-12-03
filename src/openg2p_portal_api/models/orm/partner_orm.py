from datetime import datetime
from typing import List, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModelWithId
from sqlalchemy import Boolean, DateTime, String, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .reg_id_orm import RegIDORM


class PartnerORM(BaseORMModelWithId):
    __tablename__ = "res_partner"

    name: Mapped[str] = mapped_column(String())
    family_name: Mapped[str] = mapped_column(String())
    given_name: Mapped[str] = mapped_column(String())
    email: Mapped[str] = mapped_column(String())
    # gender: Mapped[str] = mapped_column(String())
    birthdate: Mapped[datetime] = mapped_column(DateTime())
    # notification_preferences: Mapped[str] = mapped_column(String())

    reg_ids: Mapped[Optional[List[RegIDORM]]] = relationship(back_populates="partner")

    create_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    write_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    display_name: Mapped[str] = mapped_column(
        String(), default=lambda ctx: ctx.current_parameters["name"]
    )
    type: Mapped[str] = mapped_column(String(), default="contact")
    is_registrant: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_group: Mapped[bool] = mapped_column(Boolean(), default=False)

    @classmethod
    async def get_partner_data(cls, id: int):
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls).filter(cls.id == id)

            result = await session.execute(stmt)
        return result.scalar()
