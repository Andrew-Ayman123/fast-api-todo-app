"""Integration tests for TodoPGRepository using real database connection."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import text

from app.config.database import DatabaseConnection
from app.dependencies import get_database
from app.repositories.todo_pg_repository_impl import TodoPGRepository
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)


class TestTodoPGRepository:
    """Integration tests for TodoPGRepository with real database connection."""

    @pytest_asyncio.fixture(autouse=True)
    async def cleanup_database(self, database: DatabaseConnection):
        """Clean up database after each test to ensure clean state."""
        yield  # This runs the test first

        # Clean up after test
        session = await database.get_session().__anext__()
        try:
            # Delete in correct order due to foreign key constraints
            await session.execute(text("DELETE FROM todo_items"))
            await session.execute(text("DELETE FROM todos"))
            await session.commit()
        finally:
            await session.close()


    @pytest_asyncio.fixture(scope="function")
    async def database(self) -> AsyncGenerator[DatabaseConnection, None]:
        """Create a test database connection.

        Uses environment variables for test database configuration.
        Ensure you have a test database set up before running these tests.
        """
        # Create database connection with logging disabled for cleaner test output
        db = get_database()

        yield db

        await db.close()

    @pytest_asyncio.fixture
    async def repository(self, database: DatabaseConnection) -> TodoPGRepository:
        """Create TodoPGRepository instance with test database."""
        return TodoPGRepository(database)

    @pytest_asyncio.fixture
    async def sample_todo_data(self) -> TodoListCreateRequest:
        """Sample todo data for testing."""
        return TodoListCreateRequest(
            title="Test Todo List",
            description="A test todo list for testing purposes",
        )

    @pytest_asyncio.fixture
    async def sample_todo_item_data(self) -> TodoListItemsAddRequest:
        """Sample todo item data for testing."""
        return TodoListItemsAddRequest(
            title="Test Todo Item",
            description="A test todo item for testing purposes",
        )

    @pytest.mark.asyncio
    async def test_create_todo_list_success(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test successful creation of a todo list."""
        # Act
        result = await repository.create_todo_list(sample_todo_data)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.title == sample_todo_data.title
        assert result.description == sample_todo_data.description
        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.todo_items == []  # New todo should have empty items list

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id_existing(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test retrieving an existing todo list by ID."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)

        # Act
        result = await repository.get_todo_list_by_id(created_todo.id)

        # Assert
        assert result is not None
        assert result.id == created_todo.id
        assert result.title == sample_todo_data.title
        assert result.description == sample_todo_data.description
        assert result.todo_items == []

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id_non_existing(self, repository: TodoPGRepository) -> None:
        """Test retrieving a non-existing todo list by ID."""
        # Act
        result = await repository.get_todo_list_by_id(999999)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_todo_lists_empty(self, repository: TodoPGRepository) -> None:
        """Test retrieving all todo lists when database is empty."""
        # Act
        result = await repository.get_all_todo_lists()

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_todo_lists_with_data(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test retrieving all todo lists with existing data."""
        # Arrange
        todo1 = await repository.create_todo_list(sample_todo_data)
        todo2_data = TodoListCreateRequest(title="Second Todo", description="Second description")
        todo2 = await repository.create_todo_list(todo2_data)

        # Act
        result = await repository.get_all_todo_lists()

        # Assert
        assert len(result) == 2
        todo_ids = [todo.id for todo in result]
        assert todo1.id in todo_ids
        assert todo2.id in todo_ids

    @pytest.mark.asyncio
    async def test_get_all_todo_lists_with_pagination(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test retrieving all todo lists with pagination."""
        # Arrange
        for i in range(5):
            todo_data = TodoListCreateRequest(title=f"Todo {i}", description=f"Description {i}")
            await repository.create_todo_list(todo_data)

        # Act
        result_page1 = await repository.get_all_todo_lists(skip=0, limit=2)
        result_page2 = await repository.get_all_todo_lists(skip=2, limit=2)

        # Assert
        assert len(result_page1) == 2
        assert len(result_page2) == 2
        # Ensure no overlap between pages
        page1_ids = {todo.id for todo in result_page1}
        page2_ids = {todo.id for todo in result_page2}
        assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_update_todo_list_success(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test successful update of a todo list."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        update_data = TodoListUpdateRequest(
            title="Updated Title",
            description="Updated Description",
        )

        # Act
        result = await repository.update_todo_list(created_todo.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_todo.id
        assert result.title == "Updated Title"
        assert result.description == "Updated Description"
        assert result.updated_at > created_todo.updated_at

    @pytest.mark.asyncio
    async def test_update_todo_list_partial(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test partial update of a todo list."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        update_data = TodoListUpdateRequest(title="Updated Title Only")

        # Act
        result = await repository.update_todo_list(created_todo.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_todo.id
        assert result.title == "Updated Title Only"
        assert result.description == sample_todo_data.description  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_todo_list_non_existing(self, repository: TodoPGRepository) -> None:
        """Test updating a non-existing todo list."""
        # Arrange
        update_data = TodoListUpdateRequest(title="Non-existing")

        # Act
        result = await repository.update_todo_list(999999, update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_todo_list_no_changes(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test updating a todo list with no actual changes."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        update_data = TodoListUpdateRequest()  # No fields set

        # Act
        result = await repository.update_todo_list(created_todo.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_todo.id
        assert result.title == created_todo.title
        assert result.description == created_todo.description

    @pytest.mark.asyncio
    async def test_delete_todo_list_success(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test successful deletion of a todo list."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)

        # Act
        result = await repository.delete_todo_list(created_todo.id)

        # Assert
        assert result is True

        # Verify it's actually deleted
        deleted_todo = await repository.get_todo_list_by_id(created_todo.id)
        assert deleted_todo is None

    @pytest.mark.asyncio
    async def test_delete_todo_list_non_existing(self, repository: TodoPGRepository) -> None:
        """Test deleting a non-existing todo list."""
        # Act
        result = await repository.delete_todo_list(999999)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_add_todo_list_item_success(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test successful addition of a todo item to a todo list."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)

        # Act
        result = await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.todo_id == created_todo.id
        assert result.title == sample_todo_item_data.title
        assert result.description == sample_todo_item_data.description
        assert result.completed is False
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_add_todo_list_item_to_non_existing_todo(
        self,
        repository: TodoPGRepository,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test adding a todo item to a non-existing todo list."""
        # Act
        result = await repository.add_todo_list_item(999999, sample_todo_item_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_todo_list_items_empty(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test retrieving todo items from an empty todo list."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)

        # Act
        result = await repository.get_todo_list_items(created_todo.id)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_todo_list_items_with_data(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test retrieving todo items with existing data."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        item1 = await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)
        item2_data = TodoListItemsAddRequest(title="Second Item", description="Second description")
        item2 = await repository.add_todo_list_item(created_todo.id, item2_data)

        # Act
        result = await repository.get_todo_list_items(created_todo.id)

        # Assert
        assert len(result) == 2
        item_ids = [item.id for item in result]
        assert item1.id in item_ids
        assert item2.id in item_ids

    @pytest.mark.asyncio
    async def test_get_todo_list_items_from_non_existing_todo(
        self,
        repository: TodoPGRepository,
    ) -> None:
        """Test retrieving todo items from a non-existing todo list."""
        # Act
        result = await repository.get_todo_list_items(999999)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_todo_list_items_with_pagination(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test retrieving todo items with pagination."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        for i in range(5):
            item_data = TodoListItemsAddRequest(title=f"Item {i}", description=f"Description {i}")
            await repository.add_todo_list_item(created_todo.id, item_data)

        # Act
        result_page1 = await repository.get_todo_list_items(created_todo.id, skip=0, limit=2)
        result_page2 = await repository.get_todo_list_items(created_todo.id, skip=2, limit=2)

        # Assert
        assert len(result_page1) == 2
        assert len(result_page2) == 2

    @pytest.mark.asyncio
    async def test_update_todo_list_item_success(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test successful update of a todo item."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        created_item = await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)
        update_data = TodoListItemUpdateRequest(
            title="Updated Item",
            description="Updated Description",
            completed=True,
        )

        # Act
        result = await repository.update_todo_list_item(created_todo.id, created_item.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_item.id
        assert result.title == "Updated Item"
        assert result.description == "Updated Description"
        assert result.completed is True

    @pytest.mark.asyncio
    async def test_update_todo_list_item_partial(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test partial update of a todo item."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        created_item = await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)
        update_data = TodoListItemUpdateRequest(completed=True)

        # Act
        result = await repository.update_todo_list_item(created_todo.id, created_item.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_item.id
        assert result.title == sample_todo_item_data.title  # Should remain unchanged
        assert result.description == sample_todo_item_data.description  # Should remain unchanged
        assert result.completed is True

    @pytest.mark.asyncio
    async def test_update_todo_list_item_non_existing(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test updating a non-existing todo item."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        update_data = TodoListItemUpdateRequest(title="Non-existing")

        # Act
        result = await repository.update_todo_list_item(created_todo.id, 999999, update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_todo_list_item_wrong_todo(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test updating a todo item with wrong todo_id."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        created_item = await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)
        update_data = TodoListItemUpdateRequest(title="Wrong Todo")

        # Act
        result = await repository.update_todo_list_item(999999, created_item.id, update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_todo_list_item_success(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test successful deletion of a todo item."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        created_item = await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)

        # Act
        result = await repository.delete_todo_list_item(created_todo.id, created_item.id)

        # Assert
        assert result is True

        # Verify it's actually deleted
        items = await repository.get_todo_list_items(created_todo.id)
        assert len(items) == 0

    @pytest.mark.asyncio
    async def test_delete_todo_list_item_non_existing(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Test deleting a non-existing todo item."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)

        # Act
        result = await repository.delete_todo_list_item(created_todo.id, 999999)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_todo_list_item_wrong_todo(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test deleting a todo item with wrong todo_id."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        created_item = await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)

        # Act
        result = await repository.delete_todo_list_item(999999, created_item.id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_cascade_delete_todo_items_when_todo_deleted(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Test that todo items are deleted when their parent todo is deleted."""
        # Arrange
        created_todo = await repository.create_todo_list(sample_todo_data)
        await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)
        await repository.add_todo_list_item(created_todo.id, sample_todo_item_data)

        # Verify items exist
        items_before = await repository.get_todo_list_items(created_todo.id)


        # Act - Delete the todo list
        result = await repository.delete_todo_list(created_todo.id)

        # Assert
        assert len(items_before) == 2
        assert result is True

        # Verify items are also deleted (should return empty list for non-existent todo)
        items_after = await repository.get_todo_list_items(created_todo.id)
        assert len(items_after) == 0

    @pytest.mark.asyncio
    async def test_multiple_todo_list_operations_integration(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
    ) -> None:
        """Integration test for creating, updating, and deleting multiple todo lists."""
        # Create multiple todo lists
        todo1 = await repository.create_todo_list(sample_todo_data)
        todo2_data = TodoListCreateRequest(title="Second Todo", description="Second description")
        todo2 = await repository.create_todo_list(todo2_data)
        todo3_data = TodoListCreateRequest(title="Third Todo", description="Third description")
        todo3 = await repository.create_todo_list(todo3_data)

        # Verify all created
        assert todo1.id is not None
        assert todo2.id is not None
        assert todo3.id is not None

        # Update multiple
        update_data = TodoListUpdateRequest(title="Updated Title", description="Updated description")
        updated1 = await repository.update_todo_list(todo1.id, update_data)
        updated2 = await repository.update_todo_list(todo2.id, update_data)

        assert updated1.title == "Updated Title"
        assert updated2.title == "Updated Title"

        # Delete multiple
        delete_result1 = await repository.delete_todo_list(todo1.id)
        delete_result2 = await repository.delete_todo_list(todo2.id)
        delete_result3 = await repository.delete_todo_list(todo3.id)

        assert delete_result1 is True
        assert delete_result2 is True
        assert delete_result3 is True

    @pytest.mark.asyncio
    async def test_multiple_todo_item_operations_integration(
        self,
        repository: TodoPGRepository,
        sample_todo_data: TodoListCreateRequest,
        sample_todo_item_data: TodoListItemsAddRequest,
    ) -> None:
        """Integration test for creating, updating, and deleting multiple todo items."""
        # Create parent todo
        todo = await repository.create_todo_list(sample_todo_data)

        # Create multiple items
        item1 = await repository.add_todo_list_item(todo.id, sample_todo_item_data)
        item2_data = TodoListItemsAddRequest(title="Second Item", description="Second item description")
        item2 = await repository.add_todo_list_item(todo.id, item2_data)
        item3_data = TodoListItemsAddRequest(title="Third Item", description="Third item description")
        item3 = await repository.add_todo_list_item(todo.id, item3_data)

        # Verify all created
        assert item1.id is not None
        assert item2.id is not None
        assert item3.id is not None

        # Update multiple
        update_data = TodoListItemUpdateRequest(title="Updated Item", completed=True)
        updated1 = await repository.update_todo_list_item(todo.id, item1.id, update_data)
        updated2 = await repository.update_todo_list_item(todo.id, item2.id, update_data)

        assert updated1.title == "Updated Item"
        assert updated1.completed is True
        assert updated2.title == "Updated Item"
        assert updated2.completed is True

        # Delete multiple
        delete_result1 = await repository.delete_todo_list_item(todo.id, item1.id)
        delete_result2 = await repository.delete_todo_list_item(todo.id, item2.id)
        delete_result3 = await repository.delete_todo_list_item(todo.id, item3.id)

        assert delete_result1 is True
        assert delete_result2 is True
        assert delete_result3 is True
