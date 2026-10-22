"""
Quick local check that the DB layer works: creates tables, opens a session,
inserts a user + related rows, reads them back, and tests delete cascades.

Run from the repo root:
    uv run --directory . env PYTHONPATH=src python scripts/db_smoke_test.py
Use a throwaway DB instead of ./gradvision.db with:
    DATABASE_URL=sqlite:///./smoke.db ...
"""

from sqlalchemy import func, select, text

from app.core.database import Base, SessionLocal, engine
from app.models import models  # noqa: F401  (registers tables on Base)
from app.models.models import (
    Application, DegreeType, PastEducation, Program, Task, University, User,
)


def main() -> None:
    print("DB:", engine.url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("tables:", sorted(Base.metadata.tables))

    with engine.connect() as conn:
        print("SELECT 1 ->", conn.execute(text("SELECT 1")).scalar())
        if engine.dialect.name == "sqlite":
            print("PRAGMA foreign_keys ->", conn.execute(text("PRAGMA foreign_keys")).scalar())

    with SessionLocal() as db:
        uni = University(university_name="Test U", location="Somewhere")
        prog = Program(university=uni, program_name="MS CS", degree_type=DegreeType.masters)
        user = User(
            first_name="Ada", last_name="Lovelace", email="ada@example.com",
            hashed_password="not-a-real-hash",
            past_education=[PastEducation(
                university_name="Old U", degree="BS", year_started=2020,
                year_ended=2024, currently_attending=False,
            )],
        )
        app = Application(user=user, program=prog, tasks=[Task(user=user, title="Request transcripts")])
        db.add_all([uni, prog, user, app])
        db.commit()

        got = db.scalars(select(User).where(User.email == "ada@example.com")).one()
        print("read back:", got.user_id, got.first_name, "| created_at:", got.created_at)
        print("past_education:", [p.university_name for p in got.past_education])
        print("applications:", [(a.program.program_name, a.status.value) for a in got.applications])
        print("tasks:", [t.title for t in got.tasks])

        # cascade check: deleting the user should remove their rows via ON DELETE CASCADE
        # (expire first: with passive_deletes=True the ORM only deletes children it has
        # already loaded, so this makes sure we're testing the DB-level cascade)
        user_id = got.user_id
        db.expire_all()
        db.delete(db.get(User, user_id))
        db.commit()
        for model in (PastEducation, Application, Task):
            n = db.scalar(select(func.count()).select_from(model).where(model.user_id == user_id))
            print(f"{model.__name__} rows left after user delete: {n}", "OK" if n == 0 else "<-- CASCADE NOT WORKING")


if __name__ == "__main__":
    main()
