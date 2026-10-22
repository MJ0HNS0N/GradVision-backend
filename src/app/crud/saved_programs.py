"""Database operations for user saved (bookmarked) programs."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.models import Program as ProgramModel
from app.models.models import SavedProgram as SavedProgramModel


def get_saved_program(
    db: Session,
    user_id: int,
    program_id: int,
) -> SavedProgramModel | None:
    return db.execute(
        select(SavedProgramModel).where(
            SavedProgramModel.user_id == user_id,
            SavedProgramModel.program_id == program_id,
        )
    ).scalar_one_or_none()


def list_saved_programs(db: Session, user_id: int) -> list[ProgramModel]:
    rows = db.execute(
        select(SavedProgramModel)
        .where(SavedProgramModel.user_id == user_id)
        .options(
            selectinload(SavedProgramModel.program).selectinload(ProgramModel.university),
        )
    ).scalars().all()
    return [row.program for row in rows]


def save_program(
    db: Session,
    user_id: int,
    program_id: int,
) -> SavedProgramModel:
    saved = SavedProgramModel(user_id=user_id, program_id=program_id)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved


def delete_saved_program(db: Session, saved: SavedProgramModel) -> None:
    db.delete(saved)
    db.commit()
