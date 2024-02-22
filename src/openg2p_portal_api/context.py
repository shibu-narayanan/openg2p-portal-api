from contextvars import ContextVar
from typing import Any, Dict

auth_id_type_config_cache: ContextVar[Dict[str, Any]] = ContextVar(
    "auth_id_type_config_cache", default={}
)
