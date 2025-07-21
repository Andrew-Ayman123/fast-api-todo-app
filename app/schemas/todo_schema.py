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
