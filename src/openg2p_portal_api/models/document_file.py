from fastapi import File, UploadFile
from pydantic import BaseModel, ConfigDict, Field, validator, constr
from typing import List, Dict, Any

class DocumentFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str 
    backend_id: int 
    