"""Todo Models Module.

This module defines the data models for todos, including todo lists and todo list items.
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.user_model import Base 


class TodoListModel(Base):
    """SQLAlchemy Todo model - represents the todos table."""

    __tablename__ = "todos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    todo_items = relationship("TodoListItemModel", back_populates="todo", cascade="all, delete-orphan")
    user = relationship("UserModel", back_populates="todos")


class TodoListItemModel(Base):
    """SQLAlchemy Todo Item model - represents the todo_items table."""

    __tablename__ = "todo_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    todo_id = Column(UUID(as_uuid=True), ForeignKey("todos.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    todo = relationship("TodoListModel", back_populates="todo_items")
