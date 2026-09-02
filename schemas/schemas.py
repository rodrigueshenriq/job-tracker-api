
from pydantic import BaseModel
from typing import Optional

class ApplicationCreate(BaseModel):
    company: str
    position: str
    status: Optional[str] = "applied"
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class ApplicationOut(ApplicationCreate):
    id: int
    class Config:
        orm_mode = True
