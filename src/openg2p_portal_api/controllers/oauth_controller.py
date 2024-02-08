from fastapi import Request
from openg2p_fastapi_auth.controllers.auth_controller import AuthController
from openg2p_fastapi_auth.controllers.oauth_controller import OAuthController
from openg2p_fastapi_common.utils import cookie_utils

from ..config import Settings
from ..services.partner_service import PartnerService

_config = Settings.get_config()


class OAuthController(OAuthController):
    """
    OAuthController handles OAuth authentication flows and callbacks.
    """

    def __init__(self, **kwargs):
        """
        Initializes the OAuthController with necessary components and configurations.
        """
        super().__init__(**kwargs)
        self.auth_controller = AuthController.get_component()
        self.partner_service = PartnerService.get_component()

    async def oauth_callback(self, request: Request):
        """
        Handles the OAuth callback after a user has authenticated with an OAuth provider.

        Args:

            request (Request): The incoming request object containing the OAuth data.

        Returns:

            The response object after processing the OAuth callback.
        """
        res = await super().oauth_callback(request)

        userinfo_dict = await AuthController.get_oauth_validation_data(
            self,
            auth=cookie_utils.get_response_cookies(res, "X-Access-Token")[-1],
            id_token=cookie_utils.get_response_cookies(res, "X-ID-Token")[-1],
        )
        await self.partner_service.check_and_create_partner(userinfo_dict)

        return res
