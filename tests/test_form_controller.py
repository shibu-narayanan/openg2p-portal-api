from unittest.mock import AsyncMock, MagicMock

import pytest
from openg2p_fastapi_common.errors.http_exceptions import (
    BadRequestError,
    UnauthorizedError,
)
from openg2p_portal_api.controllers.form_controller import FormController
from openg2p_portal_api.models.credentials import AuthCredentials
from openg2p_portal_api.models.form import ProgramForm, ProgramRegistrantInfo
from openg2p_portal_api.models.program import Program


@pytest.fixture
def mock_form_service():
    service = MagicMock()
    service.get_program_form = AsyncMock()
    service.create_form_draft = AsyncMock()
    service.submit_application_form = AsyncMock()
    return service


@pytest.fixture
def mock_program_service():
    service = MagicMock()
    service.get_program_by_id_service = AsyncMock()
    return service


@pytest.fixture
def form_controller(mock_form_service, mock_program_service):
    controller = FormController()
    controller._form_service = mock_form_service
    controller._program_service = mock_program_service
    return controller


@pytest.fixture
def auth_credentials():
    return AuthCredentials(partner_id=1, credentials="test_token")


@pytest.fixture
def program_registrant_info():
    return ProgramRegistrantInfo(name="Test User", email="test@example.com")


class TestFormController:
    @pytest.mark.asyncio
    async def test_get_program_form_success(self, form_controller, auth_credentials):
        program_id = 1
        expected_form = ProgramForm(id=1, program_id=program_id, status="draft")
        form_controller.form_service.get_program_form.return_value = expected_form

        result = await form_controller.get_program_form(program_id, auth_credentials)

        assert result == expected_form, "Retrieved form should match expected form"
        form_controller.form_service.get_program_form.assert_called_once_with(
            program_id, auth_credentials.partner_id
        ), "get_program_form should be called with correct parameters"

    @pytest.mark.asyncio
    async def test_get_program_form_unauthorized(self, form_controller):
        program_id = 1
        auth_credentials = AuthCredentials(partner_id=0, credentials="test_token")

        with pytest.raises(UnauthorizedError):
            await form_controller.get_program_form(program_id, auth_credentials)

    @pytest.mark.asyncio
    async def test_create_or_update_form_draft_success(
        self, form_controller, auth_credentials, program_registrant_info
    ):
        program_id = 1
        expected_form = ProgramForm(id=1, program_id=program_id, status="draft")
        form_controller.form_service.create_form_draft.return_value = expected_form

        result = await form_controller.create_or_update_form_draft(
            program_id, program_registrant_info, auth_credentials
        )

        assert result == expected_form, "Created draft form should match expected form"
        form_controller.form_service.create_form_draft.assert_called_once_with(
            program_id, program_registrant_info, auth_credentials.partner_id
        ), "create_form_draft should be called with correct parameters"

    @pytest.mark.asyncio
    async def test_create_or_update_form_draft_unauthorized(
        self, form_controller, program_registrant_info
    ):
        program_id = 1
        auth_credentials = AuthCredentials(partner_id=0, credentials="test_token")

        with pytest.raises(UnauthorizedError):
            await form_controller.create_or_update_form_draft(
                program_id, program_registrant_info, auth_credentials
            )

    @pytest.mark.asyncio
    async def test_submit_form_success(
        self, form_controller, auth_credentials, program_registrant_info
    ):
        program_id = 1
        expected_form = ProgramForm(id=1, program_id=program_id, status="submitted")
        Program(id=program_id, name="Test Program", is_portal_form_mapped=True)
        form_controller.form_service.submit_application_form.return_value = (
            expected_form
        )

        result = await form_controller.submit_form(
            program_id, program_registrant_info, auth_credentials
        )

        assert result == expected_form, "Submitted form should match expected form"
        form_controller.program_service.get_program_by_id_service.assert_called_once_with(
            program_id, auth_credentials.partner_id
        ), "get_program_by_id_service should be called with correct parameters"
        form_controller.form_service.submit_application_form.assert_called_once_with(
            program_id, program_registrant_info, auth_credentials.partner_id
        ), "submit_application_form should be called with correct parameters"

    @pytest.mark.asyncio
    async def test_submit_form_unauthorized(
        self, form_controller, program_registrant_info
    ):
        program_id = 1
        auth_credentials = AuthCredentials(partner_id=0, credentials="test_token")

        with pytest.raises(UnauthorizedError):
            await form_controller.submit_form(
                program_id, program_registrant_info, auth_credentials
            )

    @pytest.mark.asyncio
    async def test_submit_form_not_mapped(
        self, form_controller, auth_credentials, program_registrant_info
    ):
        program_id = 1
        program = Program(
            id=program_id, name="Test Program", is_portal_form_mapped=False
        )
        form_controller.program_service.get_program_by_id_service.return_value = program

        with pytest.raises(BadRequestError):
            await form_controller.submit_form(
                program_id, program_registrant_info, auth_credentials
            )

    @pytest.mark.asyncio
    async def test_get_program_form_not_found(self, form_controller, auth_credentials):
        program_id = 1
        form_controller.form_service.get_program_form.side_effect = BadRequestError(
            code="G2P-REQ-400", message="Program ID not Found", http_status_code=400
        )

        with pytest.raises(BadRequestError) as exc:
            await form_controller.get_program_form(program_id, auth_credentials)
        assert (
            exc.value.message == "Program ID not Found"
        ), "Should raise BadRequestError with correct message"

    @pytest.mark.asyncio
    async def test_submit_form_draft_error(
        self, form_controller, auth_credentials, program_registrant_info
    ):
        program_id = 1
        form_controller.form_service.create_form_draft.side_effect = BadRequestError(
            code="G2P-REQ-400",
            message="Error: In creating the draft",
            http_status_code=400,
        )

        with pytest.raises(BadRequestError) as exc:
            await form_controller.create_or_update_form_draft(
                program_id, program_registrant_info, auth_credentials
            )
        assert (
            exc.value.message == "Error: In creating the draft"
        ), "Should raise BadRequestError with correct message"
