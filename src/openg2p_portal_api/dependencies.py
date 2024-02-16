from typing import Optional

from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from openg2p_fastapi_auth.dependencies import JwtBearerAuth
from openg2p_fastapi_auth.models.credentials import (
    AuthCredentials as OriginalAuthCredentials,
)
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError

from .config import Settings
from .models.credentials import AuthCredentials
from .models.orm.reg_id_orm import RegIDORM

_config = Settings.get_config(strict=False)


class JwtBearerAuth(JwtBearerAuth):
    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        res: OriginalAuthCredentials = await super().__call__(request)
        if not res:
            return None

        # TODO: to be removed
        id_type_id = _config.auth_id_type_ids[res.iss]

        partners = await RegIDORM.get_partner_by_reg_id(id_type_id, res.sub)
        if not partners:
            raise UnauthorizedError(
                message="Unauthorized. Partner Not Found in Registry."
            )
        partner = partners[0]

        new_res = AuthCredentials(partner_id=partner.partner_id, **res.model_dump())

        return new_res
