from unittest.mock import AsyncMock, MagicMock

import pytest
from openg2p_portal_api.controllers.program_controller import ProgramController
from openg2p_portal_api.models.credentials import AuthCredentials
from openg2p_portal_api.models.program import (
    ApplicationDetails,
    BenefitDetails,
    Program,
    ProgramSummary,
)
from openg2p_portal_api.services.program_service import ProgramService

TEST_DATA = {
    "PARTNER_ID": 1,
    "PROGRAM_ID": 1,
    "TOKEN": "test_token",
    "PROGRAM_NAME": "Test Program",
    "DATE": "2023-01-01",
}


@pytest.fixture
def mock_program_service():
    service = MagicMock(spec=ProgramService)
    service.get_all_program_service = AsyncMock()
    service.get_program_by_id_service = AsyncMock()
    service.get_program_summary_service = AsyncMock()
    service.get_application_details_service = AsyncMock()
    service.get_benefit_details_service = AsyncMock()
    return service


@pytest.fixture
def program_controller(mock_program_service):
    controller = ProgramController()
    controller._program_service = mock_program_service
    return controller


@pytest.fixture
def auth_credentials():
    return AuthCredentials(
        partner_id=TEST_DATA["PARTNER_ID"], credentials=TEST_DATA["TOKEN"]
    )


class TestProgramController:
    @pytest.mark.asyncio
    async def test_get_programs_success(self, program_controller, auth_credentials):
        expected_programs = [
            Program(id=TEST_DATA["PROGRAM_ID"], name=f"{TEST_DATA['PROGRAM_NAME']} 1"),
            Program(id=2, name=f"{TEST_DATA['PROGRAM_NAME']} 2"),
        ]
        program_controller.program_service.get_all_program_service.return_value = (
            expected_programs
        )
        result = await program_controller.get_programs(auth_credentials)
        assert result == expected_programs, "Should return list of programs as expected"
        program_controller.program_service.get_all_program_service.assert_called_once_with(
            auth_credentials.partner_id
        ), "Should call get_all_program_service with correct partner_id"

    @pytest.mark.asyncio
    async def test_get_program_by_id_success(
        self, program_controller, auth_credentials
    ):
        expected_program = Program(
            id=TEST_DATA["PROGRAM_ID"], name=TEST_DATA["PROGRAM_NAME"]
        )
        program_controller.program_service.get_program_by_id_service.return_value = (
            expected_program
        )
        result = await program_controller.get_program_by_id(
            TEST_DATA["PROGRAM_ID"], auth_credentials
        )
        assert result == expected_program, "Should return the expected program"
        program_controller.program_service.get_program_by_id_service.assert_called_once_with(
            TEST_DATA["PROGRAM_ID"], auth_credentials.partner_id
        ), "Should call get_program_by_id_service with correct program_id and partner_id"

    @pytest.mark.asyncio
    async def test_get_program_summary_success(
        self, program_controller, auth_credentials
    ):
        expected_summary = [
            ProgramSummary(
                program_name=f"{TEST_DATA['PROGRAM_NAME']} 1",
                enrollment_status="Active",
                total_funds_awaited=1000,
                total_funds_received=500,
            )
        ]
        program_controller.program_service.get_program_summary_service.return_value = (
            expected_summary
        )
        result = await program_controller.get_program_summary(auth_credentials)
        assert result == expected_summary, "Should return the expected program summary"
        program_controller.program_service.get_program_summary_service.assert_called_once_with(
            auth_credentials.partner_id
        ), "Should call get_program_summary_service with correct partner_id"

    @pytest.mark.asyncio
    async def test_get_application_details_success(
        self, program_controller, auth_credentials
    ):
        expected_details = [
            ApplicationDetails(
                program_name=f"{TEST_DATA['PROGRAM_NAME']} 1",
                application_id=TEST_DATA["PROGRAM_ID"],
                date_applied=TEST_DATA["DATE"],
                application_status="Pending",
            )
        ]
        program_controller.program_service.get_application_details_service.return_value = (
            expected_details
        )
        result = await program_controller.get_application_details(auth_credentials)
        assert (
            result == expected_details
        ), "Should return the expected application details"
        program_controller.program_service.get_application_details_service.assert_called_once_with(
            auth_credentials.partner_id
        ), "Should call get_application_details_service with correct partner_id"

    @pytest.mark.asyncio
    async def test_get_benefit_details_success(
        self, program_controller, auth_credentials
    ):
        expected_details = [
            BenefitDetails(
                program_name=f"{TEST_DATA['PROGRAM_NAME']} 1",
                enrollment_status="Active",
                funds_awaited=1000,
                funds_received=500,
                entitlement_ref_no=TEST_DATA["PROGRAM_ID"],
            )
        ]
        program_controller.program_service.get_benefit_details_service.return_value = (
            expected_details
        )
        result = await program_controller.get_benefit_details(auth_credentials)
        assert result == expected_details, "Should return the expected benefit details"
        program_controller.program_service.get_benefit_details_service.assert_called_once_with(
            auth_credentials.partner_id
        ), "Should call get_benefit_details_service with correct partner_id"

    @pytest.mark.asyncio
    async def test_get_programs_error(self, program_controller, auth_credentials):
        program_controller.program_service.get_all_program_service.side_effect = (
            Exception("Failed to fetch programs from database")
        )

        with pytest.raises(Exception) as exc_info:
            await program_controller.get_programs(auth_credentials)

        assert (
            str(exc_info.value) == "Failed to fetch programs from database"
        ), "Should raise exception with appropriate error message"

    @pytest.mark.asyncio
    async def test_get_program_by_id_error(self, program_controller, auth_credentials):
        program_controller.program_service.get_program_by_id_service.side_effect = (
            Exception("Program not found in database")
        )

        with pytest.raises(Exception) as exc_info:
            await program_controller.get_program_by_id(
                TEST_DATA["PROGRAM_ID"], auth_credentials
            )

        assert (
            str(exc_info.value) == "Program not found in database"
        ), "Should raise exception when program is not found"
