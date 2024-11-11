from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openg2p_portal_api.models.orm.program_membership_orm import ProgramMembershipORM
from openg2p_portal_api.services.membership_service import MembershipService
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def mock_session():
    session = AsyncMock()
    async_session = AsyncMock()
    async_session.__aenter__.return_value = session
    async_session.__aexit__.return_value = None
    return session, async_session


@pytest.fixture
def mock_session_maker(mock_session):
    session, async_session = mock_session
    with patch(
        "openg2p_portal_api.services.membership_service.async_sessionmaker",
        return_value=lambda: async_session,
    ) as session_maker:
        yield session_maker


class TestMembershipService:
    @pytest.mark.asyncio
    async def test_check_and_create_mem_existing(self):
        service = MembershipService()
        mock_membership = MagicMock(id=1)

        with patch.object(
            ProgramMembershipORM,
            "get_membership_by_id",
            new_callable=AsyncMock,
            return_value=mock_membership,
        ):
            result = await service.check_and_create_mem(1, 1)
            assert (
                result == 1
            ), "Should return existing membership ID when membership already exists"

    @pytest.mark.asyncio
    async def test_check_and_create_mem_new_success(
        self, mock_session, mock_session_maker
    ):
        service = MembershipService()
        session, _ = mock_session

        with patch.object(
            ProgramMembershipORM,
            "get_membership_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            session.refresh = AsyncMock()

            await service.check_and_create_mem(1, 1)
            session.add.assert_called_once(), "Should add new membership to session"
            session.commit.assert_called_once(), "Should commit the new membership"
            session.refresh.assert_called_once(), "Should refresh the session after commit"

    @pytest.mark.asyncio
    async def test_check_and_create_mem_integrity_error(
        self, mock_session, mock_session_maker
    ):
        service = MembershipService()
        session, _ = mock_session

        with patch.object(
            ProgramMembershipORM,
            "get_membership_by_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            session.commit.side_effect = IntegrityError(None, None, None)

            result = await service.check_and_create_mem(1, 1)
            assert (
                result == "Could not add to registrant to program!!"
            ), "Should return error message when IntegrityError occurs"
