from fastapi import Request
from openg2p_fastapi_auth.controllers.auth_controller import AuthController
from openg2p_fastapi_auth.controllers.oauth_controller import OAuthController
from openg2p_fastapi_common.utils import cookie_utils

from ..config import Settings
from ..services.partner_service import PartnerService

_config = Settings.get_config()


class OAuthController(OAuthController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_controller = AuthController.get_component()
        self.partner_service = PartnerService.get_component()

    async def oauth_callback(self, request: Request):
        res = await super().oauth_callback(request)

        userinfo_dict = await AuthController.get_oauth_validation_data(
            self,
            auth=cookie_utils.get_response_cookies(res, "X-Access-Token")[-1],
            id_token=cookie_utils.get_response_cookies(res, "X-ID-Token")[-1],
        )
        await PartnerService.check_and_create_partner(self, userinfo_dict)

        return res
