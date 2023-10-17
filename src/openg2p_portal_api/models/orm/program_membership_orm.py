from openg2p_fastapi_common.models import BaseORMModelWithId
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ProgramMembershipORM(BaseORMModelWithId):
    __tablename__ = "g2p_program_membership"

    partner_id: Mapped[int] = mapped_column(Integer())
    program_id: Mapped[int] = mapped_column(Integer())
    latest_registrant_info_status: Mapped[str] = mapped_column(String())
