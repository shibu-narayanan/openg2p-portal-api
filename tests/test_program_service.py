from datetime import datetime
from unittest.mock import MagicMock

import pytest
from openg2p_portal_api.models.orm.program_orm import ProgramORM
from openg2p_portal_api.models.orm.program_registrant_info_orm import (
    ProgramRegistrantInfoORM,
)
from openg2p_portal_api.services.program_service import ProgramService

TEST_DATA = {
    "PROGRAM": {
        "ID": 1,
        "PARTNER_ID": 1,
        "NAME": "Test Program",
        "DESC": "Description of the program",
        "CREATE_DATE": datetime(2024, 1, 1),
        "SELF_SERVICE_PORTAL_FORM": True,
        "IS_MULTIPLE_FORM_SUBMISSION": False,
    },
    "STATUS": {
        "NOT_APPLIED": "Not Applied",
        "ACTIVE": "active",
        "NO_APPLICATION": "Not submitted any application",
    },
    "ERROR": {"PROGRAM_NOT_FOUND": "Program with ID 1 not found."},
    "TEST": {
        "KEYWORD": "Test",
        "NONEXISTENT": "NonExistent",
        "BENEFIT": "Test Benefit",
        "APPLICATION": "Test Application",
    },
}


@pytest.fixture
def program_mock():
    program = MagicMock()
    program.id = TEST_DATA["PROGRAM"]["ID"]
    program.name = TEST_DATA["PROGRAM"]["NAME"]
    program.description = TEST_DATA["PROGRAM"]["DESC"]
    program.create_date = TEST_DATA["PROGRAM"]["CREATE_DATE"]
    program.self_service_portal_form = TEST_DATA["PROGRAM"]["SELF_SERVICE_PORTAL_FORM"]
    program.is_multiple_form_submission = TEST_DATA["PROGRAM"][
        "IS_MULTIPLE_FORM_SUBMISSION"
    ]
    program.membership = []
    program.configure_mock(
        **{
            "program_name": TEST_DATA["PROGRAM"]["NAME"],
            "enrollment_status": TEST_DATA["STATUS"]["ACTIVE"],
            "application_status": TEST_DATA["STATUS"]["ACTIVE"],
        }
    )
    return program


@pytest.fixture
def program_reg_info_mock():
    reg_info = MagicMock()
    reg_info.partner_id = TEST_DATA["PROGRAM"]["PARTNER_ID"]
    reg_info.state = TEST_DATA["STATUS"]["ACTIVE"]
    return reg_info


