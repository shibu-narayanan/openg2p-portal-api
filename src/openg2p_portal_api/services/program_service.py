from openg2p_fastapi_common.service import BaseService

from ..models.orm.program_orm import ProgramORM
from ..models.orm.program_registrant_info_orm import ProgramRegistrantInfoORM
from ..models.program import Program


class ProgramService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def get_all_program_service(self, partnerid: int):
        program_list = []
        res = await ProgramORM.get_all_programs()

        if res:
            for program in res:
                response_dict = {
                    "id": program.id,
                    "name": program.name,
                    "description": program.description,
                    "state": "Not Applied",
                    "has_applied": False,
                    "self_service_portal_form": program.self_service_portal_form,
                    "is_multiple_form_submission": program.is_multiple_form_submission,
                    "last_application_status": "Not submitted any application",
                }
                membership = program.membership
                if membership:
                    for member in membership:
                        if member.partner_id == partnerid:
                            response_dict.update(
                                {"state": member.state, "has_applied": True}
                            )
                            latest_reg_info = (
                                await ProgramRegistrantInfoORM.get_latest_reg_info(
                                    member.id
                                )
                            )
                            if latest_reg_info:
                                response_dict[
                                    "last_application_status"
                                ] = latest_reg_info.state

                program_list.append(Program(**response_dict))

        return program_list

    async def get_program_by_id_service(self, programid: int, partnerid: int):
        res = await ProgramORM.get_all_by_program_id(programid)

        response_dict = {
            "id": res.id,
            "name": res.name,
            "description": res.description,
            "state": "Not Applied",
            "has_applied": False,
            "self_service_portal_form": res.self_service_portal_form,
            "is_multiple_form_submission": res.is_multiple_form_submission,
            "last_application_status": "Not submitted any application",
        }

        if res:
            membership = res.membership
            if membership:
                for member in membership:
                    if member.partner_id == partnerid:
                        response_dict.update(
                            {
                                "state": member.state,
                                "has_applied": True,
                            }
                        )
                        latest_reg_info = (
                            await ProgramRegistrantInfoORM.get_latest_reg_info(
                                member.id
                            )
                        )
                        if latest_reg_info:
                            response_dict[
                                "last_application_status"
                            ] = latest_reg_info.state

                        break

            return Program(**response_dict)
        else:
            # TODO: Add error handling
            pass

    async def get_program_by_key_service(self, keyword: str, partnerid: int):
        program_list = []
        res = await ProgramORM.get_all_program_by_keyword(keyword)

        if res:
            for program in res:
                response_dict = {
                    "id": program.id,
                    "name": program.name,
                    "description": program.description,
                    "state": "Not Applied",
                    "has_applied": False,
                    "self_service_portal_form": program.self_service_portal_form,
                    "is_multiple_form_submission": program.is_multiple_form_submission,
                    "last_application_status": "Not submitted any application",
                }
                membership = program.membership
                if membership:
                    for member in membership:
                        if member.partner_id == partnerid:
                            response_dict.update(
                                {"state": member.state, "has_applied": True}
                            )
                            latest_reg_info = (
                                await ProgramRegistrantInfoORM.get_latest_reg_info(
                                    member.id
                                )
                            )
                            if latest_reg_info:
                                response_dict[
                                    "last_application_status"
                                ] = latest_reg_info.state

                program_list.append(Program(**response_dict))
        return program_list
