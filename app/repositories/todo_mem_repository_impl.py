"""In-memory implementation of Todo repository.

This module provides an in-memory implementation of the TodoRepositoryInterface
for testing and development purposes.
"""

from datetime import datetime

from app.models.todo_model import TodoListItemModel, TodoListModel
from app.repositories.todo_repository_interface import TodoRepositoryInterface
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)


class TodoMemoryRepository(TodoRepositoryInterface):
    """In-memory implementation of Todo repository using lists for storage."""

    def __init__(self) -> None:
        """Initialize the in-memory repository with empty storage."""
        self.todos: list[TodoListModel] = []
        self._next_todo_id = 1
        self._next_item_id = 1

    async def create_todo_list(self, todo_data: TodoListCreateRequest) -> TodoListModel:
        """Create a new todo list in memory.

        Args:
            todo_data (TodoListCreateRequest): The data for creating a new todo list.

        Returns:
            TodoListModel: The created todo list with assigned ID.

        """
        todo = TodoListModel(
            id=self._next_todo_id,
            title=todo_data.title,
            description=todo_data.description,
            todo_items=[],
        )
        self.todos.append(todo)
        self._next_todo_id += 1
        return todo

    async def get_todo_list_by_id(self, todo_id: int) -> TodoListModel | None:
        """Get a todo list by its ID from memory.

        Args:
            todo_id (int): The ID of the todo list to retrieve.

        Returns:
            TodoListModel | None: The todo list if found, None otherwise.

        """
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    async def get_all_todo_lists(self, skip: int = 0, limit: int = 100) -> list[TodoListModel]:
        """Get all todo lists with pagination from memory.

        Args:
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListModel]: List of todo lists.

        """
        return self.todos[skip : skip + limit]

    async def update_todo_list(self, todo_id: int, todo_data: TodoListUpdateRequest) -> TodoListModel | None:
        """Update an existing todo list in memory.

        Args:
            todo_id (int): The ID of the todo list to update.
            todo_data (TodoListUpdateRequest): The update data for the todo list.

        Returns:
            TodoListModel | None: The updated todo list if found, None otherwise.

        """
        todo = await self.get_todo_list_by_id(todo_id)
        if not todo:
            return None

        if todo_data.title is not None:
            todo.title = todo_data.title
        if todo_data.description is not None:
            todo.description = todo_data.description

        return todo

    async def delete_todo_list(self, todo_id: int) -> bool:
        """Delete a todo list by its ID from memory.

        Args:
            todo_id (int): The ID of the todo list to delete.

        Returns:
            bool: True if the todo list was deleted, False if not found.

        """
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                return True
        return False

    async def add_todo_list_item(self, todo_id: int, item_data: TodoListItemsAddRequest) -> TodoListItemModel | None:
        """Add a new item to a todo list in memory.

        Args:
            todo_id (int): The ID of the todo list to add the item to.
            item_data (TodoListItemsAddRequest): The data for the new todo item.

        Returns:
            TodoListItemModel | None: The created todo item if successful, None if todo list not found.

        """
        todo = await self.get_todo_list_by_id(todo_id)
        if not todo:
            return None

        item = TodoListItemModel(
            id=self._next_item_id,
            title=item_data.title,
            description=item_data.description,
            completed=False,
            created_at=datetime.now(tz=datetime.timezone.utc),
            updated_at=datetime.now(tz=datetime.timezone.utc),
        )
        todo.todo_items.append(item)
        self._next_item_id += 1
        return item

    async def get_todo_list_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> list[TodoListItemModel]:
        """Get all items from a todo list with pagination from memory.

        Args:
            todo_id (int): The ID of the todo list to get items from.
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListItemModel]: List of todo items.

        """
        todo = await self.get_todo_list_by_id(todo_id)
        if not todo:
            return []
        return todo.todo_items[skip : skip + limit]

    async def update_todo_list_item(
        self,
        todo_id: int,
        item_id: int,
        item_data: TodoListItemUpdateRequest,
    ) -> TodoListItemModel | None:
        """Update an existing todo list item in memory.

        Args:
            todo_id (int): The ID of the todo list containing the item.
            item_id (int): The ID of the todo item to update.
            item_data (TodoListItemUpdateRequest): The update data for the todo item.

        Returns:
            TodoListItemModel | None: The updated todo item if found, None otherwise.

        """
        todo = await self.get_todo_list_by_id(todo_id)
        if not todo:
            return None

        for item in todo.todo_items:
            if item.id == item_id:
                if item_data.title is not None:
                    item.title = item_data.title
                if item_data.description is not None:
                    item.description = item_data.description
                if item_data.completed is not None:
                    item.completed = item_data.completed
                item.updated_at = datetime.now(tz=datetime.timezone.utc)
                return item
        return None

    async def delete_todo_list_item(self, todo_id: int, item_id: int) -> bool:
        """Delete a todo list item by its ID from memory.

        Args:
            todo_id (int): The ID of the todo list containing the item.
            item_id (int): The ID of the todo item to delete.

        Returns:
            bool: True if the todo item was deleted, False if not found.

        """
        todo = await self.get_todo_list_by_id(todo_id)
        if not todo:
            return False

        for i, item in enumerate(todo.todo_items):
            if item.id == item_id:
                del todo.todo_items[i]
                return True
        return False
