from openg2p_fastapi_common.service import BaseService
from sqlalchemy.orm import Session

from ..models.program import ProgramList


class ProgramService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_all_program(self, db: Session) -> ProgramList:
        programs = db.query(ProgramList).all()
        return programs
