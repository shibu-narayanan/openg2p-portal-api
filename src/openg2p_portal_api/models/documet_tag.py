from pydantic import BaseModel
class DocumentTag(BaseModel):
    id:int
    name: str

    class Config:
        from_attributes=True  

   