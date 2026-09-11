
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from models.models import JobApplication
from schemas.schemas import ApplicationCreate, ApplicationUpdate, ApplicationOut
from database.database import get_db

router = APIRouter()

@router.post("/", response_model=ApplicationOut)
def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    db_app = JobApplication(**application.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

@router.get("/", response_model=List[ApplicationOut])
def read_applications(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(JobApplication).offset(skip).limit(limit).all()

@router.get("/{application_id}", response_model=ApplicationOut)
def read_application(application_id: int, db: Session = Depends(get_db)):
    app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.put("/{application_id}", response_model=ApplicationOut)
def update_application(application_id: int, application: ApplicationUpdate, db: Session = Depends(get_db)):
    db_app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    for key, value in application.dict(exclude_unset=True).items():
        setattr(db_app, key, value)
    db.commit()
    db.refresh(db_app)
    return db_app

@router.delete("/{application_id}", response_model=dict)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    db_app = db.query(JobApplication).filter(JobApplication.id == application_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(db_app)
    db.commit()
    return {"detail": "Application deleted"}
