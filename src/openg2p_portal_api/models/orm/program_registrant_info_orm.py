from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class FormORM(BaseORMModel):
    __tablename__ = "g2p_program_registrant_info"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("g2p_program.id"))
    program_registrant_info: Mapped[str] = mapped_column(String())
