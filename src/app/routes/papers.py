"""Professors and Papers routes (used to fetch papers)"""

from fastapi import FastAPI, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db

from app.crud.papers import get_papers_by_professor, search_papers
from app.schemas.papers import Paper

# endpoints: /professors/{id}/papers (papers linked to one professor), /papers (for general search)

def get_professor_papers(id: int, db: Session = Depends(get_db)):
    papers = get_papers_by_professor(db, id)
    if papers is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Professor not found")
    return papers

def get_papers_search(
    professor_id: int | None = None,
    query: str | None = None,
    year_published: int | None = None,
    db: Session = Depends(get_db),
    limit: int | None = Query(None, ge=1, le=100),
    offset: int | None = Query(None, ge=0),
):
    return search_papers(db, professor_id, query, year_published, limit, offset)


# function to register the endpoints with the fastAPI app
def register(app: FastAPI) -> None:
    app.add_api_route("/api/professors/{id}/papers", get_professor_papers, methods=['GET'],
                      response_model=list[Paper], tags=["Professors and Papers"])

    app.add_api_route("/api/papers", get_papers_search, methods=['GET'],
                      response_model=list[Paper], tags=["Professors and Papers"])
