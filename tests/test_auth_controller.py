from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openg2p_fastapi_auth.models.orm.login_provider import LoginProvider
from openg2p_portal_api.controllers.auth_controller import AuthController
from openg2p_portal_api.models.orm.auth_oauth_provider import AuthOauthProviderORM
from openg2p_portal_api.models.orm.partner_orm import (
    BankORM,
    PartnerBankORM,
    PartnerORM,
    PartnerPhoneNoORM,
)
from openg2p_portal_api.models.orm.reg_id_orm import RegIDORM, RegIDTypeORM
from openg2p_portal_api.models.profile import UpdateProfile
from sqlalchemy.exc import IntegrityError

TEST_CONSTANTS = {
    "PARTNER_ID": "test_partner_id",
    "UNAUTHORIZED_MESSAGE": "Unauthorized",
    "NATIONAL_ID": "National ID",
    "PASSPORT": "Passport",
    "BANK": "Test Bank",
    "PHONE_NUMBER": "+1234567890",
}


class TestAuthController:
    @pytest.fixture
    def auth_controller(self):
        with patch.object(
            AuthController, "partner_service", new_callable=MagicMock
        ) as mock_partner_service:
            controller = AuthController()
            controller.partner_service = mock_partner_service
            yield controller

    @pytest.fixture
    def mock_auth(self) -> MagicMock:
        mock_auth = MagicMock()
        mock_auth.partner_id = TEST_CONSTANTS["PARTNER_ID"]
        return mock_auth

    @pytest.fixture
    def mock_partner(self) -> MagicMock:
        mock_partner = MagicMock()
        mock_partner.id = 1
        mock_partner.email = "test@example.com"
        mock_partner.gender = "M"
        mock_partner.addl_name = "Test"
        mock_partner.given_name = "John"
        mock_partner.family_name = "Doe"
        mock_partner.birthdate = "1990-01-01"
        mock_partner.birth_place = "Test City"
        return mock_partner

    @pytest.mark.asyncio
    async def test_get_profile_success(
        self,
        auth_controller: AuthController,
        mock_auth: MagicMock,
        mock_partner: MagicMock,
    ):
        mock_reg_ids = [
            MagicMock(
                id_type=MagicMock(name=TEST_CONSTANTS["NATIONAL_ID"]),
                value="123456789",
                expiry_date="2025-01-01",
            ),
            MagicMock(
                id_type=MagicMock(name=TEST_CONSTANTS["PASSPORT"]),
                value="AB123456",
                expiry_date="2026-01-01",
            ),
        ]

        mock_bank_accounts = [
            MagicMock(
                bank=MagicMock(name=TEST_CONSTANTS["BANK"]),
                bank_id=1,
                acc_number="1234567890",
                account_holder_name="John Doe",
            )
        ]

        mock_phone_numbers = [
            MagicMock(
                phone_no=TEST_CONSTANTS["PHONE_NUMBER"],
                is_primary=True,
                date_collected="2023-01-01",
            )
        ]

        PartnerORM.get_partner_data = AsyncMock(return_value=mock_partner)
        RegIDORM.get_all_partner_ids = AsyncMock(return_value=mock_reg_ids)
        PartnerBankORM.get_partner_banks = AsyncMock(return_value=mock_bank_accounts)
        PartnerPhoneNoORM.get_partner_phone_details = AsyncMock(
            return_value=mock_phone_numbers
        )

        mock_reg_id_type1 = MagicMock(spec=RegIDTypeORM)
        mock_reg_id_type1.name = TEST_CONSTANTS["NATIONAL_ID"]
        mock_reg_id_type2 = MagicMock(spec=RegIDTypeORM)
        mock_reg_id_type2.name = TEST_CONSTANTS["PASSPORT"]

        RegIDTypeORM.get_id_type_name = AsyncMock(
            side_effect=lambda x: mock_reg_id_type1
            if x == mock_reg_ids[0].id_type
            else mock_reg_id_type2
        )

        mock_bank = MagicMock()
        mock_bank.name = TEST_CONSTANTS["BANK"]
        BankORM.get_by_id = AsyncMock(return_value=mock_bank)

        profile = await auth_controller.get_profile(mock_auth)

        assert profile.id == 1, "Profile ID should match the mock partner ID"
        assert (
            profile.email == "test@example.com"
        ), "Email should match the mock partner email"
        assert profile.gender == "M", "Gender should match the mock partner gender"
        assert (
            profile.addl_name == "Test"
        ), "Additional name should match the mock partner additional name"
        assert (
            profile.given_name == "John"
        ), "Given name should match the mock partner given name"
        assert (
            profile.family_name == "Doe"
        ), "Family name should match the mock partner family name"
        assert (
            str(profile.birthdate) == "1990-01-01"
        ), "Birthdate should match the mock partner birthdate"
        assert (
            profile.birth_place == "Test City"
        ), "Birth place should match the mock partner birth place"

        assert len(profile.ids) == 2, "Should have two IDs from mock data"
        assert (
            profile.ids[0].id_type == TEST_CONSTANTS["NATIONAL_ID"]
        ), "First ID type should match the mock data"
        assert (
            profile.ids[0].value == "123456789"
        ), "First ID value should match the mock data"
        assert (
            profile.ids[1].id_type == TEST_CONSTANTS["PASSPORT"]
        ), "Second ID type should match the mock data"
        assert (
            profile.ids[1].value == "AB123456"
        ), "Second ID value should match the mock data"

        assert len(profile.bank_ids) == 1, "Should have one bank account from mock data"
        assert (
            profile.bank_ids[0].bank_name == TEST_CONSTANTS["BANK"]
        ), "Bank name should match the mock data"
        assert (
            profile.bank_ids[0].acc_number == "1234567890"
        ), "Account number should match the mock data"

        assert (
            len(profile.phone_numbers) == 1
        ), "Should have one phone number from mock data"
        assert (
            profile.phone_numbers[0].phone_no == TEST_CONSTANTS["PHONE_NUMBER"]
        ), "Phone number should match the mock data"

    @pytest.mark.asyncio
    async def test_get_profile_with_empty_related_data(
        self,
        auth_controller: AuthController,
        mock_auth: MagicMock,
        mock_partner: MagicMock,
    ):
        PartnerORM.get_partner_data = AsyncMock(return_value=mock_partner)
        RegIDORM.get_all_partner_ids = AsyncMock(return_value=[])
        PartnerBankORM.get_partner_banks = AsyncMock(return_value=[])
        PartnerPhoneNoORM.get_partner_phone_details = AsyncMock(return_value=[])

        profile = await auth_controller.get_profile(mock_auth)

        assert profile.id == 1, "Profile ID should match the mock partner ID"
        assert (
            str(profile.birthdate) == "1990-01-01"
        ), "Birthdate should match the mock partner birthdate"
        assert len(profile.ids) == 0, "Should have no IDs as per mock data"
        assert (
            len(profile.bank_ids) == 0
        ), "Should have no bank accounts as per mock data"
        assert (
            len(profile.phone_numbers) == 0
        ), "Should have no phone numbers as per mock data"

    @pytest.mark.asyncio
    async def test_update_profile(
        self, auth_controller: AuthController, mock_auth: MagicMock
    ):
        update_data = UpdateProfile(
            given_name="John", family_name="Doe", email="john@example.com"
        )

        auth_controller.partner_service.update_partner_info = AsyncMock()

        result = await auth_controller.update_profile(update_data, mock_auth)

        auth_controller.partner_service.update_partner_info.assert_called_once_with(
            TEST_CONSTANTS["PARTNER_ID"], update_data.model_dump(exclude={"id"})
        )
        assert (
            result == "Updated the partner info"
        ), "Update result should match expected message"

    @pytest.mark.asyncio
    async def test_update_profile_integrity_error(
        self, auth_controller: AuthController, mock_auth: MagicMock
    ):
        update_data = UpdateProfile(given_name="John")

        auth_controller.partner_service.update_partner_info = AsyncMock(
            side_effect=IntegrityError(None, None, None)
        )

        result = await auth_controller.update_profile(update_data, mock_auth)
        assert (
            result == "Could not add to registrant to program!!"
        ), "Error message should match expected message"

    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self):
        controller = AuthController()
        mock_auth = MagicMock()
        mock_auth.partner_id = None

        with pytest.raises(Exception, match=TEST_CONSTANTS["UNAUTHORIZED_MESSAGE"]):
            await controller.get_profile(mock_auth)

    @pytest.mark.asyncio
    async def test_get_login_providers_db(self, auth_controller: AuthController):
        mock_provider = MagicMock()
        mock_provider.map_auth_provider_to_login_provider.return_value = LoginProvider(
            id=1, name="Test Provider", type="oauth2"
        )

        AuthOauthProviderORM.get_all = AsyncMock(return_value=[mock_provider])

        result = await auth_controller.get_login_providers_db()

        assert len(result) == 1, "Should return one provider from mock data"
        assert isinstance(
            result[0], LoginProvider
        ), "Result should be a LoginProvider instance"
        assert result[0].id == 1, "Provider ID should match the mock data"
        assert (
            result[0].name == "Test Provider"
        ), "Provider name should match the mock data"

    @pytest.mark.asyncio
    async def test_get_login_provider_db_by_id(self, auth_controller: AuthController):
        mock_provider = MagicMock()
        mock_provider.map_auth_provider_to_login_provider.return_value = LoginProvider(
            id=1, name="Test Provider", type="oauth2"
        )

        AuthOauthProviderORM.get_by_id = AsyncMock(return_value=mock_provider)

        result = await auth_controller.get_login_provider_db_by_id(1)

        assert isinstance(
            result, LoginProvider
        ), "Result should be a LoginProvider instance"
        assert result.id == 1, "Provider ID should match the mock data"
        assert (
            result.name == "Test Provider"
        ), "Provider name should match the mock data"

    @pytest.mark.asyncio
    async def test_get_login_provider_db_by_id_not_found(
        self, auth_controller: AuthController
    ):
        AuthOauthProviderORM.get_by_id = AsyncMock(return_value=None)

        result = await auth_controller.get_login_provider_db_by_id(999)
        assert result is None, "Result should be None for non-existent provider"

    @pytest.mark.asyncio
    async def test_get_login_provider_db_by_iss(self, auth_controller: AuthController):
        mock_provider = MagicMock()
        mock_provider.map_auth_provider_to_login_provider.return_value = LoginProvider(
            id=1, name="Test Provider", type="oauth2"
        )

        AuthOauthProviderORM.get_auth_provider_from_iss = AsyncMock(
            return_value=mock_provider
        )

        result = await auth_controller.get_login_provider_db_by_iss("test_issuer")

        assert isinstance(
            result, LoginProvider
        ), "Result should be a LoginProvider instance"
        assert result.id == 1, "Provider ID should match the mock data"
        assert (
            result.name == "Test Provider"
        ), "Provider name should match the mock data"

    @pytest.mark.asyncio
    async def test_get_login_provider_db_by_iss_not_found(
        self, auth_controller: AuthController
    ):
        AuthOauthProviderORM.get_auth_provider_from_iss = AsyncMock(return_value=None)

        result = await auth_controller.get_login_provider_db_by_iss("invalid_issuer")
        assert result is None, "Result should be None for non-existent issuer"
