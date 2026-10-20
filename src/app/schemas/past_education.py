"""Past education schemas (nested under User)."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class PastEducationBase(BaseModel):
    university_name: str
    major: Optional[str] = None
    degree: str
    year_started: int
    year_ended: int
    currently_attending: bool


class PastEducationCreate(PastEducationBase):
    pass


class PastEducation(PastEducationBase):
    model_config = ConfigDict(from_attributes=True)
    education_id: int
