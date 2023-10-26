from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..models.orm.program_registrant_info_orm import ProgramRegistrantInfoORM
from .membership_service import MembershipService


class FormService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.membership_service = MembershipService.get_component()

    async def create_new_form_draft(
        self, program_id: int, form_data, state: str, registrant_id: int
    ):
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            program_membership_id = await MembershipService.check_and_create_mem(
                self, program_id, registrant_id
            )
            program_registrant_info = ProgramRegistrantInfoORM(
                program_id=program_id,
                program_membership_id=program_membership_id,
                program_registrant_info=form_data.program_registrant_info,
                state=state,
                registrant_id=registrant_id,
            )

            try:
                session.add(program_registrant_info)

                await session.commit()
            except IntegrityError:
                return "Error: Duplicate entry or integrity violation"

        return "Successfully submitted the draft!!"
