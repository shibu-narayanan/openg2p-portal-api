from unittest.mock import AsyncMock, patch

import pytest
from openg2p_portal_api.controllers.program_controller import ProgramController
from openg2p_portal_api.models.credentials import AuthCredentials

MOCK_PROGRAM_SUMMARY = [
    {
        "program_name": "Program 1",
        "enrollment_status": "Enrolled",
        "total_funds_awaited": 1000,
        "total_funds_received": 500,
    }
]


class TestProgramController:
    @pytest.mark.asyncio
    async def test_get_program_summary(self):
        mock_auth_credentials = AuthCredentials(partner_id=42)

        with patch(
            "openg2p_portal_api.dependencies.JwtBearerAuth", return_value=AsyncMock()
        ) as mock_jwt_auth:
            #  patch.object(ProgramService, 'get_program_summary_service', new_callable=AsyncMock) as mock_summary_service:

            mock_jwt_auth().return_value = mock_auth_credentials
            # mock_summary_service.return_value = MOCK_PROGRAM_SUMMARY

            controller = ProgramController()

            response = await controller.get_program_summary(mock_auth_credentials)

            assert response == MOCK_PROGRAM_SUMMARY


if __name__ == "__main__":
    pytest.main([__file__])


# import pytest
# import asyncio
# from unittest.mock import patch
# from openg2p_portal_api.services.program_service import ProgramService

# MOCK_PROGRAM_SUMMARY = [
#     {
#         "program_name": "Program 1",
#         "enrollment_status": "Enrolled",
#         "total_funds_awaited": 1000,
#         "total_funds_received": 500
#     }
# ]
# EXPECTED_RESULT = [
#     {
#         "program_name": "Program 1",
#         "enrollment_status": "Enrolled",
#         "total_funds_awaited": 1000,
#         "total_funds_received": 500
#     }
# ]

# class TestProgramService:
#     @pytest.mark.asyncio
#     async def test_get_program_summary_service(self):
#         with patch('openg2p_portal_api.models.orm.program_orm.ProgramORM.get_program_summary',
#                    return_value=MOCK_PROGRAM_SUMMARY):
#             service = ProgramService()
#             result = await service.get_program_summary_service(partnerid=42)
#             result_as_dicts = [obj.__dict__ for obj in result]
#             assert result_as_dicts == EXPECTED_RESULT

# if __name__ == "__main__":
#     asyncio.run(TestProgramService().test_get_program_summary_service())
