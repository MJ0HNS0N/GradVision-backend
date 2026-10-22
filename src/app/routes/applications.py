from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Application as ApplicationModel

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("user/{id}", response_model=list[ApplicationModel])
def get_user_applications(
    id: int,
    db: Session = Depends(get_db),
) -> list[ApplicationModel]:
    applications = db.query(ApplicationModel).filter(ApplicationModel.user_id == id).all()
    if not applications:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No applications found for this user",
        )
    return applications

@router.patch("/user/{id}", response_model=ApplicationModel)
def update_application(
    id: int,
    application_in: ApplicationModel,
    db: Session = Depends(get_db),
) -> ApplicationModel:
    application = db.query(ApplicationModel).filter(ApplicationModel.application_id == id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    for key, value in application_in.dict(exclude_unset=True).items():
        setattr(application, key, value)
    db.commit()
    db.refresh(application)
    return application

@router.delete("/{id}", response_model=dict)
def delete_application(
    id: int,
    db: Session = Depends(get_db),
) -> dict:
    application = db.query(ApplicationModel).filter(ApplicationModel.application_id == id).first()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    db.delete(application)
    db.commit()
    return {"detail": "Application deleted successfully"}

@router.post("", response_model=ApplicationModel, status_code=status.HTTP_201_CREATED)
def create_application(
    application_in: ApplicationModel,
    db: Session = Depends(get_db),
) -> ApplicationModel:
    application = ApplicationModel(**application_in.dict())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application
