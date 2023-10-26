from openg2p_fastapi_common.controller import BaseController

from ..config import Settings
from ..models.form import ProgramForm, ProgramRegistrantInfo
from ..models.orm.program_orm import ProgramORM
from ..services.form_service import FormService

_config = Settings.get_config()


class FormController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._form_service = FormService.get_component()

        self.router.add_api_route(
            "/form/{programid}",
            self.get_program_form,
            responses={200: {"model": ProgramForm}},
            methods=["GET"],
        )

        self.router.add_api_route(
            "/form/{programid}",
            self.update_form_draft,
            responses={200: {"model": ProgramForm}},
            methods=["PUT"],
        )

        self.router.add_api_route(
            "/form/{programid}",
            self.crate_new_form_draft,
            responses={200: {"model": ProgramForm}},
            methods=["POST"],
        )

        self.router.add_api_route(
            "/form/{programid}/submit",
            self.submit_form,
            responses={200: {"model": ProgramForm}},
            methods=["POST"],
        )

    @property
    def form_service(self):
        if not self._form_service:
            self._form_service = FormService.get_component()
        return self._form_service

    async def get_program_form(self, programid: int):
        response_dict = {}
        res = await ProgramORM.get_program_form(programid)
        if res:
            form = res.form
            if form:
                response_dict = {
                    "id": form.id,
                    "program_id": res.id,
                    "schema": form.schema,
                    "submission_data": None,
                    "program_name": res.name,
                    "program_description": res.description,
                }
            else:
                response_dict = {
                    "id": None,
                    "program_id": res.id,
                    "schema": None,
                    "submission_data": None,
                    "program_name": res.name,
                    "program_description": res.description,
                }
            return ProgramForm(**response_dict)
        else:
            # TODO: Add error handling
            pass

    async def update_form_draft(self, programreginfo: ProgramRegistrantInfo):
        return "form data updated!!"

    async def crate_new_form_draft(
        self, programid: int, programreginfo: ProgramRegistrantInfo
    ):
        return "Successfully saved the draft"

    async def submit_form(self, programid: int, programreginfo: ProgramRegistrantInfo):
        state = "active"
        registrant_id = 46

        return await FormService.create_new_form_draft(
            self, programid, programreginfo, state, registrant_id
        )
