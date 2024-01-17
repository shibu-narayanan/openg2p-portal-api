from typing import List, Optional

from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .cycle_orm import CycleORM


class CycleMembershipORM(BaseORMModel):
    __tablename__ = "g2p_cycle_membership"

    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column()
    cycle_id: Mapped[int] = mapped_column(ForeignKey("g2p_cycle.id"))
    cycles: Mapped[Optional[List["CycleORM"]]] = relationship(
        back_populates="cycle_memberships"
    )
