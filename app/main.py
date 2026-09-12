from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Task
from .schemas import TaskCreate, TaskResponse


# API application
app = FastAPI(
    title="Task Manager API",
    version="0.2.0",
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Serve frontend static files
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


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
):
    new_task = Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    db: Session = Depends(get_db),
):
    return db.query(Task).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


@app.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    task.completed = True
    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()

    return None

