from sqlalchemy.orm import Session

from schemas.programs import SavedProgram, ProgramSummary
from user import get_user_by_id as get_user

def get_program(db:Session, program_id: int):
    return db.query(ProgramSummary).filter(ProgramSummary.program_id == program_id).first()

def save_program(db:Session, program_id: int, user_id: int):
    user = get_user(db, user_id)
    program = get_program(db, program_id)
    
    if program and user:
        saved_program = SavedProgram(user_id=user_id, program_id=program_id)
        db.add(saved_program)
        db.commit()
        db.refresh(saved_program)
        user.saved_programs.append(saved_program)
        return saved_program
    return []

def remove_program(db:Session, program_id: int, user_id: int):
    user = get_user(db, user_id)
    program = get_program(db, program_id)

    if program and user:
        saved_program = db.query(SavedProgram).filter(SavedProgram.user_id == user_id, SavedProgram.program_id == program_id).first()
        if saved_program:
            db.delete(saved_program)
            db.commit()
            user.saved_programs.remove(saved_program)
            return saved_program
    return []
        

def get_saved_programs(db:Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return []
    
    return user.saved_programs