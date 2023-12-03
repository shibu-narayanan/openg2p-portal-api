from typing import Annotated, List

from fastapi import Depends
from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError

from ..config import Settings
from ..dependencies import JwtBearerAuth
from ..models.credentials import AuthCredentials
from ..models.program import Program
from ..services.program_service import ProgramService

_config = Settings.get_config()


class ProgramController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._program_service = ProgramService.get_component()

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

    @property
    def program_service(self):
        if not self._program_service:
            self._program_service = ProgramService.get_component()
        return self._program_service

    async def get_programs(
        self, auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())]
    ):
        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )
        return await self.program_service.get_all_program_service(auth.partner_id)

    async def get_program_by_id(
        self, programid: int, auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())]
    ):
        if not auth.partner_id:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )

        return await self.program_service.get_program_by_id_service(
            programid, auth.partner_id
        )
