"""Todo repository interface module.

This module defines the abstract interface for Todo repository operations,
providing a contract for different repository implementations.
"""
from abc import ABC, abstractmethod

from app.models.todo_model import TodoListItemModel, TodoListModel
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)


class TodoRepositoryInterface(ABC):
    """Abstract base class defining the interface for Todo repository operations."""

    @abstractmethod
    async def count_todo_lists(self) -> int:
        """Count the total number of todo lists in the database."""

    @abstractmethod
    async def count_todo_list_items(self, todo_id: int) -> int:
        """Count the total number of items in a specific todo list."""
    """Abstract base class defining the interface for Todo repository operations."""

    @abstractmethod
    async def create_todo_list(self, todo_data: TodoListCreateRequest) -> TodoListModel:
        """Create a new todo list.

        Args:
            todo_data (TodoListCreateRequest): The data for creating a new todo list.

        Returns:
            TodoListModel: The created todo list with assigned ID.

        """

    @abstractmethod
    async def get_todo_list_by_id(self, todo_id: int) -> TodoListModel | None:
        """Get a todo list by its ID.

        Args:
            todo_id (int): The ID of the todo list to retrieve.

        Returns:
            TodoListModel | None: The todo list if found, None otherwise.

        """

    @abstractmethod
    async def get_all_todo_lists(self, skip: int = 0, limit: int = 100) -> list[TodoListModel]:
        """Get all todo lists with pagination.

        Args:
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListModel]: List of todo lists.

        """

    @abstractmethod
    async def update_todo_list(self, todo_id: int, todo_data: TodoListUpdateRequest) -> TodoListModel | None:
        """Update an existing todo list.

        Args:
            todo_id (int): The ID of the todo list to update.
            todo_data (TodoListUpdateRequest): The update data for the todo list.

        Returns:
            TodoListModel | None: The updated todo list if found, None otherwise.

        """

    @abstractmethod
    async def delete_todo_list(self, todo_id: int) -> bool:
        """Delete a todo list by its ID.

        Args:
            todo_id (int): The ID of the todo list to delete.

        Returns:
            bool: True if the todo list was deleted, False if not found.

        """

    @abstractmethod
    async def add_todo_list_item(self, todo_id: int, item_data: TodoListItemsAddRequest) -> TodoListItemModel | None:
        """Add a new item to a todo list.

        Args:
            todo_id (int): The ID of the todo list to add the item to.
            item_data (TodoListItemsAddRequest): The data for the new todo item.

        Returns:
            TodoListItemModel | None: The created todo item if successful, None if todo list not found.

        """

    @abstractmethod
    async def get_todo_list_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> list[TodoListItemModel]:
        """Get all items from a todo list with pagination.

        Args:
            todo_id (int): The ID of the todo list to get items from.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListItemModel]: List of todo items.

        """

    @abstractmethod
    async def update_todo_list_item(
        self, todo_id: int, item_id: int, item_data: TodoListItemUpdateRequest,
    ) -> TodoListItemModel | None:
        """Update an existing todo list item.

        Args:
            todo_id (int): The ID of the todo list containing the item.
            item_id (int): The ID of the todo item to update.
            item_data (TodoListItemUpdateRequest): The update data for the todo item.

        Returns:
            TodoListItemModel | None: The updated todo item if found, None otherwise.

        """

    @abstractmethod
    async def delete_todo_list_item(self, todo_id: int, item_id: int) -> bool:
        """Delete a todo list item by its ID.

        Args:
            todo_id (int): The ID of the todo list containing the item.
            item_id (int): The ID of the todo item to delete.

        Returns:
            bool: True if the todo item was deleted, False if not found.

        """
