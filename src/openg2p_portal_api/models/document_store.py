from pydantic import BaseModel, field_validator
from typing import Dict, Any

class DocumentStore(BaseModel):
    is_public:bool
    name: str
    server_env_defaults: Dict[str, Any]

    class Config:
        from_attributes = True

   
    @field_validator('server_env_defaults', mode='before')
    def validate_server_env_defaults(cls, v):
        if isinstance(v, str):
            try:
                import json
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Input should be a valid dictionary.")
        return v
