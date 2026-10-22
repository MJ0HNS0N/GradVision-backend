from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
import app.crud
from app.schemas.universities import UniversitySummary, ProfessorRead

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/universities", response_model=list[UniversitySummary])
def search_universities(
    user_id: int,
    location: str | None = None,
    program_type: str | None = None,
    db: Session = Depends(get_db),
):
    return app.crud.search_universities(
        db=db,
        user_id=user_id,
        location=location,
        program_type=program_type,
    )

@router.get("/professors", response_model=list[ProfessorRead])
def get_professors_endpoint(
    user_id: int,
    university_id: int,
    db: Session = Depends(get_db),
):
    professors = app.crud.get_professors(
        db=db,
        university_id=university_id,
        user_id=user_id,
    )

    if not professors:
        raise HTTPException(
            status_code=404,
            detail="No professors found for this university and user's interests",
        )

    return professors