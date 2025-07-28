"""Todo repository interface module.

This module defines the abstract interface for Todo repository operations,
providing a contract for different repository implementations.
"""

import uuid
from abc import ABC, abstractmethod
from typing import TypeVar

from sqlalchemy.sql import Select

from app.models.todo_model import TodoListItemModel, TodoListModel
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)

T = TypeVar("T")


class TodoRepositoryInterface(ABC):
    """Abstract base class defining the interface for Todo repository operations."""

    @abstractmethod
    async def _fetch_one(self, query: Select[tuple[T]]) -> T | None:
        """Execute a SELECT query to fetch a single record."""

    @abstractmethod
    async def _fetch_all(self, query: Select[tuple[T]]) -> list[T]:
        """Execute a SELECT query to fetch multiple records."""

    @abstractmethod
    async def create_todo_list(self, todo_data: TodoListCreateRequest, user_id: uuid.UUID) -> TodoListModel:
        """Create a new todo list for a specific user."""

    @abstractmethod
    async def get_todo_list_by_id(self, todo_id: uuid.UUID, user_id: uuid.UUID) -> TodoListModel | None:
        """Get a todo list by its ID for a specific user."""

    @abstractmethod
    async def get_all_todo_lists(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TodoListModel]:
        """Retrieve all todo lists for a user with pagination."""

    @abstractmethod
    async def update_todo_list(
        self,
        todo_id: uuid.UUID,
        todo_data: TodoListUpdateRequest,
        user_id: uuid.UUID,
    ) -> TodoListModel | None:
        """Update a user's todo list by ID."""

    @abstractmethod
    async def delete_todo_list(self, todo_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a user's todo list by ID."""

    @abstractmethod
    async def add_todo_list_item(
        self,
        todo_id: uuid.UUID,
        item_data: TodoListItemsAddRequest,
        user_id: uuid.UUID,
    ) -> TodoListItemModel | None:
        """Add an item to a user's todo list."""

    @abstractmethod
    async def get_todo_list_items(
        self,
        todo_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TodoListItemModel]:
        """Get items from a user's todo list with pagination."""

    @abstractmethod
    async def update_todo_list_item(
        self,
        todo_id: uuid.UUID,
        item_id: uuid.UUID,
        item_data: TodoListItemUpdateRequest,
        user_id: uuid.UUID,
    ) -> TodoListItemModel | None:
        """Update a user's todo item in a specific todo list."""

    @abstractmethod
    async def delete_todo_list_item(
        self,
        todo_id: uuid.UUID,
        item_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Delete a user's todo item from a todo list."""

    @abstractmethod
    async def count_todo_lists(self, user_id: uuid.UUID) -> int:
        """Count all todo lists for a specific user."""

    @abstractmethod
    async def count_todo_list_items(self, todo_id: uuid.UUID, user_id: uuid.UUID) -> int:
        """Count items in a user's specific todo list."""
