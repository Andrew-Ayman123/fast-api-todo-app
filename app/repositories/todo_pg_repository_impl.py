"""PostgreSQL implementation of Todo repository.

This module provides a PostgreSQL implementation of the TodoRepositoryInterface
using SQLAlchemy ORM for database operations with user authorization.
"""

import uuid
from typing import TypeVar

from sqlalchemy import Select, delete, func, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.todo_model import TodoListItemModel, TodoListModel
from app.repositories.todo_repository_interface import TodoRepositoryInterface
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)
from app.utils.logger_util import get_logger

T = TypeVar("T")


class TodoPGRepository(TodoRepositoryInterface):
    """PostgreSQL implementation of Todo repository using SQLAlchemy ORM."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the PostgreSQL repository with async session.

        Args:
            session (AsyncSession): The database session instance.

        """
        self.session = session

    async def _fetch_one(self, query: Select[tuple[T]]) -> T | None:
        """Fetch one record using SQLAlchemy.

        Args:
            query (Select): The SQLAlchemy query to execute.

        Returns:
            T | None: The fetched record if found, None otherwise.

        """
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _fetch_all(self, query: Select[tuple[T]]) -> list[T]:
        """Fetch all records using SQLAlchemy.

        Args:
            query (Select): The SQLAlchemy query to execute.

        Returns:
            list[T]: List of all fetched records.

        """
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_todo_list(self, todo_data: TodoListCreateRequest, user_id: uuid.UUID) -> TodoListModel:
        """Create a new todo list using SQLAlchemy.

        Args:
            todo_data (TodoListCreateRequest): The data for creating a new todo list.
            user_id (uuid.UUID): The ID of the user creating the todo list.

        Returns:
            TodoListModel: The created todo list with assigned ID.

        """
        get_logger().debug("Creating new todo list with title: %s for user: %s", todo_data.title, user_id)

        new_todo = TodoListModel(title=todo_data.title, description=todo_data.description, user_id=user_id)
        self.session.add(new_todo)
        await self.session.commit()
        await self.session.refresh(new_todo)

        await self.session.refresh(new_todo, ["todo_items"])
        get_logger().info("Successfully created todo list with ID: %s for user: %s", new_todo.id, user_id)
        return new_todo

    async def get_todo_list_by_id(self, todo_id: uuid.UUID, user_id: uuid.UUID) -> TodoListModel | None:
        """Get todo by ID for a specific user using SQLAlchemy fetch_one equivalent.

        Args:
            todo_id (uuid.UUID): The ID of the todo list to retrieve.
            user_id (uuid.UUID): The ID of the user requesting the todo list.

        Returns:
            TodoListModel | None: The todo list if found and owned by user, None otherwise.

        """
        get_logger().debug("Fetching todo list by ID: %s for user: %s", todo_id, user_id)

        query = (
            select(TodoListModel)
            .options(selectinload(TodoListModel.todo_items))
            .where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
        )
        result = await self._fetch_one(query)
        if result:
            get_logger().info("Successfully retrieved todo list ID: %s for user: %s", todo_id, user_id)
        else:
            get_logger().warning("Todo list with ID: %s not found for user: %s", todo_id, user_id)
        return result

    async def get_all_todo_lists(self, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[TodoListModel]:
        """Get all todos for a user with pagination using SQLAlchemy fetch_all equivalent.

        Args:
            user_id (uuid.UUID): The ID of the user whose todos to retrieve.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListModel]: List of todo lists for the user.

        """
        get_logger().debug("Fetching all todo lists for user: %s with skip: %s, limit: %s", user_id, skip, limit)

        query = (
            select(TodoListModel)
            .options(selectinload(TodoListModel.todo_items))
            .where(TodoListModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(TodoListModel.created_at.desc())
        )
        result = await self._fetch_all(query)
        get_logger().info("Successfully retrieved %s todo lists for user: %s", len(result), user_id)
        return result

    async def update_todo_list(
        self,
        todo_id: uuid.UUID,
        todo_data: TodoListUpdateRequest,
        user_id: uuid.UUID,
    ) -> TodoListModel | None:
        """Update todo by ID for a specific user using SQLAlchemy direct update.

        Args:
            todo_id (uuid.UUID): The ID of the todo list to update.
            todo_data (TodoListUpdateRequest): The updated todo list data.
            user_id (uuid.UUID): The ID of the user updating the todo list.

        Returns:
            TodoListModel | None: The updated todo list if found and owned by user, None otherwise.

        """
        get_logger().debug("Updating todo list with ID: %s for user: %s", todo_id, user_id)

        update_data = todo_data.model_dump(exclude_unset=True)
        if not update_data:
            get_logger().info("No fields to update for todo list ID: %s, returning existing todo", todo_id)

            query = (
                select(TodoListModel)
                .options(selectinload(TodoListModel.todo_items))
                .where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
            )
            todo_list = await self._fetch_one(query)
            if not todo_list:
                get_logger().warning("Todo list with ID: %s not found for user: %s for update", todo_id, user_id)
                return None
            get_logger().info("Returning existing todo list ID: %s for user: %s", todo_id, user_id)
            return todo_list

        get_logger().debug("Updating todo list ID: %s for user: %s with data: %s", todo_id, user_id, update_data)
        stmt = (
            update(TodoListModel)
            .where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
            .values(**update_data)
            .returning(TodoListModel)
        )

        result = await self.session.execute(stmt)
        updated_todo = result.scalar_one_or_none()

        if updated_todo is None:
            get_logger().warning("Todo list with ID: %s not found for user: %s for update", todo_id, user_id)
            return None

        await self.session.commit()
        get_logger().info("Successfully updated todo list ID: %s for user: %s", todo_id, user_id)

        await self.session.refresh(updated_todo, ["todo_items"])
        return updated_todo

    async def delete_todo_list(self, todo_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete todo by ID for a specific user using SQLAlchemy direct delete.

        Args:
            todo_id (uuid.UUID): The ID of the todo list to delete.
            user_id (uuid.UUID): The ID of the user deleting the todo list.

        Returns:
            bool: True if the todo list was deleted, False if not found or not owned by user.

        """
        get_logger().debug("Deleting todo list with ID: %s for user: %s", todo_id, user_id)

        stmt = delete(TodoListModel).where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
        result = await self.session.execute(stmt)

        await self.session.commit()

        deleted = result.rowcount > 0
        if deleted:
            get_logger().info("Successfully deleted todo list ID: %s for user: %s", todo_id, user_id)
        else:
            get_logger().warning("Todo list with ID: %s not found for user: %s for deletion", todo_id, user_id)
        return deleted

    async def add_todo_list_item(
        self,
        todo_id: uuid.UUID,
        item_data: TodoListItemsAddRequest,
        user_id: uuid.UUID,
    ) -> TodoListItemModel | None:
        """Add a todo item to a user's todo using SQLAlchemy.

        Args:
            todo_id (uuid.UUID): The ID of the todo list to add the item to.
            item_data (TodoListItemsAddRequest): The data for the new todo item.
            user_id (uuid.UUID): The ID of the user adding the item.

        Returns:
            TodoListItemModel | None: The created todo item if the list exists and is owned by user, None otherwise.

        """
        get_logger().debug(
            "Adding item to todo list ID: %s with title: %s for user: %s",
            todo_id,
            item_data.title,
            user_id,
        )

        todo_query = select(TodoListModel).where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
        todo_exists = await self._fetch_one(todo_query)

        if not todo_exists:
            get_logger().warning("Todo list ID: %s not found for user: %s", todo_id, user_id)
            return None

        try:
            new_item = TodoListItemModel(
                todo_id=todo_id,
                title=item_data.title,
                description=item_data.description,
                completed=False,
            )

            self.session.add(new_item)
            await self.session.commit()
            await self.session.refresh(new_item)
            get_logger().info(
                "Successfully added item ID: %s to todo list ID: %s for user: %s",
                new_item.id,
                todo_id,
                user_id,
            )
        except IntegrityError:
            await self.session.rollback()
            get_logger().warning(
                "Failed to add item to todo list ID: %s for user: %s - integrity error",
                todo_id,
                user_id,
            )
            return None
        else:
            return new_item

    async def get_todo_list_items(
        self,
        todo_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TodoListItemModel]:
        """Get todo items for a specific user's todo using SQLAlchemy fetch_all equivalent.

        Args:
            todo_id (uuid.UUID): The ID of the todo list to get items from.
            user_id (uuid.UUID): The ID of the user requesting the items.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListItemModel]: List of todo items for the specified todo list if owned by user.
                                   Returns empty list if todo doesn't exist or isn't owned by user.

        """
        get_logger().debug(
            "Fetching items for todo list ID: %s for user: %s with skip: %s, limit: %s",
            todo_id,
            user_id,
            skip,
            limit,
        )

        query = (
            select(TodoListItemModel)
            .join(TodoListModel, TodoListItemModel.todo_id == TodoListModel.id)
            .where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
            .order_by(TodoListItemModel.created_at)
            .offset(skip)
            .limit(limit)
        )

        result = await self._fetch_all(query)
        get_logger().info(
            "Successfully retrieved %s items for todo list ID: %s for user: %s",
            len(result),
            todo_id,
            user_id,
        )
        return result

    async def update_todo_list_item(
        self,
        todo_id: uuid.UUID,
        item_id: uuid.UUID,
        item_data: TodoListItemUpdateRequest,
        user_id: uuid.UUID,
    ) -> TodoListItemModel | None:
        """Update a todo item for a specific user using SQLAlchemy direct update.

        Args:
            todo_id (uuid.UUID): The ID of the todo list containing the item.
            item_id (uuid.UUID): The ID of the todo item to update.
            item_data (TodoListItemUpdateRequest): The updated todo item data.
            user_id (uuid.UUID): The ID of the user updating the item.

        Returns:
            TodoListItemModel | None: The updated todo item if found and owned by user, None otherwise.

        """
        get_logger().debug("Updating todo item ID: %s in todo list ID: %s for user: %s", item_id, todo_id, user_id)

        update_data = item_data.model_dump(exclude_unset=True)
        if not update_data:
            get_logger().info(
                "No fields to update for todo item ID: %s in todo list ID: %s, returning existing item",
                item_id,
                todo_id,
            )

            query = (
                select(TodoListItemModel)
                .join(TodoListModel, TodoListItemModel.todo_id == TodoListModel.id)
                .where(
                    TodoListModel.id == todo_id,
                    TodoListModel.user_id == user_id,
                    TodoListItemModel.id == item_id,
                )
            )
            todo_list_item = await self._fetch_one(query)
            if not todo_list_item:
                get_logger().warning(
                    "Todo item ID: %s not found in todo list ID: %s for user: %s for update",
                    item_id,
                    todo_id,
                    user_id,
                )
                return None
            return todo_list_item

        get_logger().debug(
            "Updating todo item ID: %s in todo list ID: %s for user: %s with data: %s",
            item_id,
            todo_id,
            user_id,
            update_data,
        )

        subquery = select(TodoListModel.id).where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
        stmt = (
            update(TodoListItemModel)
            .where(TodoListItemModel.todo_id.in_(subquery), TodoListItemModel.id == item_id)
            .values(**update_data)
            .returning(TodoListItemModel)
        )
        result = await self.session.execute(stmt)
        updated_item = result.scalar_one_or_none()

        if updated_item is None:
            get_logger().warning(
                "Todo item ID: %s not found in todo list ID: %s for user: %s for update",
                item_id,
                todo_id,
                user_id,
            )
            return None

        await self.session.commit()
        get_logger().info(
            "Successfully updated todo item ID: %s in todo list ID: %s for user: %s",
            item_id,
            todo_id,
            user_id,
        )
        return updated_item

    async def delete_todo_list_item(self, todo_id: uuid.UUID, item_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a todo item for a specific user using SQLAlchemy direct delete.

        Args:
            todo_id (uuid.UUID): The ID of the todo list containing the item.
            item_id (uuid.UUID): The ID of the todo item to delete.
            user_id (uuid.UUID): The ID of the user deleting the item.

        Returns:
            bool: True if the todo item was deleted, False if not found or not owned by user.

        """
        get_logger().debug("Deleting todo item ID: %s from todo list ID: %s for user: %s", item_id, todo_id, user_id)

        subquery = select(TodoListModel.id).where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
        stmt = delete(TodoListItemModel).where(
            TodoListItemModel.todo_id.in_(subquery),
            TodoListItemModel.id == item_id,
        )
        result = await self.session.execute(stmt)

        await self.session.commit()

        deleted = result.rowcount > 0
        if deleted:
            get_logger().info(
                "Successfully deleted todo item ID: %s from todo list ID: %s for user: %s",
                item_id,
                todo_id,
                user_id,
            )
        else:
            get_logger().warning(
                "Todo item ID: %s not found in todo list ID: %s for user: %s for deletion",
                item_id,
                todo_id,
                user_id,
            )
        return deleted

    async def count_todo_lists(self, user_id: uuid.UUID) -> int:
        """Count the total number of todo lists for a specific user in the database.

        Args:
            user_id (uuid.UUID): The ID of the user whose todos to count.

        Returns:
            int: Total number of todo lists for the user.

        """
        query = select(func.count()).select_from(TodoListModel).where(TodoListModel.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def count_todo_list_items(self, todo_id: uuid.UUID, user_id: uuid.UUID) -> int:
        """Count the total number of items in a specific user's todo list.

        Args:
            todo_id (uuid.UUID): The ID of the todo list to count items for.
            user_id (uuid.UUID): The ID of the user who owns the todo list.

        Returns:
            int: Total number of items in the todo list if owned by user, 0 otherwise.

        """
        query = (
            select(func.count())
            .select_from(TodoListItemModel)
            .join(TodoListModel, TodoListItemModel.todo_id == TodoListModel.id)
            .where(TodoListModel.id == todo_id, TodoListModel.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one()
