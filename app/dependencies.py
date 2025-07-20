"""
Dependency injection module for FastAPI.
This module provides dependencies that can be injected into route handlers.
"""

from app.services.todo_service import TodoService
from app.repositories.todo_mem_repo_impl import TodoMemoryRepository
from app.repositories.todo_pg_repo_impl import TodoPGRepository
from app.config.database import database
from app.config.settings import SETTINGS

# Global instances - initialized once and reused
_todo_repository = None
_todo_service = None


async def get_todo_service() -> TodoService:
    """
    Get the TodoService instance.
    
    This function creates a singleton TodoService that can be injected
    into route handlers using FastAPI's Depends.
    
    Returns:
        TodoService: The todo service instance
    """
    global _todo_service, _todo_repository
    
    if _todo_service is None:
        # Choose repository based on database configuration
        if database:
            _todo_repository = TodoPGRepository(database)
        else:
            _todo_repository = TodoMemoryRepository()
        _todo_service = TodoService(_todo_repository)
    
    return _todo_service
