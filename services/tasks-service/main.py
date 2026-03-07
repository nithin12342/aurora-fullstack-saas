"""
Tasks Domain Service
FastAPI-based task management microservice for Aurora SaaS
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from uuid import uuid4
import os

app = FastAPI(title="Aurora Tasks Service", version="1.0.0")

# Enums
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Models
class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    tenant_id: str
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: List[str] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None

# In-memory storage (replace with PostgreSQL in production)
tasks_db: dict = {}

def get_tenant_id_from_context() -> str:
    """Extract tenant_id from request context (JWT in production)"""
    # In production, this would extract from JWT token
    return "default-tenant"

@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(
    task_data: TaskCreate,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Create a new task"""
    task_id = str(uuid4())
    now = datetime.utcnow()
    
    task = Task(
        id=task_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        tenant_id=tenant_id,
        assignee_id=task_data.assignee_id,
        due_date=task_data.due_date,
        tags=task_data.tags,
        created_at=now,
        updated_at=now,
    )
    
    tasks_db[task_id] = task
    return task

@app.get("/tasks", response_model=List[Task])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id_from_context),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List tasks with filters"""
    tasks = list(tasks_db.values())
    
    # Filter by tenant
    tasks = [t for t in tasks if t.tenant_id == tenant_id]
    
    # Apply filters
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    if assignee_id:
        tasks = [t for t in tasks if t.assignee_id == assignee_id]
    
    # Sort by created_at descending
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    
    # Pagination
    return tasks[skip:skip + limit]

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Get a specific task"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Update a task"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    tasks_db[task_id] = task
    return task

@app.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Delete a task"""
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del tasks_db[task_id]
    return {"message": "Task deleted successfully"}

@app.get("/tasks/stats/summary")
async def get_task_stats(
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Get task statistics summary"""
    tasks = [t for t in tasks_db.values() if t.tenant_id == tenant_id]
    
    return {
        "total": len(tasks),
        "todo": len([t for t in tasks if t.status == TaskStatus.TODO]),
        "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
        "done": len([t for t in tasks if t.status == TaskStatus.DONE]),
        "cancelled": len([t for t in tasks if t.status == TaskStatus.CANCELLED]),
        "by_priority": {
            "low": len([t for t in tasks if t.priority == TaskPriority.LOW]),
            "medium": len([t for t in tasks if t.priority == TaskPriority.MEDIUM]),
            "high": len([t for t in tasks if t.priority == TaskPriority.HIGH]),
            "urgent": len([t for t in tasks if t.priority == TaskPriority.URGENT]),
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tasks-service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
