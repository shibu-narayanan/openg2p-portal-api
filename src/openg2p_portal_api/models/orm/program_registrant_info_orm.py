from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ProgramRegistrantInfoORM(BaseORMModel):
    __tablename__ = "g2p_program_registrant_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("g2p_program.id"))
    program_registrant_info: Mapped[dict] = mapped_column(JSON)
    state: Mapped[str] = mapped_column(String())
    program_membership_id: Mapped[int] = mapped_column(Integer())
    registrant_id: Mapped[int] = mapped_column(Integer())
