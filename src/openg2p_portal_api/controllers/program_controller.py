from typing import List

from openg2p_fastapi_common.controller import BaseController

from ..config import Settings
from ..models.orm.program_orm import ProgramORM
from ..models.program import Program

_config = Settings.get_config()


class ProgramController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.router.add_api_route(
            "/program",
            self.get_programs,
            responses={200: {"model": List[Program]}},
            methods=["GET"],
        )

        self.router.add_api_route(
            "/program/{programid}",
            self.get_program_by_id,
            responses={200: {"model": Program}},
            methods=["GET"],
        )

    async def get_programs(self):
        return [
            Program.model_validate(program) for program in await ProgramORM.get_all()
        ]

    async def get_program_by_id(self, programid: int):
        res = await ProgramORM.get_by_id(programid)
        if res:
            return Program.model_validate(res)
        else:
            # TODO: Add error handling
            pass
