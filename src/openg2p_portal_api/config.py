from typing import Dict

from openg2p_fastapi_auth.config import ApiAuthSettings
from openg2p_fastapi_auth.config import Settings as AuthSettings
from openg2p_fastapi_common.config import Settings
from pydantic_settings import SettingsConfigDict


class Settings(AuthSettings, Settings):
    model_config = SettingsConfigDict(
        env_prefix="portal_", env_file=".env", extra="allow"
    )

    openapi_title: str = "G2P Portal API"
    openapi_description: str = """
    This module implements G2P Portal APIs.

    ***********************************
    Further details goes here
    ***********************************
    """

    openapi_version: str = "0.1.0"

    login_providers_table_name: str = "g2p_self_service_login_providers"

    auth_id_type_ids: Dict[str, int] = []

    auth_api_get_programs: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_program_by_id: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_get_program_form: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_create_or_update_form_draft: ApiAuthSettings = ApiAuthSettings(
        enabled=True
    )
    auth_api_submit_form: ApiAuthSettings = ApiAuthSettings(enabled=True)
    auth_api_update_profile: ApiAuthSettings = ApiAuthSettings(enabled=True)
