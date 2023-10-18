from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ProgramMembershipORM(BaseORMModel):
    __tablename__ = "g2p_program_membership"

    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column(Integer())
    program_id: Mapped[int] = mapped_column(ForeignKey("g2p_program.id"))

    program = relationship("ProgramORM", back_populates="membership")
