"""
FastAPI dependencies shared across routes.

`get_current_user` is the integration point for the Authentication issue:
replace this implementation with JWT validation while keeping the same name
and return type so user-scoped routes keep working.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import User as UserModel


def get_current_user(
    db: Session = Depends(get_db),
) -> UserModel:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
