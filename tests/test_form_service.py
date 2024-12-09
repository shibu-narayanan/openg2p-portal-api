from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from openg2p_portal_api.models.form import ProgramForm
from openg2p_portal_api.models.orm.program_orm import ProgramORM
from openg2p_portal_api.models.orm.program_registrant_info_orm import (
    ProgramRegistrantInfoDraftORM,
)
from openg2p_portal_api.services.form_service import FormService

TEST_DATA = {
    "PROGRAM_ID": 1,
    "REGISTRANT_ID": 1,
    "MOCK_PROGRAM_NAME": "Test Program",
    "MOCK_PROGRAM_DESCRIPTION": "Test Description",
    "MOCK_EMAIL": "test@example.com",
    "MOCK_USER_NAME": "Test User",
}


@pytest.fixture
def form_service():
    service = FormService()
    service.membership_service = MagicMock()
    service.partner_service = MagicMock()
    return service


class TestFormService:
    @pytest.mark.asyncio
    async def test_get_program_form_success(self, form_service):
        program_id = TEST_DATA["PROGRAM_ID"]
        registrant_id = TEST_DATA["REGISTRANT_ID"]
        mock_program = MagicMock()
        mock_program.id = program_id
        mock_program.name = TEST_DATA["MOCK_PROGRAM_NAME"]
        mock_program.description = TEST_DATA["MOCK_PROGRAM_DESCRIPTION"]
        mock_program.form.id = 1
        mock_program.form.schema = '{"fields": []}'

        ProgramORM.get_program_form = AsyncMock(return_value=mock_program)
        ProgramRegistrantInfoDraftORM.get_draft_reg_info_by_id = AsyncMock(
            return_value=None
        )

        result = await form_service.get_program_form(program_id, registrant_id)

        assert isinstance(
            result, ProgramForm
        ), "Result should be a ProgramForm instance"
        assert result.program_id == program_id, "Program ID should match"
        assert (
            result.program_name == TEST_DATA["MOCK_PROGRAM_NAME"]
        ), "Program name should match"
        assert (
            result.program_description == TEST_DATA["MOCK_PROGRAM_DESCRIPTION"]
        ), "Program description should match"

    @pytest.mark.asyncio
    async def test_get_program_form_not_found(self, form_service):
        program_id = 999
        registrant_id = TEST_DATA["REGISTRANT_ID"]
        ProgramORM.get_program_form = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await form_service.get_program_form(program_id, registrant_id)
        assert exc.value.status_code == 400, "Status code should be 400"
        assert exc.value.detail == "Program ID not Found", "Error detail should match"

    @pytest.mark.asyncio
    async def test_create_form_draft_new(self, form_service):
        program_id = TEST_DATA["PROGRAM_ID"]
        registrant_id = TEST_DATA["REGISTRANT_ID"]
        form_data = MagicMock()
        form_data.program_registrant_info = {
            "name": TEST_DATA["MOCK_USER_NAME"],
            "email": TEST_DATA["MOCK_EMAIL"],
        }

        ProgramRegistrantInfoDraftORM.get_draft_reg_info_by_id = AsyncMock(
            return_value=None
        )

        with patch("sqlalchemy.ext.asyncio.AsyncSession.commit") as mock_commit:
            result = await form_service.create_form_draft(
                program_id, form_data, registrant_id
            )
            assert (
                result == "Successfully submitted the draft!!"
            ), "Draft submission message should match"
            mock_commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_application_form_success(self, form_service):
        program_id = TEST_DATA["PROGRAM_ID"]
        registrant_id = TEST_DATA["REGISTRANT_ID"]
        form_data = MagicMock()
        form_data.program_registrant_info = {
            "name": TEST_DATA["MOCK_USER_NAME"],
            "email": TEST_DATA["MOCK_EMAIL"],
        }

        mock_program = MagicMock(is_multiple_form_submission=True)

        ProgramRegistrantInfoDraftORM.get_draft_reg_info_by_id = AsyncMock(
            return_value=None
        )
        form_service.membership_service.check_and_create_mem = AsyncMock(
            return_value=123
        )
        form_service.partner_service.update_partner_info = AsyncMock(
            return_value=["name"]
        )

        with patch("sqlalchemy.ext.asyncio.AsyncSession.get") as mock_get, patch(
            "sqlalchemy.ext.asyncio.AsyncSession.execute"
        ) as mock_execute, patch("sqlalchemy.ext.asyncio.AsyncSession.commit"):
            mock_get.return_value = mock_program
            mock_execute.return_value = MagicMock(
                scalars=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=None))
                )
            )

            result = await form_service.submit_application_form(
                program_id, form_data, registrant_id
            )

        assert (
            "Successfully applied into the program! Application ID:" in result
        ), "Application submission message should match"
        assert len(result.split()[-1]) == 11, "Application ID length should be 11"
        form_service.membership_service.check_and_create_mem.assert_called_once_with(
            program_id, registrant_id
        )
        form_service.partner_service.update_partner_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_application_form_multiple_not_allowed(self, form_service):
        program_id = TEST_DATA["PROGRAM_ID"]
        registrant_id = TEST_DATA["REGISTRANT_ID"]
        form_data = MagicMock()
        form_data.program_registrant_info = {"name": TEST_DATA["MOCK_USER_NAME"]}

        mock_program = MagicMock(is_multiple_form_submission=False)
        mock_application = MagicMock()
        mock_result = MagicMock(
            scalars=MagicMock(
                return_value=MagicMock(first=MagicMock(return_value=mock_application))
            )
        )

        with patch("sqlalchemy.ext.asyncio.AsyncSession.get") as mock_get, patch(
            "sqlalchemy.ext.asyncio.AsyncSession.execute"
        ) as mock_execute:
            mock_get.return_value = mock_program
            mock_execute.return_value = mock_result

            result = await form_service.submit_application_form(
                program_id, form_data, registrant_id
            )

        assert (
            result
            == "Error: Multiple form submissions are not allowed for this program."
        ), "Error message for multiple submissions should match"

    def test_compute_application_id(self, form_service):
        today = datetime.today()
        expected_prefix = today.strftime("%d%m%y")

        result = form_service._compute_application_id()

        assert result.startswith(
            expected_prefix
        ), "Application ID should start with today's date"
        assert len(result) == 11, "Application ID length should be 11"

    def test_clean_program_registrant_info(self, form_service):
        program_info = {"name": "Test", "email": TEST_DATA["MOCK_EMAIL"], "age": 25}
        updated_fields = ["name", "email"]

        result = form_service.clean_program_registrant_info(
            program_info, updated_fields
        )

        assert "name" not in result, "Name should be removed from result"
        assert "email" not in result, "Email should be removed from result"
        assert result == {"age": 25}, "Result should only contain age"

    def test_clean_program_registrant_info_empty(self, form_service):
        program_info = {}
        updated_fields = ["name", "email"]

        result = form_service.clean_program_registrant_info(
            program_info, updated_fields
        )
        assert result == {}, "Result should be empty"

    def test_clean_program_registrant_info_no_updates(self, form_service):
        program_info = {"name": "Test", "email": TEST_DATA["MOCK_EMAIL"]}
        updated_fields = []

        result = form_service.clean_program_registrant_info(
            program_info, updated_fields
        )
        assert result == program_info, "Result should match original program info"
