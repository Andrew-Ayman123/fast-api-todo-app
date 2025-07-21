"""Todo Service Module.

This module defines the TodoService class, which provides methods for managing todos.
It interacts with the TodoRepositoryInterface to perform CRUD operations on todos.
"""

from app.exceptions.todo_exception import TodoListItemNotFoundError, TodoListNotFoundError
from app.models.todo_model import TodoListItemModel, TodoListModel
from app.repositories.todo_repository_interface import TodoRepositoryInterface
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)


class TodoService:
    """Service class for managing todos.

    Example:
        todo_service = TodoService(todo_repository=todo_repository_instance)
        new_todo = await todo_service.create_todo_list(todo_data)
        all_todos = await todo_service.get_all_todo_lists_without_items()

    """

    def __init__(self, todo_repository: TodoRepositoryInterface) -> None:
        """Initialize the TodoService with a repository instance.

        Args:
            todo_repository (TodoRepositoryInterface): An instance of TodoRepositoryInterface for database operations.

        """
        self.todo_repository = todo_repository

    async def create_todo_list(self, todo_data: TodoListCreateRequest) -> TodoListModel:
        """Create a new todo list.

        Args:
            todo_data (TodoListCreateRequest): Data for creating a new todo list including title
                and optional description.

        Returns:
            TodoListModel: The created TodoListModel instance with assigned ID.

        """
        return await self.todo_repository.create_todo_list(todo_data)

    async def get_todo_list_by_id(self, todo_id: int) -> TodoListModel:
        """Get a todo list by ID.

        Args:
            todo_id (int): ID of the todo list to retrieve.

        Returns:
            TodoListModel: The TodoListModel instance.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.

        """
        todo = await self.todo_repository.get_todo_list_by_id(todo_id)
        if not todo:
            raise TodoListNotFoundError(todo_id)
        return todo

    async def get_all_todo_lists_without_items(self, skip: int = 0, limit: int = 100) -> list[TodoListModel]:
        """Get all todo lists with pagination (without their own list items).

        Args:
            skip (int, optional): Number of records to skip for pagination. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListModel]: List of TodoListModel instances with pagination applied.

        """
        return await self.todo_repository.get_all_todo_lists(skip, limit)

    async def update_todo_list(self, todo_id: int, todo_data: TodoListUpdateRequest) -> TodoListModel:
        """Update an existing todo list.

        Args:
            todo_id (int): ID of the todo list to update.
            todo_data (TodoListUpdateRequest): Updated data for the todo list.

        Returns:
            TodoListModel: The updated TodoListModel instance.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.

        """
        todo = await self.todo_repository.update_todo_list(todo_id, todo_data)
        if not todo:
            raise TodoListNotFoundError(todo_id)
        return todo

    async def delete_todo_list(self, todo_id: int) -> None:
        """Delete a todo list.

        Args:
            todo_id (int): ID of the todo list to delete.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.

        """
        success = await self.todo_repository.delete_todo_list(todo_id)
        if not success:
            raise TodoListNotFoundError(todo_id)


    async def add_todo_list_item(self, todo_id: int, item_data: TodoListItemsAddRequest) -> TodoListItemModel:
        """Add a new item to a todo list.

        Args:
            todo_id (int): ID of the todo list to which the item will be added.
            item_data (TodoListItemsAddRequest): Data for the new todo item including title
                and optional description.

        Returns:
            TodoListItemModel: The created TodoListItemModel instance.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.

        """
        item = await self.todo_repository.add_todo_list_item(todo_id, item_data)
        if not item:
            raise TodoListNotFoundError(todo_id)
        return item

    async def get_todo_list_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> list[TodoListItemModel]:
        """Get all items for a todo list with pagination.

        Args:
            todo_id (int): ID of the todo list.
            skip (int, optional): Number of records to skip for pagination. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListItemModel]: List of TodoListItemModel instances with pagination applied.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.

        """
        return await self.todo_repository.get_todo_list_items(todo_id, skip, limit)

    async def update_todo_item(
        self,
        todo_id: int,
        item_id: int,
        item_data: TodoListItemUpdateRequest,
    ) -> TodoListItemModel:
        """Update a specific item within a todo list.

        Args:
            todo_id (int): ID of the todo list containing the item.
            item_id (int): ID of the item to update.
            item_data (TodoListItemUpdateRequest): Partial Updated data for the todo item.

        Returns:
            TodoListItemModel: The updated TodoListItemModel instance.

        Raises:
            TodoListItemNotFoundError: If the todo list or item with the given IDs is not found.

        """
        item = await self.todo_repository.update_todo_list_item(todo_id, item_id, item_data)
        if not item:
            raise TodoListItemNotFoundError(todo_id, item_id)

        return item

    async def delete_todo_list_item(self, todo_id: int, item_id: int) -> None:
        """Delete a todo item from a todo list.

        Args:
            todo_id (int): ID of the todo list.
            item_id (int): ID of the todo item to delete.

        Raises:
            TodoListItemNotFoundError: If the todo list or item with the given IDs is not found.

        """
        success = await self.todo_repository.delete_todo_list_item(todo_id, item_id)
        if not success:
            raise TodoListItemNotFoundError(todo_id, item_id)

    async def create_many_todo_lists(self, todo_lists: list[TodoListCreateRequest]) -> list[TodoListModel]:
        """Create multiple todo lists.

        Args:
            todo_lists (list[TodoListCreateRequest]): List of todo lists to create.

        Returns:
            list[TodoListModel]: List of created todo lists.

        """
        created_todos = []
        for todo_data in todo_lists:
            created_todo = await self.todo_repository.create_todo_list(todo_data)
            created_todos.append(created_todo)
        return created_todos

    async def update_many_todo_lists(self, updates: list) -> list[TodoListModel]:
        """Update multiple todo lists.

        Args:
            updates (list): List of update objects with id and update data.

        Returns:
            list[TodoListModel]: List of updated todo lists.

        Raises:
            TodoListNotFoundError: If any todo list with the given IDs is not found.

        """
        updated_todos = []
        for update in updates:
            todo_id = update.id
            todo_data = update.data
            updated_todo = await self.todo_repository.update_todo_list(todo_id, todo_data)
            if not updated_todo:
                raise TodoListNotFoundError(todo_id)
            updated_todos.append(updated_todo)
        return updated_todos

    async def delete_many_todo_lists(self, todo_ids: list[int]) -> None:
        """Delete multiple todo lists.

        Args:
            todo_ids (list[int]): List of todo list IDs to delete.

        Raises:
            TodoListNotFoundError: If any todo list with the given IDs is not found.

        """
        for todo_id in todo_ids:
            success = await self.todo_repository.delete_todo_list(todo_id)
            if not success:
                raise TodoListNotFoundError(todo_id)

    async def create_many_todo_list_items(self, todo_id: int, items: list) -> list[TodoListItemModel]:
        """Add multiple items to a todo list.

        Args:
            todo_id (int): ID of the todo list to add items to.
            items (list): List of todo items to add.

        Returns:
            list[TodoListItemModel]: List of created todo list items.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.

        """
        created_items = []
        for item_data in items:
            created_item = await self.todo_repository.add_todo_list_item(todo_id, item_data)
            if not created_item:
                raise TodoListNotFoundError(todo_id)
            created_items.append(created_item)
        return created_items

    async def update_many_todo_list_items(self, todo_id: int, updates: list) -> list[TodoListItemModel]:
        """Update multiple todo list items.

        Args:
            todo_id (int): ID of the todo list containing the items.
            updates (list): List of update objects with id and update data.

        Returns:
            list[TodoListItemModel]: List of updated todo list items.

        Raises:
            TodoListItemNotFoundError: If any todo list item with the given IDs is not found.

        """
        updated_items = []
        for update in updates:
            item_id = update.id
            item_data = update.data
            updated_item = await self.todo_repository.update_todo_list_item(todo_id, item_id, item_data)
            if not updated_item:
                raise TodoListItemNotFoundError(todo_id, item_id)
            updated_items.append(updated_item)
        return updated_items

    async def delete_many_todo_list_items(self, todo_id: int, item_ids: list[int]) -> None:
        """Delete multiple todo list items.

        Args:
            todo_id (int): ID of the todo list containing the items.
            item_ids (list[int]): List of todo list item IDs to delete.

        Raises:
            TodoListItemNotFoundError: If any todo list item with the given IDs is not found.

        """
        for item_id in item_ids:
            success = await self.todo_repository.delete_todo_list_item(todo_id, item_id)
            if not success:
                raise TodoListItemNotFoundError(todo_id, item_id)

    async def count_todo_lists(self) -> int:
        """Count the total number of todo lists in the database."""
        return await self.todo_repository.count_todo_lists()

    async def count_todo_list_items(self, todo_id: int) -> int:
        """Count the total number of items in a specific todo list."""
        return await self.todo_repository.count_todo_list_items(todo_id)