class TestProgramService:
    @pytest.mark.asyncio
    async def test_get_all_programs_empty_result(self, mocker):
        mocker.patch.object(ProgramORM, "get_all_programs", return_value=[])
        program_service = ProgramService()
        programs = await program_service.get_all_program_service(
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"]
        )
        assert programs == [], "Expected empty list when no programs are found"

    @pytest.mark.asyncio
    async def test_get_all_programs_success(self, mocker, program_mock):
        mocker.patch.object(ProgramORM, "get_all_programs", return_value=[program_mock])
        program_service = ProgramService()
        programs = await program_service.get_all_program_service(
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"]
        )
        assert len(programs) == 1, "Expected exactly one program in response"
        assert (
            programs[0].id == TEST_DATA["PROGRAM"]["ID"]
        ), "Program ID does not match expected value"
        assert (
            programs[0].name == TEST_DATA["PROGRAM"]["NAME"]
        ), "Program name does not match expected value"
        assert (
            programs[0].create_date == TEST_DATA["PROGRAM"]["CREATE_DATE"]
        ), "Program create date does not match expected value"
        assert (
            programs[0].self_service_portal_form
            == TEST_DATA["PROGRAM"]["SELF_SERVICE_PORTAL_FORM"]
        ), "Self service portal form flag does not match expected value"
        assert (
            programs[0].is_multiple_form_submission
            == TEST_DATA["PROGRAM"]["IS_MULTIPLE_FORM_SUBMISSION"]
        ), "Multiple form submission flag does not match expected value"

    @pytest.mark.asyncio
    async def test_get_all_programs_with_membership(
        self, mocker, program_mock, program_reg_info_mock
    ):
        program_mock.membership = [program_reg_info_mock]
        mocker.patch.object(ProgramORM, "get_all_programs", return_value=[program_mock])
        mocker.patch.object(
            ProgramRegistrantInfoORM,
            "get_latest_reg_info",
            return_value=program_reg_info_mock,
        )

        program_service = ProgramService()
        programs = await program_service.get_all_program_service(
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"]
        )

        assert len(programs) == 1, "Expected exactly one program in response"
        assert programs[0].has_applied is True, "Program should be marked as applied"
        assert (
            programs[0].state == TEST_DATA["STATUS"]["ACTIVE"]
        ), "Program state should be active"
        assert (
            programs[0].last_application_status == TEST_DATA["STATUS"]["ACTIVE"]
        ), "Last application status should be active"

    @pytest.mark.asyncio
    async def test_get_program_by_id_with_membership(
        self, mocker, program_mock, program_reg_info_mock
    ):
        program_mock.membership = [program_reg_info_mock]
        mocker.patch.object(
            ProgramORM, "get_all_by_program_id", return_value=program_mock
        )
        mocker.patch.object(
            ProgramRegistrantInfoORM,
            "get_latest_reg_info",
            return_value=program_reg_info_mock,
        )

        program_service = ProgramService()
        program = await program_service.get_program_by_id_service(
            programid=TEST_DATA["PROGRAM"]["ID"],
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"],
        )

        assert (
            program.id == TEST_DATA["PROGRAM"]["ID"]
        ), "Program ID does not match expected value"
        assert program.has_applied is True, "Program should be marked as applied"
        assert (
            program.state == TEST_DATA["STATUS"]["ACTIVE"]
        ), "Program state should be active"
        assert (
            program.last_application_status == TEST_DATA["STATUS"]["ACTIVE"]
        ), "Last application status should be active"

    @pytest.mark.asyncio
    async def test_get_program_by_id_no_membership(self, mocker, program_mock):
        program_mock.membership = []
        mocker.patch.object(
            ProgramORM, "get_all_by_program_id", return_value=program_mock
        )

        program_service = ProgramService()
        program = await program_service.get_program_by_id_service(
            programid=TEST_DATA["PROGRAM"]["ID"],
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"],
        )

        assert (
            program.id == TEST_DATA["PROGRAM"]["ID"]
        ), "Program ID does not match expected value"
        assert program.has_applied is False, "Program should be marked as not applied"
        assert (
            program.state == TEST_DATA["STATUS"]["NOT_APPLIED"]
        ), "Program state should be 'Not Applied'"
        assert (
            program.last_application_status == TEST_DATA["STATUS"]["NO_APPLICATION"]
        ), "Last application status should be 'Not submitted any application'"

    @pytest.mark.asyncio
    async def test_get_program_by_id_not_found(self, mocker):
        mocker.patch.object(ProgramORM, "get_all_by_program_id", return_value=None)

        program_service = ProgramService()
        result = await program_service.get_program_by_id_service(
            programid=TEST_DATA["PROGRAM"]["ID"],
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"],
        )
        assert result == {
            "message": TEST_DATA["ERROR"]["PROGRAM_NOT_FOUND"]
        }, "Should return appropriate error message when program not found"

    @pytest.mark.asyncio
    async def test_get_program_by_key_empty_result(self, mocker):
        mocker.patch.object(ProgramORM, "get_all_program_by_keyword", return_value=[])
        program_service = ProgramService()
        programs = await program_service.get_program_by_key_service(
            keyword=TEST_DATA["TEST"]["NONEXISTENT"]
        )
        assert programs == [], "Expected empty list when no programs match keyword"

    @pytest.mark.asyncio
    async def test_get_program_by_key_success(self, mocker, program_mock):
        mocker.patch.object(
            ProgramORM, "get_all_program_by_keyword", return_value=[program_mock]
        )
        program_service = ProgramService()
        programs = await program_service.get_program_by_key_service(
            keyword=TEST_DATA["TEST"]["KEYWORD"]
        )
        assert len(programs) == 1, "Expected exactly one program matching keyword"
        assert (
            programs[0].id == TEST_DATA["PROGRAM"]["ID"]
        ), "Program ID does not match expected value"
        assert (
            programs[0].name == TEST_DATA["PROGRAM"]["NAME"]
        ), "Program name does not match expected value"

    @pytest.mark.asyncio
    async def test_get_program_summary(self, mocker, program_mock):
        mocker.patch.object(
            ProgramORM, "get_program_summary", return_value=[program_mock]
        )
        program_service = ProgramService()
        summaries = await program_service.get_program_summary_service(
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"]
        )
        assert len(summaries) == 1, "Expected exactly one program summary"
        assert (
            summaries[0].program_name == TEST_DATA["PROGRAM"]["NAME"]
        ), "Program name in summary does not match expected value"

    @pytest.mark.asyncio
    async def test_get_application_details(self, mocker, program_mock):
        mocker.patch.object(
            ProgramORM, "get_application_details", return_value=[program_mock]
        )
        program_service = ProgramService()
        details = await program_service.get_application_details_service(
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"]
        )
        assert len(details) == 1, "Expected exactly one application detail"
        assert (
            details[0].application_id == TEST_DATA["PROGRAM"]["ID"]
        ), "Application ID does not match expected value"

    @pytest.mark.asyncio
    async def test_get_benefit_details(self, mocker, program_mock):
        mocker.patch.object(
            ProgramORM, "get_benefit_details", return_value=[program_mock]
        )
        program_service = ProgramService()
        benefits = await program_service.get_benefit_details_service(
            partnerid=TEST_DATA["PROGRAM"]["PARTNER_ID"]
        )
        assert len(benefits) == 1, "Expected exactly one benefit detail"
        assert (
            benefits[0].entitlement_reference_number == TEST_DATA["PROGRAM"]["ID"]
        ), "Entitlement reference number does not match expected value"
