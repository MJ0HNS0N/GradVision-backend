"""University and professor schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.programs import ProgramSummary


class UniversitySummary(BaseModel):
    """List view (/api/universities) — counts only, no nested arrays."""
    model_config = ConfigDict(from_attributes=True)

    university_id: int
    university_name: str
    location: Optional[str] = None
    program_count: int
    professor_count: int


class ProfessorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    professor_id: int
    name: str
    department: Optional[str] = None
    university_id: int
    research_interests: list[str] = Field(default_factory=list)


class University(BaseModel):
    """Full detail view, including nested programs and professors."""
    model_config = ConfigDict(from_attributes=True)

    university_id: int
    university_name: str
    location: Optional[str] = None
    programs: list[ProgramSummary] = Field(default_factory=list)
    professors: list[ProfessorRead] = Field(default_factory=list)
