from sqlalchemy.orm import Session
from models import University, Program
from schemas import Application, Task

from user import get_user_by_id as get_user

def get_applications(db:Session, user_id: int):
    user = get_user(db, user_id)
    if not user:
        return []
    applications = user.applications
    return applications

def update_application(db:Session, application_id: int, user_id: int, application_data):
    # Implement the logic to update an application for a user
    # This is a placeholder implementation; you should replace it with your actual update logic
    application = db.query(Application).filter(Application.id == application_id, Application.user_id == user_id).first()
    if application:
        for key, value in application_data.items():
            setattr(application, key, value)
        db.commit()
        db.refresh(application)
    return application

def get_tasks(db:Session, user_id: int):
    # Implement the logic to retrieve tasks for a user
    # This is a placeholder implementation; you should replace it with your actual retrieval logic
    tasks = []  # Replace with actual query to get tasks for the user
    return tasks

def add_task(db:Session, user_id: int, task_data):
    # Implement the logic to add a task for a user
    # This is a placeholder implementation; you should replace it with your actual add logic
    new_task = Task(**task_data, user_id=user_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def update_task(db:Session, task_id: int, user_id: int, task_data):
    # Implement the logic to update a task for a user
    # This is a placeholder implementation; you should replace it with your actual update logic
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if task:
        for key, value in task_data.items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
    return task

def remove_task(db:Session, task_id: int, user_id: int):
    # Implement the logic to remove a task for a user
    # This is a placeholder implementation; you should replace it with your actual remove logic
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task

def get_due_dates(db:Session, user_id: int):
    # Implement the logic to retrieve due dates for a user's saved programs
    # This is a placeholder implementation; you should replace it with your actual retrieval logic
    due_dates = []  # Replace with actual query to get due dates for the user's saved programs
    return due_dates