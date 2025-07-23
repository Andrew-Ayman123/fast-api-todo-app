"""Unit tests for TodoPGRepository.

This module contains unit tests for the TodoPGRepository using a concrete
test implementation to verify the expected behavior of all repository methods.
"""
import uuid
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.sql import text

from app.models.todo_model import TodoListItemModel, TodoListModel
from app.models.user_model import UserModel
from app.repositories.todo_pg_repository_impl import TodoPGRepository
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)
from tests.test_dependencies import get_session_maker_test


class TestTodoRepository:
    """Test suite for TodoPGRepository."""

    @pytest_asyncio.fixture
    async def todo_repo(self) -> AsyncGenerator[TodoPGRepository, None]:
        """Create a fresh test repository instance for each test."""
        session_maker = get_session_maker_test()
        async with session_maker() as session:
            repo = TodoPGRepository(session=session)
            yield repo

    user_id: uuid.UUID | None = None

    @pytest_asyncio.fixture
    async def sample_user_id(self, todo_repo: TodoPGRepository) -> uuid.UUID:
        """Sample user ID for testing."""
        if self.user_id is not None:
            return self.user_id
        user = UserModel(username="Test User", email="testuser21@example.com", password="hashed")  # noqa: S106
        todo_repo.session.add(user)
        await todo_repo.session.commit()
        await todo_repo.session.refresh(user)
        self.user_id = user.id
        return user.id

    @pytest.fixture
    def sample_todo_data(self) -> dict[str, Any]:
        """Sample todo list data for testing."""
        return {"title": "Test Todo", "description": "Test Description"}

    @pytest.fixture
    def sample_todo_item_data(self) -> dict[str, Any]:
        """Sample todo item data for testing."""
        return {"title": "Test Item", "description": "Test Item Description"}

    @pytest_asyncio.fixture(autouse=True)
    async def cleanup_tables(self, todo_repo: TodoPGRepository) -> AsyncGenerator[None, None]:
        """Automatically clear the todo tables before and after each test."""
        yield
        await todo_repo.session.execute(text("DELETE FROM todo_items"))
        await todo_repo.session.execute(text("DELETE FROM todos"))
        await todo_repo.session.execute(text("DELETE FROM users"))
        await todo_repo.session.commit()

    @pytest.mark.asyncio
    async def test_create_todo_list_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test successful todo list creation."""
        todo_create = TodoListCreateRequest(**sample_todo_data)
        result = await todo_repo.create_todo_list(todo_create, sample_user_id)

        assert result is not None
        assert isinstance(result, TodoListModel)
        assert result.title == sample_todo_data["title"]
        assert result.description == sample_todo_data["description"]
        assert result.user_id == sample_user_id
        assert isinstance(result.id, uuid.UUID)
        assert result.todo_items == []  # Should be empty list for new todo

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test successful todo list retrieval by ID."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Retrieve the todo by ID
        result = await todo_repo.get_todo_list_by_id(created_todo.id, sample_user_id)

        assert result is not None
        assert result.id == created_todo.id
        assert result.title == sample_todo_data["title"]
        assert result.description == sample_todo_data["description"]
        assert result.user_id == sample_user_id

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id_not_found(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
    ) -> None:
        """Test todo list retrieval by ID when todo doesn't exist."""
        non_existent_id = uuid.uuid4()

        result = await todo_repo.get_todo_list_by_id(non_existent_id, sample_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id_wrong_user(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test todo list retrieval by ID when user doesn't own the todo."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Try to retrieve with different user
        wrong_user_id = uuid.uuid4()
        result = await todo_repo.get_todo_list_by_id(created_todo.id, wrong_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_todo_lists_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
    ) -> None:
        """Test successful retrieval of all todo lists for a user."""
        # Create multiple todos
        todos_data = [
            {"title": "Todo 1", "description": "Desc 1"},
            {"title": "Todo 2", "description": "Desc 2"},
            {"title": "Todo 3", "description": "Desc 3"},
        ]

        created_todos = []
        for todo_data in todos_data:
            todo_create = TodoListCreateRequest(**todo_data)
            todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
            assert todo is not None
            created_todos.append(todo)

        # Retrieve all todos
        result = await todo_repo.get_all_todo_lists(sample_user_id)

        assert len(result) == len(todos_data)

    @pytest.mark.asyncio
    async def test_get_all_todo_lists_empty(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
    ) -> None:
        """Test retrieval of all todo lists when user has none."""
        result = await todo_repo.get_all_todo_lists(sample_user_id)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_update_todo_list_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test successful todo list update."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Update the todo
        update_data = {"title": "Updated Title", "description": "Updated Description"}
        todo_update = TodoListUpdateRequest(**update_data)
        result = await todo_repo.update_todo_list(created_todo.id, todo_update, sample_user_id)

        assert result is not None
        assert result.id == created_todo.id
        assert result.title == update_data["title"]
        assert result.description == update_data["description"]
        assert result.user_id == sample_user_id

    @pytest.mark.asyncio
    async def test_update_todo_list_not_found(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
    ) -> None:
        """Test todo list update when todo doesn't exist."""
        non_existent_id = uuid.uuid4()
        update_data = {"title": "Updated Title"}
        todo_update = TodoListUpdateRequest(**update_data)

        result = await todo_repo.update_todo_list(non_existent_id, todo_update, sample_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_todo_list_wrong_user(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test todo list update when user doesn't own the todo."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Try to update with different user
        wrong_user_id = uuid.uuid4()
        update_data = {"title": "Updated Title"}
        todo_update = TodoListUpdateRequest(**update_data)
        result = await todo_repo.update_todo_list(created_todo.id, todo_update, wrong_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_todo_list_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test successful todo list deletion."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Delete the todo
        result = await todo_repo.delete_todo_list(created_todo.id, sample_user_id)

        assert result is True

        # Verify it's gone
        deleted_todo = await todo_repo.get_todo_list_by_id(created_todo.id, sample_user_id)
        assert deleted_todo is None

    @pytest.mark.asyncio
    async def test_delete_todo_list_not_found(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
    ) -> None:
        """Test todo list deletion when todo doesn't exist."""
        non_existent_id = uuid.uuid4()

        result = await todo_repo.delete_todo_list(non_existent_id, sample_user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_todo_list_wrong_user(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test todo list deletion when user doesn't own the todo."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Try to delete with different user
        wrong_user_id = uuid.uuid4()
        result = await todo_repo.delete_todo_list(created_todo.id, wrong_user_id)

        assert result is False

        # Verify it still exists
        existing_todo = await todo_repo.get_todo_list_by_id(created_todo.id, sample_user_id)
        assert existing_todo is not None

    @pytest.mark.asyncio
    async def test_add_todo_list_item_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
        sample_todo_item_data: dict[str, Any],
    ) -> None:
        """Test successful todo item addition."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Add an item
        item_add = TodoListItemsAddRequest(**sample_todo_item_data)
        result = await todo_repo.add_todo_list_item(created_todo.id, item_add, sample_user_id)

        assert result is not None
        assert isinstance(result, TodoListItemModel)
        assert result.title == sample_todo_item_data["title"]
        assert result.description == sample_todo_item_data["description"]
        assert result.todo_id == created_todo.id
        assert result.completed is False
        assert isinstance(result.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_add_todo_list_item_todo_not_found(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_item_data: dict[str, Any],
    ) -> None:
        """Test todo item addition when todo doesn't exist."""
        non_existent_todo_id = uuid.uuid4()
        item_add = TodoListItemsAddRequest(**sample_todo_item_data)

        result = await todo_repo.add_todo_list_item(non_existent_todo_id, item_add, sample_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_add_todo_list_item_wrong_user(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
        sample_todo_item_data: dict[str, Any],
    ) -> None:
        """Test todo item addition when user doesn't own the todo."""
        # Create a todo first
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Try to add item with different user
        wrong_user_id = uuid.uuid4()
        item_add = TodoListItemsAddRequest(**sample_todo_item_data)
        result = await todo_repo.add_todo_list_item(created_todo.id, item_add, wrong_user_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_todo_list_items_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test successful retrieval of todo items."""
        # Create a todo with items
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Add items
        items_data = [
            {"title": "Item 1", "description": "Desc 1"},
            {"title": "Item 2", "description": "Desc 2"},
            {"title": "Item 3", "description": "Desc 3"},
        ]

        for item_data in items_data:
            item_add = TodoListItemsAddRequest(**item_data)
            await todo_repo.add_todo_list_item(created_todo.id, item_add, sample_user_id)

        # Retrieve items
        result = await todo_repo.get_todo_list_items(created_todo.id, sample_user_id)

        assert len(result) == len(items_data)
        for i, item in enumerate(result):
            assert item.title == items_data[i]["title"]
            assert item.description == items_data[i]["description"]
            assert item.todo_id == created_todo.id

    @pytest.mark.asyncio
    async def test_get_todo_list_items_empty(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test retrieval of todo items when todo has none."""
        # Create a todo with no items
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        result = await todo_repo.get_todo_list_items(created_todo.id, sample_user_id)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_update_todo_list_item_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
        sample_todo_item_data: dict[str, Any],
    ) -> None:
        """Test successful todo item update."""
        # Create a todo with item
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        item_add = TodoListItemsAddRequest(**sample_todo_item_data)
        created_item = await todo_repo.add_todo_list_item(created_todo.id, item_add, sample_user_id)
        assert created_item is not None

        # Update the item
        item_update = TodoListItemUpdateRequest(
            title="Updated Title",
            description="Updated Desc",
            completed=True,
        )
        result = await todo_repo.update_todo_list_item(created_todo.id, created_item.id, item_update, sample_user_id)

        assert result is not None
        assert result.id == created_item.id
        assert result.title == item_update.title
        assert result.description == item_update.description
        assert result.completed == item_update.completed
        assert result.todo_id == created_todo.id

    @pytest.mark.asyncio
    async def test_update_todo_list_item_not_found(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test todo item update when item doesn't exist."""
        # Create a todo
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        non_existent_item_id = uuid.uuid4()
        item_update = TodoListItemUpdateRequest(title="Update Title")

        result = await todo_repo.update_todo_list_item(
            created_todo.id, non_existent_item_id, item_update, sample_user_id,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_todo_list_item_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
        sample_todo_item_data: dict[str, Any],
    ) -> None:
        """Test successful todo item deletion."""
        # Create a todo with item
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        item_add = TodoListItemsAddRequest(**sample_todo_item_data)
        created_item = await todo_repo.add_todo_list_item(created_todo.id, item_add, sample_user_id)
        assert created_item is not None

        # Delete the item
        result = await todo_repo.delete_todo_list_item(created_todo.id, created_item.id, sample_user_id)

        assert result is True

        # Verify it's gone
        items = await todo_repo.get_todo_list_items(created_todo.id, sample_user_id)
        assert len(items) == 0

    @pytest.mark.asyncio
    async def test_delete_todo_list_item_not_found(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test todo item deletion when item doesn't exist."""
        # Create a todo
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        non_existent_item_id = uuid.uuid4()

        result = await todo_repo.delete_todo_list_item(created_todo.id, non_existent_item_id, sample_user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_count_todo_lists_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
    ) -> None:
        """Test successful counting of todo lists."""
        # Initial count should be 0
        initial_count = await todo_repo.count_todo_lists(sample_user_id)
        assert initial_count == 0

        # Create some todos
        todos_data = [
            {"title": "Todo 1", "description": "Desc 1"},
            {"title": "Todo 2", "description": "Desc 2"},
        ]

        for todo_data in todos_data:
            todo_create = TodoListCreateRequest(**todo_data)
            await todo_repo.create_todo_list(todo_create, sample_user_id)

        # Verify count
        result = await todo_repo.count_todo_lists(sample_user_id)
        assert result == len(todos_data)

    @pytest.mark.asyncio
    async def test_count_todo_list_items_success(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
    ) -> None:
        """Test successful counting of todo items."""
        # Create a todo
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        # Initial count should be 0
        initial_count = await todo_repo.count_todo_list_items(created_todo.id, sample_user_id)
        assert initial_count == 0

        # Add some items
        items_data = [
            {"title": "Item 1", "description": "Desc 1"},
            {"title": "Item 2", "description": "Desc 2"},
        ]

        for item_data in items_data:
            item_add = TodoListItemsAddRequest(**item_data)
            await todo_repo.add_todo_list_item(created_todo.id, item_add, sample_user_id)

        # Verify count
        result = await todo_repo.count_todo_list_items(created_todo.id, sample_user_id)
        assert result == len(items_data)

    @pytest.mark.asyncio
    async def test_count_todo_list_items_wrong_user(
        self,
        todo_repo: TodoPGRepository,
        sample_user_id: uuid.UUID,
        sample_todo_data: dict[str, Any],
        sample_todo_item_data: dict[str, Any],
    ) -> None:
        """Test counting of todo items when user doesn't own the todo."""
        # Create a todo with items
        todo_create = TodoListCreateRequest(**sample_todo_data)
        created_todo = await todo_repo.create_todo_list(todo_create, sample_user_id)
        assert created_todo is not None

        item_add = TodoListItemsAddRequest(**sample_todo_item_data)
        await todo_repo.add_todo_list_item(created_todo.id, item_add, sample_user_id)

        # Try to count with different user
        wrong_user_id = uuid.uuid4()
        result = await todo_repo.count_todo_list_items(created_todo.id, wrong_user_id)

        assert result == 0
