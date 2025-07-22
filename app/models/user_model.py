"""User Model Module.

Defines the UserModel for authentication and ownership of todos.
"""

import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class UserModel(Base):
    """SQLAlchemy User model - represents the users table."""

    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    email = Column(String(200), unique=True, nullable=False)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    todos = relationship("TodoListModel", back_populates="user")
