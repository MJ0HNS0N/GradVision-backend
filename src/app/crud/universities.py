from sqlalchemy.orm import Session
from models import University, Program
from schemas import ProfessorRead, University
from schemas import ProgramSummary, Program
from user import get_user_by_id as get_user

def search_universities(db:Session, user_id: int, location: str = None, program_type: str = None):
    user = get_user(db, user_id)
    if not user:
        return []

    programs = db.query(Program).filter(Program.program_type == program_type, Program.field == user.program_interests).all()
    universities = db.query(University).filter(University.location == location, University.programs == programs).all()
    return universities

def get_professors(db:Session, university_id: int, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return []
    return db.query(ProfessorRead).filter(ProfessorRead.university_id == university_id, ProfessorRead.research_interests == user.research_interests).all()

def get_programs_from_university(db:Session, university_id: int, field: str = None, degree_type: str = None):
    query = db.query(ProgramSummary).filter(ProgramSummary.university_id == university_id)
    if field:
        query = query.filter(ProgramSummary.field == field)
    if degree_type:
        query = query.filter(ProgramSummary.degree_type == degree_type)
    return query.all()