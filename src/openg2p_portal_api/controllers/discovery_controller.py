from fastapi import Query
from openg2p_fastapi_common.controller import BaseController

from ..config import Settings
from ..models.program import ProgramBase
from ..services.program_service import ProgramService

_config = Settings.get_config()


class DiscoveryController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._program_service = ProgramService.get_component()

        self.router.tags += ["portal"]

        self.router.add_api_route(
            "/discovery",
            self.get_program_by_keyword,
            responses={200: {"model": ProgramBase}},
            methods=["GET"],
        )

    @property
    def program_service(self):
        if not self._program_service:
            self._program_service = ProgramService.get_component()
        return self._program_service

    async def get_program_by_keyword(
        self,
        keyword: str = Query(..., description="keyword to search"),
        page: int = Query(None, description="page number for pagination"),
        pagesize: int = Query(None, description="number of records in a page"),
    ):
        return await self.program_service.get_program_by_key_service(keyword)
