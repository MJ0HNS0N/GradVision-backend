"""Paper schemas."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Paper(BaseModel):
    """TODO: professor_ids comes from the ProfessorPaper association rows, not a
    plain column — build it with e.g.
        Paper(**paper.__dict__, professor_ids=[pp.professor_id for pp in paper.professors])
    or add a `professor_ids` hybrid/association_proxy on the Paper model."""

    paper_id: int
    title: str
    authors: list[str] = Field(default_factory=list)
    professor_ids: list[int] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    publication_date: Optional[date] = None
    external_id_openalex: Optional[str] = None
    link: Optional[str] = None
