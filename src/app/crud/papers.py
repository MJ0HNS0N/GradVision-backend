from sqlalchemy.orm import Session
from models import University, Program
from schemas import ProfessorRead, University
from schemas import ProgramSummary, Program
from user import get_user_by_id as get_user

def get_papers(db:Session, professor_id: int):
    papers = db.query(Paper).filter(Paper.professor_ids.contains([professor_id])).all()
    return papers
