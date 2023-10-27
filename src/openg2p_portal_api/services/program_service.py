from openg2p_fastapi_common.service import BaseService

from ..models.orm.program_orm import ProgramORM


class ProgramService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_program_by_key_service(self, keyword: str):
        membership = await ProgramORM.get_all_program_by_keyword(keyword)

        return membership
