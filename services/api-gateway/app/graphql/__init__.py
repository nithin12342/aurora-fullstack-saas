"""
GraphQL Schema and Resolvers
"""
import strawberry
from typing import Optional, List
from datetime import datetime


@strawberry.type
class User:
    id: strawberry.ID
    email: str
    name: str
    avatar: Optional[str] = None
    role: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime


@strawberry.type
class Task:
    id: strawberry.ID
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[str] = None
    tenant_id: str
    created_by: str
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


@strawberry.type
class Tenant:
    id: strawberry.ID
    name: str
    slug: str
    plan: str
    custom_domain: Optional[str] = None
    logo: Optional[str] = None
    created_at: datetime


@strawberry.type
class Subscription:
    id: strawberry.ID
    tenant_id: str
    plan: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool


@strawberry.type
class Invoice:
    id: strawberry.ID
    tenant_id: str
    amount: float
    currency: str
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime


@strawberry.input
class CreateTaskInput:
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None


@strawberry.input
class UpdateTaskInput:
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[datetime] = None


@strawberry.type
class Query:
    """GraphQL Query definitions"""
    
    @strawberry.field
    async def me(self) -> Optional[User]:
        """Get current user"""
        # Implementation would fetch from database
        return User(
            id="1",
            email="user@example.com",
            name="John Doe",
            role="admin",
            tenant_id="tenant-1",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
    
    @strawberry.field
    async def users(self, tenant_id: str) -> List[User]:
        """Get users for a tenant"""
        return []
    
    @strawberry.field
    async def tasks(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> List[Task]:
        """Get tasks for a tenant"""
        return []
    
    @strawberry.field
    async def task(self, id: strawberry.ID) -> Optional[Task]:
        """Get a single task by ID"""
        return None
    
    @strawberry.field
    async def tenant(self, id: strawberry.ID) -> Optional[Tenant]:
        """Get tenant by ID"""
        return None
    
    @strawberry.field
    async def subscription(self, tenant_id: str) -> Optional[Subscription]:
        """Get subscription for tenant"""
        return None
    
    @strawberry.field
    async def invoices(self, tenant_id: str) -> List[Invoice]:
        """Get invoices for tenant"""
        return []


@strawberry.type
class Mutation:
    """GraphQL Mutation definitions"""
    
    @strawberry.mutation
    async def create_task(
        self,
        input: CreateTaskInput,
        tenant_id: str,
        created_by: str,
    ) -> Task:
        """Create a new task"""
        now = datetime.now()
        return Task(
            id="new-task-id",
            title=input.title,
            description=input.description,
            status="todo",
            priority=input.priority,
            assignee_id=input.assignee_id,
            tenant_id=tenant_id,
            created_by=created_by,
            due_date=input.due_date,
            created_at=now,
            updated_at=now,
        )
    
    @strawberry.mutation
    async def update_task(
        self,
        id: strawberry.ID,
        input: UpdateTaskInput,
    ) -> Optional[Task]:
        """Update an existing task"""
        return None
    
    @strawberry.mutation
    async def delete_task(self, id: strawberry.ID) -> bool:
        """Delete a task"""
        return True


# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
