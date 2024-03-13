from typing import List, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.models import BaseORMModelWithId
from sqlalchemy import ForeignKey, String, and_, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from .cycle_membership_orm import CycleMembershipORM
from .cycle_orm import CycleORM
from .entitlement_orm import EntitlementORM
from .formio_builder_orm import FormORM
from .payment_orm import PaymentORM
from .program_membership_orm import ProgramMembershipORM
from .program_registrant_info_orm import ProgramRegistrantInfoORM


class ProgramORM(BaseORMModelWithId):
    __tablename__ = "g2p_program"

    name: Mapped[str] = mapped_column(String())
    description: Mapped[str] = mapped_column(String())
    is_multiple_form_submission: Mapped[str] = mapped_column()

    membership: Mapped[Optional[List["ProgramMembershipORM"]]] = relationship(
        back_populates="program"
    )

    self_service_portal_form: Mapped[int] = mapped_column(
        ForeignKey("formio_builder.id")
    )
    form: Mapped[Optional[List["FormORM"]]] = relationship(back_populates="program")
    # cycles: Mapped[Optional[list["CycleORM"]]] = relationship(back_populates="program")

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
    async def get_all_program_by_keyword(cls, keyword: str):
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(cls)
                .filter(cls.name.like(f"%{keyword}%"))
                .options(selectinload(cls.membership))
            )
            result = await session.execute(stmt)
            response = list(result.scalars().all()) if result.scalars() else []
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

    @classmethod
    async def get_program_summary(cls, partner_id: int) -> List["ProgramORM"]:
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(
                    ProgramORM.name.label("program_name"),
                    ProgramMembershipORM.state.label("enrollment_status"),
                    func.coalesce(func.sum(EntitlementORM.initial_amount), 0).label(
                        "total_funds_awaited"
                    ),
                    func.coalesce(func.sum(PaymentORM.amount_paid), 0).label(
                        "total_funds_received"
                    ),
                )
                .select_from(ProgramMembershipORM)
                .outerjoin(ProgramORM, ProgramMembershipORM.program_id == ProgramORM.id)
                .outerjoin(
                    CycleORM, ProgramMembershipORM.program_id == CycleORM.program_id
                )
                .outerjoin(
                    CycleMembershipORM,
                    and_(
                        ProgramMembershipORM.partner_id
                        == CycleMembershipORM.partner_id,
                        CycleORM.id == CycleMembershipORM.cycle_id,
                    ),
                )
                .outerjoin(
                    EntitlementORM,
                    and_(
                        CycleMembershipORM.partner_id == EntitlementORM.partner_id,
                        CycleMembershipORM.cycle_id == EntitlementORM.cycle_id,
                        EntitlementORM.state == "approved",
                    ),
                )
                .outerjoin(
                    PaymentORM,
                    and_(
                        EntitlementORM.id == PaymentORM.entitlement_id,
                        PaymentORM.status == "paid",
                    ),
                )
                .where(ProgramMembershipORM.partner_id == partner_id)
                .group_by(ProgramORM.name, ProgramMembershipORM.state)
            )
            result = await session.execute(stmt)
        return result.all()

    async def get_application_details(partner_id: int) -> List["ProgramORM"]:
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(
                    ProgramORM.name.label("program_name"),
                    ProgramRegistrantInfoORM.application_id.label("application_id"),
                    ProgramRegistrantInfoORM.create_date.label("date_applied"),
                    ProgramRegistrantInfoORM.state.label("application_status"),
                )
                .select_from(ProgramRegistrantInfoORM)
                .outerjoin(
                    ProgramMembershipORM,
                    and_(
                        ProgramMembershipORM.partner_id
                        == ProgramRegistrantInfoORM.registrant_id,
                        ProgramMembershipORM.program_id
                        == ProgramRegistrantInfoORM.program_id,
                    ),
                )
                .outerjoin(ProgramORM, ProgramMembershipORM.program_id == ProgramORM.id)
            )
            # print("####################################")
            # print(stmt)
            result = await session.execute(stmt)
        return result.all()

    async def get_benefit_details(cls, partner_id: int) -> List["ProgramORM"]:
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = (
                select(
                    ProgramORM.name.label("program_name"),
                    ProgramMembershipORM.state.label("enrollment_status"),
                    func.coalesce(EntitlementORM.initial_amount, 0).label(
                        "funds_awaited"
                    ),
                    func.coalesce(PaymentORM.amount_paid, 0).label("funds_received"),
                    EntitlementORM.ern.label("entitlement_reference_number"),
                    # CycleORM.name.label("cycle_name")
                )
                .select_from(ProgramMembershipORM)
                .outerjoin(ProgramORM, ProgramMembershipORM.program_id == ProgramORM.id)
                .outerjoin(
                    CycleORM, ProgramMembershipORM.program_id == CycleORM.program_id
                )
                .outerjoin(
                    CycleMembershipORM,
                    and_(
                        ProgramMembershipORM.partner_id
                        == CycleMembershipORM.partner_id,
                        CycleORM.id == CycleMembershipORM.cycle_id,
                    ),
                )
                .outerjoin(
                    EntitlementORM,
                    and_(
                        CycleMembershipORM.partner_id == EntitlementORM.partner_id,
                        CycleMembershipORM.cycle_id == EntitlementORM.cycle_id,
                        EntitlementORM.state == "approved",
                    ),
                )
                .outerjoin(
                    PaymentORM,
                    and_(
                        EntitlementORM.id == PaymentORM.entitlement_id,
                        PaymentORM.status == "paid",
                    ),
                )
                .where(ProgramMembershipORM.partner_id == partner_id)
            )
            result = await session.execute(stmt)
        return result.all()
