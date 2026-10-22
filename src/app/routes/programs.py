"""Program and University Routes (get university and program info)"""

from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.crud.universities import list_universities
from app.crud.programs import get_program
from app.schemas.universities import UniversitySummary
from app.schemas.programs import Program

# endpoints: /api/universities/ (list universities)
# /api/program/{program_id} (get full detail for one program)

def list_universities_endpoint(
    db: Session = Depends(get_db),
    location: str | None = None,
    search: str | None = None,
    program_fields: list[str] | None = Query(None),
    limit: int | None = Query(None, ge=1, le=100),
    offset: int | None = Query(None, ge=0),
):
    return list_universities(db, location, search, program_fields, limit, offset)

def get_program_endpoint(
    program_id: int,
    db: Session = Depends(get_db)
):
    program = get_program(db, program_id)
    if program is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return program


# function to register the endpoints with the fastAPI app
def register(app: FastAPI) -> None:
    app.add_api_route("/api/universities", list_universities_endpoint, methods=['GET'], 
                      response_model=list[UniversitySummary], tags=["Universities and Programs"])

    app.add_api_route("/api/program/{program_id}", get_program_endpoint, methods=['GET'], 
                      response_model=Program, tags=["Universities and Programs"])
    