"""
Fill the database with mock catalog data (universities, programs, events,
professors, papers) so the API endpoints have something to return.

Run from the repo root, after the tables exist (`uv run alembic upgrade head`):

    uv run python scripts/seed_db.py            # seed; skips if universities already exist
    uv run python scripts/seed_db.py --reset    # wipe existing rows first, then seed

Uses DATABASE_URL (default sqlite:///./gradvision.db, relative to where you run this).
Run it from the repo root so the app and this script see the same database file.

--reset deletes rows, it does NOT drop tables (Alembic owns the schema). It also
deletes user data that points at programs (applications, their tasks, saved programs)
because those rows can't exist without the programs. Users themselves are kept.
For safety it refuses to run against a non-SQLite database unless you add --force.
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import delete, inspect, select  # noqa: E402

from app.core.database import DATABASE_URL, SessionLocal, engine  # noqa: E402
from app.models.models import (  # noqa: E402
    Application, DegreeType, Event, Paper, Professor, ProfessorPaper,
    Program, SavedProgram, Task, University,
)

MS, PHD, COMBINED = DegreeType.masters, DegreeType.phd, DegreeType.combined


def upcoming(month: int, day: int) -> date:
    """Next occurrence of this month/day, so seeded deadlines are always in the future."""
    today = date.today()
    candidate = date(today.year, month, day)
    return candidate if candidate >= today else date(today.year + 1, month, day)


def deadlines(app_month: int, app_day: int) -> list[Event]:
    deadline = upcoming(app_month, app_day)
    return [
        Event(label="Application deadline", event_type="deadline", event_date=deadline),
        Event(label="Financial aid priority date", event_type="deadline",
              event_date=deadline - timedelta(days=30)),
        Event(label="Admission decisions released", event_type="decision",
              event_date=deadline + timedelta(days=75)),
    ]


COMMON_REQS = ["Transcripts", "Statement of purpose", "3 letters of recommendation", "Resume/CV"]

# (name, location, [programs], [professors])
# program: name, field, degree, funding, price, start, end, link, extra requirements, content, (deadline month, day)
UNIVERSITIES = [
    ("San Diego State University", "San Diego, CA", [
        ("MS Computer Science", "Computer Science", MS, False, 24000, 2027, 2029,
         "https://example.edu/sdsu/ms-cs", ["GRE (optional)"],
         ["Algorithms", "Operating Systems", "Machine Learning"], (12, 1)),
        ("MS Data Science", "Data Science", MS, True, 26000, 2027, 2029,
         "https://example.edu/sdsu/ms-ds", ["Programming sample"],
         ["Statistics", "Data Mining", "Visualization"], (1, 15)),
        ("MS Public Health", "Public Health", MS, False, 21000, 2027, 2029,
         "https://example.edu/sdsu/mph", [], ["Epidemiology", "Biostatistics"], (2, 1)),
    ], [
        ("Dr. Maria Santos", "Computer Science", ["machine learning", "computer vision"]),
        ("Dr. Wei Chen", "Computer Science", ["natural language processing", "machine learning"]),
        ("Dr. Priya Nair", "Public Health", ["epidemiology", "health data"]),
    ]),
    ("Massachusetts Institute of Technology", "Cambridge, MA", [
        ("PhD Electrical Engineering and Computer Science", "Electrical Engineering", PHD, True, 0, 2027, 2032,
         "https://example.edu/mit/phd-eecs", ["Research statement"],
         ["Signal Processing", "Machine Learning", "Systems"], (12, 15)),
        ("PhD Computer Science", "Computer Science", PHD, True, 0, 2027, 2032,
         "https://example.edu/mit/phd-cs", ["Research statement"],
         ["Theory", "Robotics", "Machine Learning"], (12, 15)),
        ("SM Mechanical Engineering", "Mechanical Engineering", MS, False, 58000, 2027, 2029,
         "https://example.edu/mit/sm-meche", [], ["Thermodynamics", "Controls"], (1, 5)),
    ], [
        ("Dr. Elena Volkov", "EECS", ["robotics", "machine learning"]),
        ("Dr. James Okafor", "EECS", ["signal processing", "wireless systems"]),
    ]),
    ("Stanford University", "Stanford, CA", [
        ("MS Computer Science", "Computer Science", MS, False, 62000, 2027, 2029,
         "https://example.edu/stanford/ms-cs", ["GRE (optional)"],
         ["Artificial Intelligence", "Systems", "Theory"], (12, 1)),
        ("Combined BS/MS Biology", "Biology", COMBINED, True, 45000, 2027, 2031,
         "https://example.edu/stanford/bsms-bio", ["Faculty advisor approval"],
         ["Genetics", "Cell Biology", "Lab Methods"], (1, 20)),
    ], [
        ("Dr. Hannah Brooks", "Biology", ["genomics", "cell biology"]),
        ("Dr. Raj Patel", "Computer Science", ["natural language processing", "reinforcement learning"]),
    ]),
    ("University of Michigan", "Ann Arbor, MI", [
        ("PhD Data Science", "Data Science", PHD, True, 0, 2027, 2032,
         "https://example.edu/umich/phd-ds", ["Research statement"],
         ["Statistical Learning", "Causal Inference"], (12, 10)),
        ("MS Mechanical Engineering", "Mechanical Engineering", MS, False, 39000, 2027, 2029,
         "https://example.edu/umich/ms-meche", [], ["Fluid Mechanics", "Manufacturing"], (2, 1)),
    ], [
        ("Dr. Sofia Alvarez", "Statistics", ["causal inference", "machine learning"]),
    ]),
    # a university with no programs or professors, to exercise the zero-count case
    ("Pacific Coast College", "Eugene, OR", [], []),
]

# (title, authors, topics, abstract, date or None, openalex id, link, [professor names])
PAPERS = [
    ("Efficient Vision Transformers for Edge Devices",
     ["Maria Santos", "Wei Chen"], ["computer vision", "machine learning"],
     "We study compact transformer architectures for on-device image classification.",
     date(2024, 6, 12), "W2000000001", "https://example.org/papers/2000000001",
     ["Dr. Maria Santos", "Dr. Wei Chen"]),
    ("Low-Resource Language Modelling with Synthetic Data",
     ["Wei Chen"], ["natural language processing"],
     "Synthetic data augmentation improves language models for under-resourced languages.",
     date(2023, 11, 3), "W2000000002", "https://example.org/papers/2000000002",
     ["Dr. Wei Chen"]),
    ("Epidemiological Modelling of Seasonal Respiratory Illness",
     ["Priya Nair"], ["epidemiology", "health data"],
     "A Bayesian model for forecasting regional respiratory illness incidence.",
     date(2022, 2, 20), "W2000000003", "https://example.org/papers/2000000003",
     ["Dr. Priya Nair"]),
    ("Sample-Efficient Robot Manipulation",
     ["Elena Volkov"], ["robotics", "reinforcement learning"],
     "Learning dexterous manipulation policies from few demonstrations.",
     date(2024, 9, 1), "W2000000004", "https://example.org/papers/2000000004",
     ["Dr. Elena Volkov"]),
    ("Adaptive Beamforming for Dense Wireless Networks",
     ["James Okafor", "Elena Volkov"], ["signal processing", "wireless systems"],
     "Beamforming that adapts to rapidly changing user density.",
     date(2021, 4, 15), "W2000000005", "https://example.org/papers/2000000005",
     ["Dr. James Okafor", "Dr. Elena Volkov"]),
    ("Single-Cell Genomics at Scale",
     ["Hannah Brooks"], ["genomics", "cell biology"],
     "Pipelines for analysing millions of single-cell expression profiles.",
     date(2023, 7, 28), "W2000000006", "https://example.org/papers/2000000006",
     ["Dr. Hannah Brooks"]),
    ("Language Agents That Learn From Feedback",
     ["Raj Patel", "Wei Chen"], ["natural language processing", "reinforcement learning"],
     "Training language agents with human and automated feedback signals.",
     date(2024, 1, 9), "W2000000007", "https://example.org/papers/2000000007",
     ["Dr. Raj Patel", "Dr. Wei Chen"]),
    ("Causal Forests for Heterogeneous Treatment Effects",
     ["Sofia Alvarez"], ["causal inference", "machine learning"],
     "Estimating who benefits from an intervention with tree ensembles.",
     date(2022, 10, 5), "W2000000008", "https://example.org/papers/2000000008",
     ["Dr. Sofia Alvarez"]),
    ("Genomic Language Models: A Survey",
     ["Hannah Brooks", "Raj Patel"], ["genomics", "machine learning"],
     "A survey of language-model techniques applied to genomic sequences.",
     date(2024, 3, 18), "W2000000009", "https://example.org/papers/2000000009",
     ["Dr. Hannah Brooks", "Dr. Raj Patel"]),
    # undated preprint with no linked professor
    ("Unpublished Notes on Federated Learning", [], ["machine learning"], None,
     None, None, None, []),
]

# delete order matters: children before parents (foreign keys are enforced)
TABLES_TO_CLEAR = [
    Task, Application, SavedProgram, Event, ProfessorPaper, Paper, Professor, Program, University,
]


def check_tables_exist() -> None:
    existing = set(inspect(engine).get_table_names())
    missing = [t.__tablename__ for t in TABLES_TO_CLEAR if t.__tablename__ not in existing]
    if missing:
        sys.exit(f"Missing tables {missing}. Run `uv run alembic upgrade head` first.")


def reset(db) -> None:
    for model in TABLES_TO_CLEAR:
        db.execute(delete(model))
    db.commit()
    print("Cleared existing catalog data.")


def seed(db) -> None:
    professors: dict[str, Professor] = {}
    objects: list = []

    for uni_name, location, programs, profs in UNIVERSITIES:
        university = University(university_name=uni_name, location=location)

        for (name, field, degree, funding, price, start, end, link, extra_reqs,
             content, (month, day)) in programs:
            university.programs.append(Program(
                program_name=name, field=field, degree_type=degree,
                funding_available=funding, price=price or None,
                program_start=start, program_end=end, application_link=link,
                application_requirements=COMMON_REQS + extra_reqs,
                program_content=content, events=deadlines(month, day),
            ))

        for prof_name, department, interests in profs:
            professor = Professor(name=prof_name, department=department,
                                  research_interests=interests)
            university.professors.append(professor)
            professors[prof_name] = professor

        objects.append(university)

    for title, authors, topics, abstract, published, openalex_id, link, prof_names in PAPERS:
        paper = Paper(title=title, authors=authors, topics=topics, abstract=abstract,
                      publication_date=published, external_id_openalex=openalex_id, link=link)
        paper.professors = [ProfessorPaper(professor=professors[n]) for n in prof_names]
        objects.append(paper)

    db.add_all(objects)
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the GradVision database with mock data.")
    parser.add_argument("--reset", action="store_true",
                        help="delete existing catalog rows (and user activity tied to them) before seeding")
    parser.add_argument("--force", action="store_true",
                        help="allow --reset against a non-SQLite database")
    args = parser.parse_args()

    print("Database:", engine.url)
    if args.reset and not DATABASE_URL.startswith("sqlite") and not args.force:
        sys.exit("Refusing to --reset a non-SQLite database without --force.")

    check_tables_exist()

    with SessionLocal() as db:
        if args.reset:
            reset(db)
        elif db.scalar(select(University.university_id).limit(1)) is not None:
            print("Database already has universities, skipping. Use --reset to wipe and reseed.")
            return

        seed(db)

        for model in (University, Program, Event, Professor, Paper, ProfessorPaper):
            count = len(db.scalars(select(model)).all())
            print(f"  {model.__tablename__:18} {count}")
    print("Seeded.")


if __name__ == "__main__":
    main()
