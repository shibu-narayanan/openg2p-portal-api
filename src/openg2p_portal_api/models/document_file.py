from fastapi import File, UploadFile
from pydantic import BaseModel, Field, constr
from typing import List, Dict, Any

class DocumentFile(BaseModel):
    name: str 
    backend_id: int 
    
    class Config:
        from_attributes = True
