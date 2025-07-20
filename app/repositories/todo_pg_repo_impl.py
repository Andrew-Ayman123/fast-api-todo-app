from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.todo_model import TodoModel, TodoItemModel
from app.schemas.todo_schema import TodoCreateRequest, TodoUpdateRequest, TodoItemsAddRequest, TodoItemUpdateRequest
from app.repositories.todo_repository import TodoRepositoryInterface
from app.config.database import DatabaseConnection
from datetime import datetime

class TodoPGRepository(TodoRepositoryInterface):
    """PostgreSQL implementation of Todo repository using SQLAlchemy ORM"""

    def __init__(self, database: DatabaseConnection):
        self.database = database

    async def _fetch_one(self, session: AsyncSession, query) -> Optional[object]:
        """Fetch one record using SQLAlchemy"""
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _fetch_all(self, session: AsyncSession, query) -> List[object]:
        """Fetch all records using SQLAlchemy"""
        result = await session.execute(query)
        return result.scalars().all()

    async def create_todo(self, todo_data: TodoCreateRequest) -> TodoModel:
        """Create a new todo using SQLAlchemy"""
        async with self.database.async_session() as session:
            new_todo = TodoModel(
                title=todo_data.title,
                description=todo_data.description
            )
            session.add(new_todo)
            await session.commit()
            await session.refresh(new_todo)
            
            # Ensure todo_items relationship is loaded before session closes
            # For a new todo, this will be an empty list
            await session.refresh(new_todo, ["todo_items"])
            return new_todo
    
    async def get_todo_by_id(self, todo_id: int) -> Optional[TodoModel]:
        """Get todo by ID using SQLAlchemy fetch_one equivalent"""
        async with self.database.async_session() as session:
            query = select(TodoModel).options(selectinload(TodoModel.todo_items)).where(TodoModel.id == todo_id)
            return await self._fetch_one(session, query)
    
    async def get_all_todos(self, skip: int = 0, limit: int = 100) -> List[TodoModel]:
        """Get all todos with pagination using SQLAlchemy fetch_all equivalent"""
        async with self.database.async_session() as session:
            query = select(TodoModel).options(selectinload(TodoModel.todo_items)).offset(skip).limit(limit).order_by(TodoModel.id)
            return await self._fetch_all(session, query)
    
    async def update_todo(self, todo_id: int, todo_data: TodoUpdateRequest) -> Optional[TodoModel]:
        """Update todo by ID using SQLAlchemy"""
        async with self.database.async_session() as session:
            # Fetch the todo to update
            query = select(TodoModel).where(TodoModel.id == todo_id)
            todo = await self._fetch_one(session, query)
            
            if not todo:
                return None
            
            # Update fields if provided
            if todo_data.title is not None:
                todo.title = todo_data.title
            if todo_data.description is not None:
                todo.description = todo_data.description
            
            await session.commit()
            await session.refresh(todo)
            return todo
    
    async def delete_todo(self, todo_id: int) -> bool:
        """Delete todo by ID using SQLAlchemy"""
        async with self.database.async_session() as session:
            query = select(TodoModel).where(TodoModel.id == todo_id)
            todo = await self._fetch_one(session, query)
            
            if not todo:
                return False
            
            await session.delete(todo)
            await session.commit()
            return True
    
    async def add_todo_item(self, todo_id: int, item_data: TodoItemsAddRequest) -> Optional[TodoItemModel]:
        """Add a todo item to a todo using SQLAlchemy"""
        async with self.database.async_session() as session:
            # Check if todo exists
            todo_query = select(TodoModel).where(TodoModel.id == todo_id)
            todo = await self._fetch_one(session, todo_query)
            
            if not todo:
                return None
            
            new_item = TodoItemModel(
                todo_id=todo_id,
                title=item_data.title,
                description=item_data.description,
                completed=False
            )
            
            session.add(new_item)
            await session.commit()
            await session.refresh(new_item)
            return new_item
    
    async def get_todo_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> List[TodoItemModel]:
        """Get todo items for a specific todo using SQLAlchemy fetch_all equivalent"""
        async with self.database.async_session() as session:
            # Check if todo exists
            todo_query = select(TodoModel).where(TodoModel.id == todo_id)
            todo = await self._fetch_one(session, todo_query)
            
            if not todo:
                return []
            
            query = (select(TodoItemModel)
                    .where(TodoItemModel.todo_id == todo_id)
                    .order_by(TodoItemModel.created_at)
                    .offset(skip)
                    .limit(limit))
            
            return await self._fetch_all(session, query)
    
    async def update_todo_item(self, todo_id: int, item_id: int, item_data: TodoItemUpdateRequest) -> Optional[TodoItemModel]:
        """Update a todo item using SQLAlchemy"""
        async with self.database.async_session() as session:
            # Check if todo exists
            todo_query = select(TodoModel).where(TodoModel.id == todo_id)
            todo = await self._fetch_one(session, todo_query)
            
            if not todo:
                return None
            
            # Fetch the todo item to update
            item_query = select(TodoItemModel).where(
                TodoItemModel.todo_id == todo_id,
                TodoItemModel.id == item_id
            )
            todo_item = await self._fetch_one(session, item_query)
            
            if not todo_item:
                return None
            
            # Update fields if provided
            if item_data.title is not None:
                todo_item.title = item_data.title
            if item_data.description is not None:
                todo_item.description = item_data.description
            if item_data.completed is not None:
                todo_item.completed = item_data.completed
            
            await session.commit()
            await session.refresh(todo_item)
            return todo_item
    
    async def delete_todo_item(self, todo_id: int, item_id: int) -> bool:
        """Delete a todo item using SQLAlchemy"""
        async with self.database.async_session() as session:
            # Check if todo exists
            todo_query = select(TodoModel).where(TodoModel.id == todo_id)
            todo = await self._fetch_one(session, todo_query)
            
            if not todo:
                return False
            
            # Fetch and delete the todo item
            item_query = select(TodoItemModel).where(
                TodoItemModel.todo_id == todo_id,
                TodoItemModel.id == item_id
            )
            todo_item = await self._fetch_one(session, item_query)
            
            if not todo_item:
                return False
            
            await session.delete(todo_item)
            await session.commit()
            return True
