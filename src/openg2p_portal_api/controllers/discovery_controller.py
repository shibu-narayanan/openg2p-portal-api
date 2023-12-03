from typing import Annotated

from fastapi import Depends, Query
from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError

from ..config import Settings
from ..dependencies import JwtBearerAuth
from ..models.credentials import AuthCredentials
from ..models.program import Program
from ..services.program_service import ProgramService

_config = Settings.get_config()


class DiscoveryController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._program_service = ProgramService.get_component()

        self.router.add_api_route(
            "/discovery",
            self.get_program_by_keyword,
            responses={200: {"model": Program}},
            methods=["GET"],
        )

    @property
    def program_service(self):
        if not self._program_service:
            self._program_service = ProgramService.get_component()
        return self._program_service

    async def get_program_by_keyword(
        self,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        keyword: str = Query(..., description="keyword to search"),
        page: int = Query(None, description="page number for pagination"),
        pagesize: int = Query(None, description="number of records in a page"),
    ):
        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )
        return await self.program_service.get_program_by_key_service(
            keyword, auth.partner_id
        )
