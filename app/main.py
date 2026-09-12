from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import get_db
from .models import Task
from .schemas import TaskCreate, TaskResponse

app = FastAPI(
    title="Task Manager API",
    version="0.2.0",
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


@app.get("/home")
def home():
    return {
        "docs": "/docs",
        "frontend": "/static/index.html",
    }


@app.get("/")
def root():
    return {
        "message": "Task Manager API is running!",
        "version": "0.2.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=201,
)
def create_task(
    task: TaskCreate,
    db: Annotated[Session, Depends(get_db)],
):
    db_task = Task(**task.model_dump())

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@app.get(
    "/tasks",
    response_model=list[TaskResponse],
)
def get_tasks(
    db: Annotated[Session, Depends(get_db)],
):
    return db.query(Task).all()


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.patch(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
)
def complete_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    task.completed = True
    db.commit()
    db.refresh(task)

    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
)
def delete_task(
    task_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    db.delete(task)
    db.commit() 
    