"""Todo Models Module.

This module defines the data models for todos, including todo lists and todo list items.
"""

# models/__init__.py
from app.models.user_model import UserModel
from app.models.todo_model import TodoListModel,TodoListItemModel
from app.models.user_model import Base  # Shared declarative base

__all__ = ['UserModel', 'TodoListModel', 'TodoListItemModel', 'Base']
