# ruff: noqa: E402

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer

from .controllers.program_controller import ProgramController
from .controllers.form_controller import FormController
class Initializer(Initializer):
    def initialize(self, **kwargs):
        super().initialize()
        # Initialize all Services, Controllers, any utils here.

        ProgramController().post_init()
        FormController().post_init()
