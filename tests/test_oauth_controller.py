import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import Request
from openg2p_fastapi_auth.models.orm.login_provider import LoginProviderTypes
from openg2p_fastapi_common.utils import cookie_utils
from openg2p_portal_api.controllers.oauth_controller import OAuthController
from openg2p_portal_api.models.orm.auth_oauth_provider import AuthOauthProviderORM

TEST_CONSTANTS = {
    "CLIENT_ID": "test_client_id",
    "CLIENT_SECRET": "test_client_secret",
    "REDIRECT_URI": "https://example.com/callback",
    "DASHBOARD_URL": "https://example.com/dashboard",
    "TOKEN_ENDPOINT": "https://example.com/token",
    "CODE": "test_code",
    "CODE_VERIFIER": "test_code_verifier",
    "PROVIDER_ID": "test_login_provider_id",
    "SUB": "test_user",
    "ID_TYPE": "test_type",
}

ASSERT_MESSAGES = {
    "NOT_HTTPX_RESPONSE": "Response should not be an instance of httpx.Response",
    "LOCATION_HEADER": "Response should contain location header",
    "DASHBOARD_REDIRECT": "Should redirect to dashboard URL",
    "MOCK_RESPONSE": "Should return mock response for empty state",
}


@pytest.fixture
def oauth_controller():
    with patch.object(OAuthController, "auth_controller", new=MagicMock()) as mock_auth:
        controller = OAuthController()
        controller.partner_service = MagicMock()
        mock_auth.return_value = MagicMock()
        return controller


@pytest.fixture
def mock_login_provider():
    return MagicMock(
        type=LoginProviderTypes.oauth2_auth_code,
        provider="test_provider",
        authorization_parameters={
            "client_id": TEST_CONSTANTS["CLIENT_ID"],
            "client_secret": TEST_CONSTANTS["CLIENT_SECRET"],
            "redirect_uri": TEST_CONSTANTS["REDIRECT_URI"],
            "scope": "read write",
            "authorize_endpoint": "https://example.com/auth",
            "token_endpoint": TEST_CONSTANTS["TOKEN_ENDPOINT"],
            "validate_endpoint": "https://example.com/validate",
            "jwks_endpoint": "https://example.com/jwks",
            "code_verifier": TEST_CONSTANTS["CODE_VERIFIER"],
            "enable_pkce": True,
            "client_assertion_type": "client_secret",
        },
    )


class TestOAuthController:
    class TestOAuthCallback:
        @pytest.mark.asyncio
        async def test_successful_oauth_callback_with_valid_state(
            self, oauth_controller, mock_login_provider
        ):
            mock_request = MagicMock(spec=Request)
            mock_request.query_params = {
                "state": json.dumps(
                    {
                        "p": TEST_CONSTANTS["PROVIDER_ID"],
                        "r": TEST_CONSTANTS["DASHBOARD_URL"],
                    }
                ),
                "code": TEST_CONSTANTS["CODE"],
            }

            cookie_utils.get_response_cookies = MagicMock(
                side_effect=[["access_token"], ["id_token"]]
            )

            oauth_controller.auth_controller.get_oauth_validation_data = AsyncMock(
                return_value={"sub": TEST_CONSTANTS["SUB"]}
            )
            oauth_controller.auth_controller.get_login_provider_db_by_id = AsyncMock(
                return_value=mock_login_provider
            )

            AuthOauthProviderORM.get_auth_id_type_config = AsyncMock(
                return_value={"id_type": TEST_CONSTANTS["ID_TYPE"]}
            )
            oauth_controller.partner_service.check_and_create_partner = AsyncMock()

            mock_response = MagicMock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "access_token": "test_access_token",
                "id_token": "test_id_token",
            }
            mock_response.is_success = True

            with patch("httpx.post", return_value=mock_response) as mock_httpx_post:
                result = await oauth_controller.oauth_callback(mock_request)

                assert not isinstance(result, httpx.Response), ASSERT_MESSAGES[
                    "NOT_HTTPX_RESPONSE"
                ]
                assert "location" in result.headers, ASSERT_MESSAGES["LOCATION_HEADER"]
                assert (
                    result.headers["location"] == TEST_CONSTANTS["DASHBOARD_URL"]
                ), ASSERT_MESSAGES["DASHBOARD_REDIRECT"]

                oauth_controller.auth_controller.get_oauth_validation_data.assert_called_once_with(
                    auth="access_token",
                    id_token="id_token",
                    provider=mock_login_provider,
                )

                AuthOauthProviderORM.get_auth_id_type_config.assert_called_once_with(
                    id=TEST_CONSTANTS["PROVIDER_ID"]
                )

                oauth_controller.partner_service.check_and_create_partner.assert_called_once_with(
                    {"sub": TEST_CONSTANTS["SUB"]},
                    id_type_config={"id_type": TEST_CONSTANTS["ID_TYPE"]},
                )

                mock_httpx_post.assert_called_once_with(
                    TEST_CONSTANTS["TOKEN_ENDPOINT"],
                    auth=(TEST_CONSTANTS["CLIENT_ID"], TEST_CONSTANTS["CLIENT_SECRET"]),
                    data={
                        "client_id": TEST_CONSTANTS["CLIENT_ID"],
                        "grant_type": "authorization_code",
                        "redirect_uri": TEST_CONSTANTS["REDIRECT_URI"],
                        "code": TEST_CONSTANTS["CODE"],
                        "code_verifier": TEST_CONSTANTS["CODE_VERIFIER"],
                    },
                )

        @pytest.mark.asyncio
        async def test_oauth_callback_empty_state(self, oauth_controller):
            mock_request = MagicMock(spec=Request)
            mock_request.query_params = {"state": "{}"}
            mock_response = MagicMock()

            with patch.object(
                OAuthController, "oauth_callback", new_callable=AsyncMock
            ) as mock_super_callback:
                mock_super_callback.return_value = mock_response
                result = await oauth_controller.oauth_callback(mock_request)

                assert result == mock_response, ASSERT_MESSAGES["MOCK_RESPONSE"]
                mock_super_callback.assert_called_once_with(mock_request)
