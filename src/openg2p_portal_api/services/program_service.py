from openg2p_fastapi_common.service import BaseService

from ..models.orm.program_orm import ProgramORM
from ..models.program import Program


class ProgramService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_all_program_service(self):
        return [
            Program.model_validate(program)
            for program in await ProgramORM.get_all_programs()
        ]

    async def get_program_by_id_service(self, programid: int):
        res = await ProgramORM.get_all_by_program_id(programid)
        if res:
            return Program.model_validate(res)
        else:
            # TODO: Add error handling
            pass

    async def get_program_by_key_service(self, keyword: str):
        membership = await ProgramORM.get_all_program_by_keyword(keyword)

        return membership
