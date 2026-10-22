from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Task as TaskModel

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/user/{id}", response_model=list[TaskModel])
def get_user_tasks(
    id: int,
    db: Session = Depends(get_db),
) -> list[TaskModel]:
    tasks = db.query(TaskModel).filter(TaskModel.user_id == id).all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found for this user",
        )
    return tasks

@router.post("", response_model=TaskModel, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskModel,
    db: Session = Depends(get_db),
) -> TaskModel:
    task = TaskModel(**task_in.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{id}", response_model=TaskModel)
def update_task( 
    id: int,
    task_in: TaskModel,
    db: Session = Depends(get_db),
) -> TaskModel:
    task = db.query(TaskModel).filter(TaskModel.task_id == id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    for key, value in task_in.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{id}", response_model=dict)
def delete_task(
    id: int,
    db: Session = Depends(get_db),
) -> dict:
    task = db.query(TaskModel).filter(TaskModel.task_id == id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}