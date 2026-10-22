"""Database operations for program catalog rows."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.models import Program as ProgramModel


def get_program_by_id(db: Session, program_id: int) -> ProgramModel | None:
    return db.execute(
        select(ProgramModel)
        .where(ProgramModel.program_id == program_id)
        .options(selectinload(ProgramModel.university))
    ).scalar_one_or_none()
