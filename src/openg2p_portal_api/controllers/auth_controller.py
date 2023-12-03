from typing import Annotated

from fastapi import Depends
from openg2p_fastapi_auth.controllers.auth_controller import AuthController

from ..config import Settings
from ..dependencies import JwtBearerAuth
from ..models.credentials import AuthCredentials
from ..models.orm.partner_orm import PartnerORM
from ..models.orm.reg_id_orm import RegIDORM
from ..models.profile import Profile

_config = Settings.get_config()


class AuthController(AuthController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_profile(
        self,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        online: bool = True,
    ):
        res = await super().get_profile(auth, online)

        partner_data = await PartnerORM.get_partner_data(auth.partner_id)
        partner_ids_data = await RegIDORM.get_all_partner_ids(partner_data.id)

        return Profile(id=partner_data.id, **res.model_dump(), ids=partner_ids_data)
