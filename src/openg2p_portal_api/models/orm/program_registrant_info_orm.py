from openg2p_fastapi_common.models import BaseORMModelWithId
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class FormORM(BaseORMModelWithId):
    __tablename__ = "g2p_program_registrant_info"

    program_registrant_info: Mapped[str] = mapped_column(String())
