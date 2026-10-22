from datetime import date

from sqlalchemy import String, cast, select
from sqlalchemy.orm import Session, selectinload

from app.models.models import Paper, Professor, ProfessorPaper


def _paper_query():
    # `professors` is eager-loaded because the Paper schema's professor_ids is an
    # association proxy over it (lazy-loading it per paper would be an N+1)
    return (
        select(Paper)
        .options(selectinload(Paper.professors))
        .order_by(Paper.publication_date.desc().nulls_last(), Paper.paper_id)
    )


def get_papers_by_professor(db: Session, professor_id: int) -> list[Paper] | None:
    """Papers linked to one professor, newest first.

    Returns None if the professor doesn't exist (the route turns that into a 404),
    and [] if they exist but have no papers.
    """
    if db.get(Professor, professor_id) is None:
        return None

    query = _paper_query().where(
        Paper.professors.any(ProfessorPaper.professor_id == professor_id)
    )
    return list(db.execute(query).scalars().all())


def search_papers(
    db: Session,
    professor_id: int | None = None,
    query: str | None = None,
    year_published: int | None = None,
    limit: int | None = None,
    offset: int | None = None
) -> list[Paper]:
    """Search papers for GET /papers. Every filter is optional and they combine with AND.

    - professor_id: only papers linked to that professor.
    - query: keywords, split on whitespace. Every keyword must appear (case-insensitive)
      in the title, abstract or topics.
    - year_published: papers whose publication_date falls in that calendar year.
    """
    stmt = _paper_query()

    if professor_id is not None:
        # filter by the professor_id if provided
        stmt = stmt.where(
            Paper.professors.any(ProfessorPaper.professor_id == professor_id)
        )
    if query:
        for keyword in query.split():
            pattern = f"%{keyword}%"
            # checks for keywords in title, abstract, or paper topics
            stmt = stmt.where(
                Paper.title.ilike(pattern)
                | Paper.abstract.ilike(pattern)
                # topics is a JSON list, so match against its text form
                | cast(Paper.topics, String).ilike(pattern)
            )
    if year_published is not None:
        # a range (not extract(year, ...)) behaves the same on SQLite and Postgres
        stmt = stmt.where(
            Paper.publication_date >= date(year_published, 1, 1),
            Paper.publication_date < date(year_published + 1, 1, 1),
        )

    # handle offsets or limits
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)

    return list(db.execute(stmt).scalars().all())
