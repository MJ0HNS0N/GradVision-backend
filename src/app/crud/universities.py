from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.models import (
    Professor as ProfessorModel,
    Program as ProgramModel,
    University as UniversityModel,
)


def search_universities(
    db: Session,
    location: str | None = None,
    search: str | None = None,
    program_fields: list[str] | None = None,
    limit: int = 50,
    offset: int = 0,
):
    query = (
        select(UniversityModel)
        .options(
            selectinload(UniversityModel.programs),
            selectinload(UniversityModel.professors),
        )
    )

    if location:
        query = query.where(UniversityModel.location == location)

    if search:
        query = query.where(
            UniversityModel.university_name.ilike(f"%{search}%")
        )

    if program_fields:
        query = (
            query.join(UniversityModel.programs)
            .where(ProgramModel.field.in_(program_fields))
            .distinct()
        )

    universities = db.execute(
        query.offset(offset).limit(limit)
    ).scalars().all()

    return [
        {
            "university_id": university.university_id,
            "university_name": university.university_name,
            "location": university.location,
            "program_count": len(university.programs),
            "professor_count": len(university.professors),
        }
        for university in universities
    ]


def get_professors(
    db: Session,
    university_id: int,
):
    return list(
        db.execute(
            select(ProfessorModel).where(
                ProfessorModel.university_id == university_id
            )
        ).scalars()
    )