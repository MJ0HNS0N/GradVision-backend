"""Database operations for users and nested past education."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.models.models import PastEducation as PastEducationModel
from app.models.models import User as UserModel
from app.schemas.past_education import PastEducationCreate
from app.schemas.users import UserCreate, UserUpdate


def _user_query():
    return select(UserModel).options(selectinload(UserModel.past_education))


def get_user_by_id(db: Session, user_id: int) -> UserModel | None:
    return db.execute(
        _user_query().where(UserModel.user_id == user_id)
    ).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> UserModel | None:
    return db.execute(
        _user_query().where(UserModel.email == email)
    ).scalar_one_or_none()


def _past_education_from_create(
    items: list[PastEducationCreate],
) -> list[PastEducationModel]:
    return [
        PastEducationModel(
            university_name=item.university_name,
            major=item.major,
            degree=item.degree,
            year_started=item.year_started,
            year_ended=item.year_ended,
            currently_attending=item.currently_attending,
        )
        for item in items
    ]


def create_user(db: Session, user_in: UserCreate) -> UserModel:
    user = UserModel(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        research_interests=[],
        career_goals=[],
        program_interests=[],
        past_education=_past_education_from_create(user_in.past_education),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return get_user_by_id(db, user.user_id)  # type: ignore[return-value]


def replace_past_education(
    db: Session,
    user: UserModel,
    items: list[PastEducationCreate],
) -> None:
    user.past_education.clear()
    user.past_education.extend(_past_education_from_create(items))


def update_user(db: Session, user: UserModel, user_in: UserUpdate) -> UserModel:
    data = user_in.model_dump(
        exclude_unset=True,
        exclude={"password", "past_education"},
    )

    if user_in.password is not None:
        user.hashed_password = hash_password(user_in.password)

    if user_in.past_education is not None:
        replace_past_education(db, user, user_in.past_education)

    for field, value in data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return get_user_by_id(db, user.user_id)  # type: ignore[return-value]


def delete_user(db: Session, user: UserModel) -> None:
    db.delete(user)
    db.commit()
