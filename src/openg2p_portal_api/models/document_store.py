from pydantic import BaseModel, ConfigDict, field_validator
from typing import Dict, Any

class DocumentStore(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    is_public:bool
    name: str
    server_env_defaults: Dict[str, Any]

   
    @field_validator('server_env_defaults', mode='before')
    def validate_server_env_defaults(cls, v):
        if isinstance(v, str):
            try:
                import json
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Input should be a valid dictionary.")
        return v
