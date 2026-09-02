
from sqlalchemy import Column, Integer, String
from database.database import Base

class JobApplication(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, index=True)
    position = Column(String, index=True)
    status = Column(String, index=True, default="applied")
    notes = Column(String, nullable=True)
