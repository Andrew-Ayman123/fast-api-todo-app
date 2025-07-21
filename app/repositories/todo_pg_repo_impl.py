"""PostgreSQL implementation of Todo repository.

This module provides a PostgreSQL implementation of the TodoRepositoryInterface
using SQLAlchemy ORM for database operations.
"""
from sqlalchemy import Select, delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.config.database import DatabaseConnection
from app.models.todo_model import TodoListItemModel, TodoListModel
from app.repositories.todo_repository import TodoRepositoryInterface
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)


class TodoPGRepository(TodoRepositoryInterface):
    """PostgreSQL implementation of Todo repository using SQLAlchemy ORM."""

    def __init__(self, database: DatabaseConnection) -> None:
        """Initialize the PostgreSQL repository with database connection.

        Args:
            database (DatabaseConnection): The database connection instance.

        """
        self.database = database

    async def _fetch_one(self, session: AsyncSession, query: Select) -> object | None:
        """Fetch one record using SQLAlchemy.

        Args:
            session (AsyncSession): The database session.
            query (Select): The SQLAlchemy query to execute.

        Returns:
            object | None: The fetched record if found, None otherwise.

        """
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _fetch_all(self, session: AsyncSession, query: Select) -> list[object]:
        """Fetch all records using SQLAlchemy.

        Args:
            session (AsyncSession): The database session.
            query (Select): The SQLAlchemy query to execute.

        Returns:
            list[object]: List of all fetched records.

        """
        result = await session.execute(query)
        return result.scalars().all()

    async def create_todo_list(self, todo_data: TodoListCreateRequest) -> TodoListModel:
        """Create a new todo list using SQLAlchemy.

        Args:
            todo_data (TodoListCreateRequest): The data for creating a new todo list.

        Returns:
            TodoListModel: The created todo list with assigned ID.

        """
        async with self.database.async_session() as session:
            new_todo = TodoListModel(title=todo_data.title, description=todo_data.description)
            session.add(new_todo)
            await session.commit()
            await session.refresh(new_todo)

            # Ensure todo_items relationship is loaded before session closes
            # For a new todo, this will be an empty list
            await session.refresh(new_todo, ["todo_items"])
            return new_todo

    async def get_todo_list_by_id(self, todo_id: int) -> TodoListModel | None:
        """Get todo by ID using SQLAlchemy fetch_one equivalent.

        Args:
            todo_id (int): The ID of the todo list to retrieve.

        Returns:
            TodoListModel | None: The todo list if found, None otherwise.

        """
        async with self.database.async_session() as session:
            query = (
                select(TodoListModel).options(selectinload(TodoListModel.todo_items)).where(TodoListModel.id == todo_id)
            )
            return await self._fetch_one(session, query)

    async def get_all_todo_lists(self, skip: int = 0, limit: int = 100) -> list[TodoListModel]:
        """Get all todos with pagination using SQLAlchemy fetch_all equivalent.

        Args:
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListModel]: List of todo lists.

        """
        async with self.database.async_session() as session:
            query = (
                select(TodoListModel)
                .options(selectinload(TodoListModel.todo_items))
                .offset(skip)
                .limit(limit)
                .order_by(TodoListModel.id)
            )
            return await self._fetch_all(session, query)

    async def update_todo_list(self, todo_id: int, todo_data: TodoListUpdateRequest) -> TodoListModel | None:
        """Update todo by ID using SQLAlchemy direct update.

        Args:
            todo_id (int): The ID of the todo list to update.
            todo_data (TodoListUpdateRequest): The updated todo list data.

        Returns:
            TodoListModel | None: The updated todo list if found, None otherwise.

        """
        async with self.database.async_session() as session:
            # Perform direct update and check affected rows
            update_data = todo_data.model_dump(exclude_unset=True)
            if not update_data:
                # No fields to update, fetch and return existing todo
                query = (
                    select(TodoListModel)
                    .options(selectinload(TodoListModel.todo_items))
                    .where(TodoListModel.id == todo_id)
                )
                return await self._fetch_one(session, query)

            stmt = update(TodoListModel).where(TodoListModel.id == todo_id).values(**update_data)
            result = await session.execute(stmt)

            # Check if any rows were affected (todo exists)
            if result.rowcount == 0:
                return None

            await session.commit()

            # Fetch and return the updated todo with items using selectinload
            # selectinload is used here because we need to return the complete todo with its items
            # after the update operation, avoiding the N+1 query problem
            query = (
                select(TodoListModel)
                .options(selectinload(TodoListModel.todo_items))
                .where(TodoListModel.id == todo_id)
            )
            return await self._fetch_one(session, query)

    async def delete_todo_list(self, todo_id: int) -> bool:
        """Delete todo by ID using SQLAlchemy direct delete.

        Args:
            todo_id (int): The ID of the todo list to delete.

        Returns:
            bool: True if the todo list was deleted, False if not found.

        """
        async with self.database.async_session() as session:
            # Perform direct delete and check affected rows
            stmt = delete(TodoListModel).where(TodoListModel.id == todo_id)
            result = await session.execute(stmt)

            await session.commit()
            # Return True if any rows were deleted (todo existed)
            return result.rowcount > 0

    async def add_todo_list_item(self, todo_id: int, item_data: TodoListItemsAddRequest) -> TodoListItemModel | None:
        """Add a todo item to a todo using SQLAlchemy.

        Args:
            todo_id (int): The ID of the todo list to add the item to.
            item_data (TodoListItemsAddRequest): The data for the new todo item.

        Returns:
            TodoListItemModel | None: The created todo item if the list exists, None otherwise.

        """
        async with self.database.async_session() as session:
            try:
                # Create new item directly - foreign key constraint will handle todo existence validation
                new_item = TodoListItemModel(
                    todo_id=todo_id, title=item_data.title, description=item_data.description, completed=False,
                )

                session.add(new_item)
                await session.commit()
            except IntegrityError:
                # If foreign key constraint fails (todo doesn't exist), rollback and return None
                await session.rollback()
                return None
            else:
                await session.refresh(new_item)
                return new_item

    async def get_todo_list_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> list[TodoListItemModel]:
        """Get todo items for a specific todo using SQLAlchemy fetch_all equivalent.

        Args:
            todo_id (int): The ID of the todo list to get items from.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListItemModel]: List of todo items for the specified todo list.
                                   Returns empty list if todo doesn't exist.

        """
        async with self.database.async_session() as session:
            # Directly query items - if todo doesn't exist, we'll get empty list
            # No need to check todo existence separately as foreign key constraint ensures data integrity
            query = (
                select(TodoListItemModel)
                .where(TodoListItemModel.todo_id == todo_id)
                .order_by(TodoListItemModel.created_at)
                .offset(skip)
                .limit(limit)
            )

            return await self._fetch_all(session, query)

    async def update_todo_list_item(
        self, todo_id: int, item_id: int, item_data: TodoListItemUpdateRequest,
    ) -> TodoListItemModel | None:
        """Update a todo item using SQLAlchemy direct update.

        Args:
            todo_id (int): The ID of the todo list containing the item.
            item_id (int): The ID of the todo item to update.
            item_data (TodoListItemUpdateRequest): The updated todo item data.

        Returns:
            TodoListItemModel | None: The updated todo item if found, None otherwise.

        """
        async with self.database.async_session() as session:
            # Perform direct update and check affected rows
            update_data = item_data.model_dump(exclude_unset=True)
            if not update_data:
                # No fields to update, fetch and return existing item
                query = select(TodoListItemModel).where(
                    TodoListItemModel.todo_id == todo_id, TodoListItemModel.id == item_id,
                )
                return await self._fetch_one(session, query)

            stmt = (
                update(TodoListItemModel)
                .where(TodoListItemModel.todo_id == todo_id, TodoListItemModel.id == item_id)
                .values(**update_data)
            )
            result = await session.execute(stmt)

            # Check if any rows were affected (item exists and belongs to the todo)
            if result.rowcount == 0:
                return None

            await session.commit()

            # Fetch and return the updated item
            query = select(TodoListItemModel).where(
                TodoListItemModel.todo_id == todo_id, TodoListItemModel.id == item_id,
            )
            return await self._fetch_one(session, query)

    async def delete_todo_list_item(self, todo_id: int, item_id: int) -> bool:
        """Delete a todo item using SQLAlchemy direct delete.

        Args:
            todo_id (int): The ID of the todo list containing the item.
            item_id (int): The ID of the todo item to delete.

        Returns:
            bool: True if the todo item was deleted, False if not found.

        """
        async with self.database.async_session() as session:
            # Perform direct delete and check affected rows
            stmt = delete(TodoListItemModel).where(
                TodoListItemModel.todo_id == todo_id, TodoListItemModel.id == item_id,
            )
            result = await session.execute(stmt)

            await session.commit()
            # Return True if any rows were deleted (item existed and belonged to the todo)
            return result.rowcount > 0
