from openg2p_fastapi_common.controller import BaseController

from ..config import Settings
from ..models.form import ProgramForm
from ..models.orm.program_orm import ProgramORM

_config = Settings.get_config()


class FormController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.router.add_api_route(
            "/form/{programid}",
            self.get_program_form,
            responses={200: {"model": ProgramForm}},
            methods=["GET"],
        )

        self.router.add_api_route(
            "/form/{programid}",
            self.update_form_data,
            responses={200: {"model": ProgramForm}},
            methods=["PUT"],
        )

        self.router.add_api_route(
            "/form/{programid}",
            self.crate_new_form_draft,
            responses={200: {"model": ProgramForm}},
            methods=["POST"],
        )

    async def get_program_form(self, programid: int):
        response_dict = {}
        res = await ProgramORM.get_program_form(programid)
        if res:
            form = res.form
            if form:
                response_dict = {
                    "id": form.id,
                    "schema": form.schema,
                    "program_id": res.id,
                    "submission_data": None,
                    "name": res.name,
                    "description": res.description,
                }
            else:
                response_dict = {
                    "id": None,
                    "schema": None,
                    "program_id": res.id,
                    "submission_data": None,
                    "name": res.name,
                    "description": res.description,
                }
            return ProgramForm(**response_dict)
        else:
            # TODO: Add error handling
            pass

    async def update_form_data(self, programid: int):
        return "form data updated!!"

    async def crate_new_form_draft(self, programid: int):
        return "Successfully submitted the draft!!"
