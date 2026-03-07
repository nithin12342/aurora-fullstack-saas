"""
Users Domain Service
FastAPI-based user management microservice for Aurora SaaS
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr
from uuid import uuid4
import os

app = FastAPI(title="Aurora Users Service", version="1.0.0")

# Enums
class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"

# Models
class User(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    avatar_url: Optional[str] = None
    tenant_id: str
    role: UserRole = UserRole.MEMBER
    status: UserStatus = UserStatus.PENDING
    department: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.MEMBER
    department: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None

# In-memory storage (replace with PostgreSQL in production)
users_db: dict = {}

def get_tenant_id_from_context() -> str:
    """Extract tenant_id from request context (JWT in production)"""
    return "default-tenant"

@app.post("/users", response_model=User, status_code=201)
async def create_user(
    user_data: UserCreate,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Create a new user"""
    # Check if email already exists in tenant
    for user in users_db.values():
        if user.tenant_id == tenant_id and user.email == user_data.email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists in this organization"
            )
    
    user_id = str(uuid4())
    now = datetime.utcnow()
    
    user = User(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        tenant_id=tenant_id,
        role=user_data.role,
        department=user_data.department,
        title=user_data.title,
        phone=user_data.phone,
        status=UserStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    
    users_db[user_id] = user
    return user

@app.get("/users", response_model=List[User])
async def list_users(
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    department: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id_from_context),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List users with filters"""
    users = [u for u in users_db.values() if u.tenant_id == tenant_id]
    
    # Apply filters
    if role:
        users = [u for u in users if u.role == role]
    if status:
        users = [u for u in users if u.status == status]
    if department:
        users = [u for u in users if u.department == department]
    
    # Sort by created_at descending
    users.sort(key=lambda u: u.created_at, reverse=True)
    
    return users[skip:skip + limit]

@app.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Get a specific user"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Update a user"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    users_db[user_id] = user
    return user

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Delete (deactivate) a user"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Soft delete - just mark as inactive
    user.status = UserStatus.INACTIVE
    user.updated_at = datetime.utcnow()
    users_db[user_id] = user
    return {"message": "User deactivated successfully"}

@app.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Activate a user"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user.status = UserStatus.ACTIVE
    user.updated_at = datetime.utcnow()
    users_db[user_id] = user
    return user

@app.get("/users/stats/summary")
async def get_user_stats(
    tenant_id: str = Depends(get_tenant_id_from_context)
):
    """Get user statistics summary"""
    users = [u for u in users_db.values() if u.tenant_id == tenant_id]
    
    return {
        "total": len(users),
        "active": len([u for u in users if u.status == UserStatus.ACTIVE]),
        "inactive": len([u for u in users if u.status == UserStatus.INACTIVE]),
        "pending": len([u for u in users if u.status == UserStatus.PENDING]),
        "by_role": {
            "owner": len([u for u in users if u.role == UserRole.OWNER]),
            "admin": len([u for u in users if u.role == UserRole.ADMIN]),
            "member": len([u for u in users if u.role == UserRole.MEMBER]),
            "viewer": len([u for u in users if u.role == UserRole.VIEWER]),
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "users-service",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
