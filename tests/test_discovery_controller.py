from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from openg2p_portal_api.controllers.discovery_controller import DiscoveryController
from openg2p_portal_api.models.program import ProgramBase
from openg2p_portal_api.services.program_service import ProgramService

TEST_DATA = {
    "PROGRAM_NAME": "Test Program",
    "PROGRAM_DESCRIPTION": "Test program description",
    "ORG_NAME": "Test Org",
    "KEYWORD": "test_program",
    "NONEXISTENT_KEYWORD": "nonexistent",
}


class TestDiscoveryController:
    @pytest.fixture
    def mock_program_service(self):
        return AsyncMock(spec=ProgramService)

    @pytest.fixture
    def discovery_controller(self, mock_program_service):
        with patch(
            "openg2p_portal_api.services.program_service.ProgramService.get_component",
            return_value=mock_program_service,
        ):
            controller = DiscoveryController()
        return controller

    @pytest.mark.asyncio
    async def test_get_program_by_keyword(
        self, discovery_controller, mock_program_service
    ):
        expected_response: List[ProgramBase] = [
            ProgramBase(
                id=1,
                name=TEST_DATA["PROGRAM_NAME"],
                description=TEST_DATA["PROGRAM_DESCRIPTION"],
                start_date="2024-01-01",
                end_date="2024-12-31",
                status="active",
                program_type="benefit",
                organization_id=1,
                organization_name=TEST_DATA["ORG_NAME"],
            )
        ]
        mock_program_service.get_program_by_key_service.return_value = expected_response

        response = await discovery_controller.get_program_by_keyword(
            keyword=TEST_DATA["KEYWORD"]
        )

        assert (
            response == expected_response
        ), f"Expected response to be {expected_response}"
        mock_program_service.get_program_by_key_service.assert_awaited_once_with(
            TEST_DATA["KEYWORD"]
        )

    @pytest.mark.asyncio
    async def test_get_program_by_keyword_empty_result(
        self, discovery_controller, mock_program_service
    ):
        mock_program_service.get_program_by_key_service.return_value = []

        response = await discovery_controller.get_program_by_keyword(
            keyword=TEST_DATA["NONEXISTENT_KEYWORD"]
        )

        assert response == [], "Expected response to be an empty list"
        mock_program_service.get_program_by_key_service.assert_awaited_once_with(
            TEST_DATA["NONEXISTENT_KEYWORD"]
        )

    @pytest.mark.asyncio
    async def test_program_service_property(
        self, discovery_controller, mock_program_service
    ):
        service = discovery_controller.program_service

        assert (
            service == mock_program_service
        ), "Expected program service to match the mock"
