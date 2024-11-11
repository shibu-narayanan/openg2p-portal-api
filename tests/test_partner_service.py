from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openg2p_fastapi_common.errors.http_exceptions import InternalServerError
from openg2p_portal_api.models.orm.partner_orm import PartnerORM
from openg2p_portal_api.services.partner_service import PartnerService
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession

VALID_PARTNER_DATA = {
    "sub": "12345",
    "user_id": "user123",
    "name": "John Middle Doe",
    "email": "john@example.com",
    "gender": "male",
    "birthdate": "1990/01/01",
    "phone": "1234567890",
}

VALID_ID_TYPE_CONFIG = {
    "g2p_id_type": "national_id",
    "company_id": 1,
    "token_map": "name:name email:email gender:gender birthdate:birthdate phone:phone user_id:user_id",
    "date_format": "%Y/%m/%d",
}


@pytest.fixture
def mock_engine():
    engine = MagicMock(spec=Engine)
    engine.execution_options.return_value = engine
    return engine


@pytest.fixture
def mock_session(mock_engine):
    session = AsyncMock(spec=AsyncSession)
    session.get_bind = MagicMock(return_value=mock_engine)
    session.bind = mock_engine

    sync_session = MagicMock()
    sync_session.get_bind = MagicMock(return_value=mock_engine)
    session.sync_session = sync_session

    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.add = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()

    async_context = AsyncMock()
    async_context.__aenter__.return_value = session
    async_context.__aexit__.return_value = None

    return session, async_context


@pytest.fixture
def partner_service(mock_session, mock_engine):
    with patch("openg2p_portal_api.services.partner_service.dbengine") as mock_dbengine:
        mock_dbengine.get.return_value = mock_engine
        return PartnerService()


