from openg2p_fastapi_common.controller import BaseController

from ..config import Settings

from sqlalchemy.orm import Session

from ..models.program import ProgramList
from ..services.program_service import ProgramService

_config = Settings.get_config()


class ProgramController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._program_service = ProgramService.get_component()

        self.router.add_api_route(
            "/program",
            self.get_programs,
            responses={200: {"model": ProgramList}},
            methods=["GET"],
        )

        self.router.add_api_route(
            "/program/{programid}",
            self.get_program_by_id,
            responses={200: {"model": ProgramList}},
            methods=["GET"],
        )

    @property
    def program_service(self):
        if not self._program_service:
            self._program_service = ProgramService.get_component()
        return self._program_service

    async def get_programs(self):
        return {"programs": "list of programs"}
    
    async def get_program_by_id(self, programid: int):
        return {"program": programid}

