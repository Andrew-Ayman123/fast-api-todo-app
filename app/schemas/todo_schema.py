"""Todo schema definitions for FastAPI application."""

from datetime import datetime
from typing import ClassVar

from pydantic import BaseModel


class BaseEntitySchema(BaseModel):
    """Base schema for entities with common fields.

    Args:
        id (int): Unique identifier of the entity.
        created_at (datetime): Timestamp when the entity was created.
        updated_at (datetime): Timestamp when the entity was last updated.

    """

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}


class TodoListCreateRequest(BaseModel):
    """Schema for creating a new todo list.

    Args:
        title (str): The title of the todo list.
        description (str | None, optional): Optional description of the todo list. Defaults to None.

    """

    title: str
    description: str | None = None


class TodoListUpdateRequest(BaseModel):
    """Schema for updating an existing todo list.

    Args:
        title (str, optional): Updated title of the todo list. Defaults to None.
        description (str, optional): Updated description of the todo list. Defaults to None.

    """

    title: str | None = None
    description: str | None = None


class TodoListItemsAddRequest(BaseModel):
    """Schema for adding a new item to a todo list.

    Args:
        title (str): The title of the todo item.
        description (str, optional): Optional description of the todo item. Defaults to None.

    """

    title: str
    description: str | None = None


class TodoListItemUpdateRequest(BaseModel):
    """Schema for updating an existing todo list item.

    Args:
        title (str, optional): Updated title of the todo item. Defaults to None.
        description (str, optional): Updated description of the todo item. Defaults to None.
        completed (bool, optional): Updated completion status of the todo item. Defaults to None.

    """

    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TodoListItemResponse(BaseEntitySchema):
    """Schema for todo list item response data.

    Args:
        title (str): The title of the todo item.
        description (str, optional): Optional description of the todo item. Defaults to None.
        completed (bool): Completion status of the todo item. Defaults to False.

    """

    title: str
    description: str | None = None
    completed: bool = False


class TodoListResponse(BaseEntitySchema):
    """Schema for todo list response data.

    Args:
        title (str): The title of the todo list.
        description (str, optional): Optional description of the todo list. Defaults to None.
        todo_items (list[TodoListItemResponse], optional): List of todo items in this todo list. Defaults to None.

    """

    title: str
    description: str | None = None
    todo_items: list[TodoListItemResponse] | None = None


class TodoListCreateManyRequest(BaseModel):
    """Schema for creating multiple todo lists.

    Args:
        todo_lists (list[TodoListCreateRequest]): List of todo lists to create.

    """

    todo_lists: list[TodoListCreateRequest]


class TodoListUpdateItem(BaseModel):
    """Schema for updating a single todo list in batch operation.

    Args:
        id (int): ID of the todo list to update.
        data (TodoListUpdateRequest): Update data for the todo list.

    """

    id: int
    data: TodoListUpdateRequest


class TodoListUpdateManyRequest(BaseModel):
    """Schema for updating multiple todo lists.

    Args:
        updates (list[TodoListUpdateItem]): List of update objects with id and update data.

    """

    updates: list[TodoListUpdateItem]


class TodoListDeleteManyRequest(BaseModel):
    """Schema for deleting multiple todo lists.

    Args:
        todo_ids (list[int]): List of todo list IDs to delete.

    """

    todo_ids: list[int]


class TodoListItemCreateManyRequest(BaseModel):
    """Schema for adding multiple items to a todo list.

    Args:
        todo_id (int): ID of the todo list to add items to.
        items (list[TodoListItemsAddRequest]): List of todo items to add.

    """

    todo_id: int
    items: list[TodoListItemsAddRequest]


class TodoListItemUpdateItem(BaseModel):
    """Schema for updating a single todo list item in batch operation.

    Args:
        id (int): ID of the todo list item to update.
        data (TodoListItemUpdateRequest): Update data for the todo list item.

    """

    id: int
    data: TodoListItemUpdateRequest


class TodoListItemUpdateManyRequest(BaseModel):
    """Schema for updating multiple todo list items.

    Args:
        todo_id (int): ID of the todo list containing the items.
        updates (list[TodoListItemUpdateItem]): List of update objects with id and update data.

    """

    todo_id: int
    updates: list[TodoListItemUpdateItem]


class TodoListItemDeleteManyRequest(BaseModel):
    """Schema for deleting multiple todo list items.

    Args:
        todo_id (int): ID of the todo list containing the items.
        item_ids (list[int]): List of todo list item IDs to delete.

    """

    todo_id: int
    item_ids: list[int]


class SuccessResponse(BaseModel):
    """Schema for success response.

    Args:
        success (bool): Indicates if the operation was successful.
        message (str): Success message.

    """

    success: bool = True
    message: str