class TestPartnerService:
    @pytest.mark.asyncio
    async def test_check_and_create_partner_success(
        self, partner_service, mock_session
    ):
        expected_fields = ["name", "email", "phone", "gender", "birthdate"]

        with patch(
            "openg2p_portal_api.models.orm.reg_id_orm.RegIDORM.get_partner_by_reg_id",
            new_callable=AsyncMock,
            return_value=None,
        ), patch.object(
            partner_service,
            "get_partner_fields",
            new_callable=AsyncMock,
            return_value=expected_fields,
        ), patch(
            "openg2p_portal_api.services.partner_service.async_sessionmaker",
            return_value=lambda: mock_session[1],
        ):
            await partner_service.check_and_create_partner(
                VALID_PARTNER_DATA, VALID_ID_TYPE_CONFIG
            )

            session = mock_session[0]
            self._verify_partner_creation(session)

    def _verify_partner_creation(self, session):
        assert (
            session.add.call_count == 3
        ), "Session add should be called exactly 3 times"
        session.commit.assert_called_once(), "Session commit should be called exactly once"

        partner_call = session.add.call_args_list[0]
        created_partner = partner_call[0][0]

        assert isinstance(
            created_partner, PartnerORM
        ), "Created object should be instance of PartnerORM"
        assert (
            created_partner.name == "DOE, JOHN MIDDLE "
        ), "Partner name should be properly formatted"
        assert (
            created_partner.email == "john@example.com"
        ), "Partner email should match input"
        assert created_partner.phone == "1234567890", "Partner phone should match input"
        assert (
            created_partner.gender == "Male"
        ), "Partner gender should be properly capitalized"
        assert (
            created_partner.is_registrant is True
        ), "Partner should be marked as registrant"
        assert created_partner.active is True, "Partner should be marked as active"
        assert created_partner.company_id == 1, "Partner company_id should match config"

    @pytest.mark.asyncio
    async def test_check_and_create_partner_validation(self, partner_service):
        test_cases = [
            (None, "ID Type not configured"),
            ({}, "ID Type not configured"),
        ]

        for config, expected_error in test_cases:
            with pytest.raises(InternalServerError) as exc_info:
                await partner_service.check_and_create_partner({}, config)
            assert expected_error in str(
                exc_info.value
            ), f"Expected error message '{expected_error}' not found"

    @pytest.mark.parametrize(
        "input_data, expected_output",
        [
            (("Doe", "John", "Middle"), "DOE, JOHN MIDDLE "),
            (("Smith", "Jane", ""), "SMITH, JANE "),
            (("", "", ""), ""),
        ],
    )
    def test_create_partner_process_name(
        self, partner_service, input_data, expected_output
    ):
        result = partner_service.create_partner_process_name(*input_data)
        assert (
            result == expected_output
        ), f"Name processing failed for input {input_data}"

    @pytest.mark.parametrize(
        "input_gender, expected_output",
        [
            ("male", "Male"),
            ("female", "Female"),
            ("", ""),
            ("other", "Other"),
        ],
    )
    def test_create_partner_process_gender(
        self, partner_service, input_gender, expected_output
    ):
        result = partner_service.create_partner_process_gender(input_gender)
        assert (
            result == expected_output
        ), f"Gender processing failed for input '{input_gender}'"

    def test_create_partner_process_gender_none(self, partner_service):
        with pytest.raises(AttributeError):
            partner_service.create_partner_process_gender(None)

    @pytest.mark.parametrize(
        "date_str, date_format, expected_result",
        [
            ("1990/01/01", "%Y/%m/%d", date(1990, 1, 1)),
            (None, "%Y/%m/%d", None),
        ],
    )
    def test_create_partner_process_birthdate(
        self, partner_service, date_str, date_format, expected_result
    ):
        result = partner_service.create_partner_process_birthdate(date_str, date_format)
        assert (
            result == expected_result
        ), f"Birthdate processing failed for input '{date_str}'"

    def test_create_partner_process_birthdate_invalid(self, partner_service):
        with pytest.raises(ValueError, match=".*"):
            partner_service.create_partner_process_birthdate("invalid_date", "%Y/%m/%d")

    @pytest.mark.asyncio
    async def test_get_partner_fields(self, partner_service):
        expected_fields = ["name", "email", "phone"]

        with patch.object(
            PartnerORM,
            "get_partner_fields",
            new_callable=AsyncMock,
            return_value=expected_fields,
        ):
            result = await partner_service.get_partner_fields()
            assert (
                result == expected_fields
            ), "Initial partner fields should match expected fields"

            cached_result = await partner_service.get_partner_fields()
            assert (
                cached_result == expected_fields
            ), "Cached partner fields should match expected fields"
            PartnerORM.get_partner_fields.assert_called_once(), "get_partner_fields should be called only once due to caching"

    def test_create_partner_process_other_fields(self, partner_service):
        validation = {
            "field1": "value1",
            "field2": {"key": "value"},
            "field3": ["item1", "item2"],
            "field4": "value4",
        }
        mapping = "field1: map1 field2: map2 field3: map3"
        partner_fields = ["field1", "field2", "field3"]

        result = partner_service.create_partner_process_other_fields(
            validation, mapping, partner_fields
        )

        assert result["field1"] == "value1", "Simple field mapping should be preserved"
        assert "field2" in result, "Complex field should be included"
        assert "field3" in result, "Array field should be included"
        assert "field4" not in result, "Unmapped field should be excluded"
        assert isinstance(
            result["field2"], str
        ), "Complex field should be converted to string"
        assert isinstance(
            result["field3"], str
        ), "Array field should be converted to string"

    @pytest.mark.asyncio
    async def test_update_partner_info(self, partner_service):
        session_mock = AsyncMock()
        partner_id = "123"
        data = {
            "name": "New Name",
            "email": "new@example.com",
            "invalid_field": "value",
        }

        with patch.object(
            PartnerORM, "get_partner_fields", return_value=["name", "email"]
        ):
            updated = await partner_service.update_partner_info(
                partner_id, data, session_mock
            )

            assert "name" in updated, "Valid field 'name' should be included in update"
            assert (
                "email" in updated
            ), "Valid field 'email' should be included in update"
            assert (
                "invalid_field" not in updated
            ), "Invalid field should be excluded from update"
            session_mock.execute.assert_called_once(), "Session execute should be called once"
            session_mock.commit.assert_called_once(), "Session commit should be called once"
