from datetime import date, datetime
from typing import List, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModel, BaseORMModelWithId
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    select,
)
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .reg_id_orm import RegIDORM


class PartnerORM(BaseORMModelWithId):
    __tablename__ = "res_partner"

    name: Mapped[str] = mapped_column()
    family_name: Mapped[str] = mapped_column()
    given_name: Mapped[str] = mapped_column()
    addl_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    gender: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    birthdate: Mapped[date] = mapped_column(Date())
    birth_place: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    company_id: Mapped[Optional[int]] = mapped_column()
    income: Mapped[Optional[int]] = mapped_column()
    display_name: Mapped[str] = mapped_column()
    area_id: Mapped[Optional[int]] = mapped_column()
    civil_status: Mapped[str] = mapped_column()
    occupation: Mapped[str] = mapped_column()
    district: Mapped[str] = mapped_column()
    birthdate_not_exact: Mapped[bool] = mapped_column(Boolean(), default=False)
    registration_date: Mapped[date] = mapped_column(Date())
    notification_preference: Mapped[str] = mapped_column(
        String,
        CheckConstraint("notification_preference IN ('none', 'email', 'sms', 'both')"),
        default="none",
    )
    reg_ids: Mapped[Optional[List[RegIDORM]]] = relationship(back_populates="partner")

    create_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    write_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
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


class PartnerBankORM(BaseORMModelWithId):
    __tablename__ = "res_partner_bank"

    acc_number: Mapped[str] = mapped_column()
    partner_id: Mapped[int] = mapped_column()
    bank_id: Mapped[int] = mapped_column()

    @classmethod
    async def get_partner_banks(cls, id: int) -> List["PartnerBankORM"]:
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls).filter(cls.partner_id == id)
            result = await session.execute(stmt)

            response = list(result.scalars())
        return response


class BankORM(BaseORMModelWithId):
    __tablename__ = "res_bank"

    name: Mapped[int] = mapped_column()


class PartnerPhoneNoORM(BaseORMModel):
    __tablename__ = "g2p_phone_number"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_no: Mapped[str] = mapped_column()
    partner_id: Mapped[int] = mapped_column(ForeignKey("res_partner.id"))
    date_collected: Mapped[date] = mapped_column()

    partner: Mapped[PartnerORM] = relationship()

    @classmethod
    async def get_partner_phone_details(cls, id: int) -> List["PartnerPhoneNoORM"]:
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls).filter(cls.partner_id == id)
            result = await session.execute(stmt)

            response = list(result.scalars())
        return response
