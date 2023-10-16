#!/usr/bin/env python3

# ruff: noqa: I001

from openg2p_fastapi_common.context import config_registry
from openg2p_portal_api.app import Initializer

main_init = Initializer()
print(config_registry.get())
main_init.main()
