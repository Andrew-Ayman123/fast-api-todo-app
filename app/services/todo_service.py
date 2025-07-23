"""Todo Service Module.

This module defines the TodoService class, which provides methods for managing todos
with user authorization.
"""

import uuid

from app.exceptions.todo_exception import TodoListItemNotFoundError, TodoListNotFoundError
from app.models.todo_model import TodoListItemModel, TodoListModel
from app.repositories.todo_repository_interface import TodoRepositoryInterface
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateItem,
    TodoListItemUpdateRequest,
    TodoListUpdateItem,
    TodoListUpdateRequest,
)
from app.utils.logger_util import get_logger


class TodoService:
    """Service class for managing todos with user authorization.

    Example:
        todo_service = TodoService(todo_repository=todo_repository_instance)
        new_todo = await todo_service.create_todo_list(todo_data, user_id)
        all_todos = await todo_service.get_all_todo_lists_without_items(user_id)

    """

    def __init__(self, todo_repository: TodoRepositoryInterface) -> None:
        """Initialize the TodoService with a repository instance.

        Args:
            todo_repository (TodoRepositoryInterface): An instance of TodoRepositoryInterface for database operations.

        """
        self.todo_repository = todo_repository

    async def create_todo_list(self, todo_data: TodoListCreateRequest, user_id: str) -> TodoListModel:
        """Create a new todo list for a user.

        Args:
            todo_data (TodoListCreateRequest): Data for creating a new todo list including title
                and optional description.
            user_id (str): ID of the user creating the todo list.

        Returns:
            TodoListModel: The created TodoListModel instance with assigned ID.

        """
        return await self.todo_repository.create_todo_list(todo_data, uuid.UUID(user_id))

    async def get_todo_list_by_id(self, todo_id: str, user_id: str) -> TodoListModel:
        """Get a todo list by ID for a specific user.

        Args:
            todo_id (str): ID of the todo list to retrieve.
            user_id (str): ID of the user requesting the todo list.

        Returns:
            TodoListModel: The TodoListModel instance.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to access this todo list.

        """
        todo = await self.todo_repository.get_todo_list_by_id(uuid.UUID(todo_id), uuid.UUID(user_id))
        if not todo:
            # Check if todo exists but belongs to another user
            # This is a simple approach - in a more secure system, you might not want to reveal
            # whether the todo exists at all for unauthorized users
            raise TodoListNotFoundError(uuid.UUID(todo_id))
        return todo

    async def get_all_todo_lists_without_items(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TodoListModel]:
        """Get all todo lists for a user with pagination (without their own list items).

        Args:
            user_id (str): ID of the user whose todo lists to retrieve.
            skip (int, optional): Number of records to skip for pagination. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListModel]: List of TodoListModel instances with pagination applied.

        """
        return await self.todo_repository.get_all_todo_lists(uuid.UUID(user_id), skip, limit)

    async def update_todo_list(
        self,
        todo_id: str,
        todo_data: TodoListUpdateRequest,
        user_id: str,
    ) -> TodoListModel:
        """Update an existing todo list for a specific user.

        Args:
            todo_id (str): ID of the todo list to update.
            todo_data (TodoListUpdateRequest): Updated data for the todo list.
            user_id (str): ID of the user updating the todo list.

        Returns:
            TodoListModel: The updated TodoListModel instance.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to update this todo list.

        """
        todo = await self.todo_repository.update_todo_list(uuid.UUID(todo_id), todo_data, uuid.UUID(user_id))
        if not todo:
            raise TodoListNotFoundError(uuid.UUID(todo_id))
        return todo

    async def delete_todo_list(self, todo_id: str, user_id: str) -> None:
        """Delete a todo list for a specific user.

        Args:
            todo_id (str): ID of the todo list to delete.
            user_id (str): ID of the user deleting the todo list.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to delete this todo list.

        """
        success = await self.todo_repository.delete_todo_list(uuid.UUID(todo_id), uuid.UUID(user_id))
        if not success:
            raise TodoListNotFoundError(uuid.UUID(todo_id))

    async def add_todo_list_item(
        self,
        todo_id: str,
        item_data: TodoListItemsAddRequest,
        user_id: str,
    ) -> TodoListItemModel:
        """Add a new item to a user's todo list.

        Args:
            todo_id (str): ID of the todo list to which the item will be added.
            item_data (TodoListItemsAddRequest): Data for the new todo item including title
                and optional description.
            user_id (str): ID of the user adding the item.

        Returns:
            TodoListItemModel: The created TodoListItemModel instance.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to add items to this todo list.

        """
        item = await self.todo_repository.add_todo_list_item(uuid.UUID(todo_id), item_data, uuid.UUID(user_id))
        if not item:
            raise TodoListNotFoundError(uuid.UUID(todo_id))
        return item

    async def get_todo_list_items(
        self,
        todo_id: str,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TodoListItemModel]:
        """Get all items for a user's todo list with pagination.

        Args:
            todo_id (str): ID of the todo list.
            user_id (str): ID of the user requesting the items.
            skip (int, optional): Number of records to skip for pagination. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.

        Returns:
            list[TodoListItemModel]: List of TodoListItemModel instances with pagination applied.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to access this todo list.

        """
        return await self.todo_repository.get_todo_list_items(uuid.UUID(todo_id), uuid.UUID(user_id), skip, limit)

    async def update_todo_item(
        self,
        todo_id: str,
        item_id: str,
        item_data: TodoListItemUpdateRequest,
        user_id: str,
    ) -> TodoListItemModel:
        """Update a specific item within a user's todo list.

        Args:
            todo_id (str): ID of the todo list containing the item.
            item_id (str): ID of the item to update.
            item_data (TodoListItemUpdateRequest): Updated data for the todo item.
            user_id (str): ID of the user updating the item.

        Returns:
            TodoListItemModel: The updated TodoListItemModel instance.

        Raises:
            TodoListItemNotFoundError: If the todo list or item with the given IDs is not found.
            UserNotAuthorizedError: If the user is not authorized to update this item.

        """
        item = await self.todo_repository.update_todo_list_item(
            uuid.UUID(todo_id),
            uuid.UUID(item_id),
            item_data,
            uuid.UUID(user_id),
        )
        if not item:
            raise TodoListItemNotFoundError(uuid.UUID(todo_id), uuid.UUID(item_id))

        return item

    async def delete_todo_list_item(self, todo_id: str, item_id: str, user_id: str) -> None:
        """Delete a todo item from a user's todo list.

        Args:
            todo_id (str): ID of the todo list.
            item_id (str): ID of the todo item to delete.
            user_id (str): ID of the user deleting the item.

        Raises:
            TodoListItemNotFoundError: If the todo list or item with the given IDs is not found.
            UserNotAuthorizedError: If the user is not authorized to delete this item.

        """
        success = await self.todo_repository.delete_todo_list_item(
            uuid.UUID(todo_id),
            uuid.UUID(item_id),
            uuid.UUID(user_id),
        )
        if not success:
            raise TodoListItemNotFoundError(uuid.UUID(todo_id), uuid.UUID(item_id))

    async def create_many_todo_lists(
        self,
        todo_lists: list[TodoListCreateRequest],
        user_id: str,
    ) -> list[TodoListModel]:
        """Create multiple todo lists for a user.

        Args:
            todo_lists (list[TodoListCreateRequest]): List of todo lists to create.
            user_id (str): ID of the user creating the todo lists.

        Returns:
            list[TodoListModel]: List of created todo lists.

        """
        created_todos = []
        for todo_data in todo_lists:
            created_todo = await self.todo_repository.create_todo_list(todo_data, uuid.UUID(user_id))
            created_todos.append(created_todo)
        return created_todos

    async def update_many_todo_lists(self, updates: list[TodoListUpdateItem], user_id: str) -> list[TodoListModel]:
        """Update multiple todo lists for a user.

        Args:
            updates (list): List of update objects with id and update data.
            user_id (str): ID of the user updating the todo lists.

        Returns:
            list[TodoListModel]: List of updated todo lists.

        Raises:
            TodoListNotFoundError: If any todo list with the given IDs is not found.
            UserNotAuthorizedError: If the user is not authorized to update any of the todo lists.

        """
        updated_todos = []
        for update in updates:
            todo_id = uuid.UUID(update.id)
            todo_data = update.data
            updated_todo = await self.todo_repository.update_todo_list(todo_id, todo_data, uuid.UUID(user_id))
            if not updated_todo:
                raise TodoListNotFoundError(todo_id)
            updated_todos.append(updated_todo)
        return updated_todos

    async def delete_many_todo_lists(self, todo_ids: list[str], user_id: str) -> None:
        """Delete multiple todo lists for a user.

        Args:
            todo_ids (list[str]): List of todo list IDs to delete.
            user_id (str): ID of the user deleting the todo lists.

        Raises:
            TodoListNotFoundError: If any todo list with the given IDs is not found.
            UserNotAuthorizedError: If the user is not authorized to delete any of the todo lists.

        """
        for todo_id in todo_ids:
            get_logger().debug("Deleting todo list with ID: %s for user: %s", todo_id, user_id)
            success = await self.todo_repository.delete_todo_list(uuid.UUID(todo_id), uuid.UUID(user_id))
            if not success:
                raise TodoListNotFoundError(uuid.UUID(todo_id))

    async def create_many_todo_list_items(
        self,
        todo_id: str,
        items: list[TodoListItemsAddRequest],
        user_id: str,
    ) -> list[TodoListItemModel]:
        """Add multiple items to a user's todo list.

        Args:
            todo_id (str): ID of the todo list to which the items will be added.
            items (list[TodoListItemsAddRequest]): List of todo items to add.
            user_id (str): ID of the user adding the items.

        Returns:
            list[TodoListItemModel]: List of created TodoListItemModel instances.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to add items to this todo list.

        """
        created_items = []
        for item_data in items:
            item = await self.todo_repository.add_todo_list_item(uuid.UUID(todo_id), item_data, uuid.UUID(user_id))
            if not item:
                raise TodoListNotFoundError(uuid.UUID(todo_id))
            created_items.append(item)
        return created_items

    async def update_many_todo_list_items(
        self,
        todo_id: str,
        updates: list[TodoListItemUpdateItem],
        user_id: str,
    ) -> list[TodoListItemModel]:
        """Update multiple items in a user's todo list.

        Args:
            todo_id (str): ID of the todo list containing the items to update.
            updates (list[TodoListItemUpdateItem]): List of update requests for the todo items.
            user_id (str): ID of the user updating the items.

        Returns:
            list[TodoListItemModel]: List of updated TodoListItemModel instances.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to update items in this todo list.

        """
        updated_items = []
        for update in updates:
            update_id = uuid.UUID(str(update.id))
            item = await self.todo_repository.update_todo_list_item(
                uuid.UUID(todo_id),
                update_id,
                update.data,
                uuid.UUID(user_id),
            )
            if not item:
                raise TodoListNotFoundError(uuid.UUID(todo_id))
            updated_items.append(item)
        return updated_items

    async def delete_many_todo_list_items(
        self,
        todo_id: str,
        item_ids: list[str],
        user_id: str,
    ) -> None:
        """Delete multiple items from a user's todo list.

        Args:
            todo_id (str): ID of the todo list containing the items to delete.
            item_ids (list[str]): List of item IDs to delete.
            user_id (str): ID of the user deleting the items.

        Raises:
            TodoListItemNotFoundError: If any item with the given IDs is not found in the todo list.
            UserNotAuthorizedError: If the user is not authorized to delete items from this todo list.

        """
        for item_id in item_ids:
            success = await self.todo_repository.delete_todo_list_item(
                uuid.UUID(todo_id),
                uuid.UUID(item_id),
                uuid.UUID(user_id),
            )
            if not success:
                raise TodoListItemNotFoundError(uuid.UUID(todo_id), uuid.UUID(item_id))

    async def count_todo_lists(self, user_id: str) -> int:
        """Count all todo lists for a specific user.

        Args:
            user_id (str): ID of the user whose todo lists to count.

        Returns:
            int: Total number of todo lists for the user.

        """
        return await self.todo_repository.count_todo_lists(uuid.UUID(user_id))

    async def count_todo_list_items(self, todo_id: str, user_id: str) -> int:
        """Count items in a user's specific todo list.

        Args:
            todo_id (str): ID of the todo list.
            user_id (str): ID of the user whose todo list items to count.

        Returns:
            int: Total number of items in the specified todo list.

        Raises:
            TodoListNotFoundError: If the todo list with the given ID is not found.
            UserNotAuthorizedError: If the user is not authorized to access this todo list.

        """
        return await self.todo_repository.count_todo_list_items(uuid.UUID(todo_id), uuid.UUID(user_id))
