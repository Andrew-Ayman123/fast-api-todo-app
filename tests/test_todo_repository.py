import pytest
import pytest_asyncio
from app.repositories.todo_pg_repo_impl import TodoPGRepository
from app.models.todo_model import TodoModel, TodoItemModel
from app.schemas.todo_schema import TodoCreateRequest, TodoUpdateRequest, TodoItemsAddRequest, TodoItemUpdateRequest
from app.config.database import database
from datetime import datetime


class TestTodoPGRepository:
    """Integration tests for TodoPGRepository with real database"""

    @pytest_asyncio.fixture(scope="function")
    async def todo_repository(self):
        """Fixture to provide a TodoPGRepository instance with real database"""
        repository = TodoPGRepository(database)
        yield repository
        # Clean up after tests
        await database.close()

    @pytest.mark.asyncio
    async def test_create_todo(self, todo_repository):
        """Test creating a new todo item"""
        # Arrange
        todo_data = TodoCreateRequest(title="Test Todo", description="This is a test todo")

        # Act
        result = await todo_repository.create_todo(todo_data)

        # Assert
        assert result.id is not None
        assert result.title == "Test Todo"
        assert result.description == "This is a test todo"
        assert result.created_at is not None
        assert result.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_todo_by_id_exists(self, todo_repository):
        """Test retrieving a todo by ID when it exists"""
        # Arrange - Create a todo first
        todo_data = TodoCreateRequest(title="Test Todo", description="This is a test todo")
        created_todo = await todo_repository.create_todo(todo_data)

        # Act
        result = await todo_repository.get_todo_by_id(created_todo.id)

        # Assert
        assert result is not None
        assert result.id == created_todo.id
        assert result.title == "Test Todo"
        assert result.description == "This is a test todo"

    @pytest.mark.asyncio
    async def test_get_todo_by_id_not_exists(self, todo_repository):
        """Test retrieving a todo by ID when it doesn't exist"""
        # Arrange
        todo_id = 999999  # Non-existent ID

        # Act
        result = await todo_repository.get_todo_by_id(todo_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_todos(self, todo_repository):
        """Test retrieving all todos with pagination"""
        # Arrange - Create some todos
        todo_data1 = TodoCreateRequest(title="Todo 1", description="First todo")
        todo_data2 = TodoCreateRequest(title="Todo 2", description="Second todo")
        
        await todo_repository.create_todo(todo_data1)
        await todo_repository.create_todo(todo_data2)

        # Act
        result = await todo_repository.get_all_todos(skip=0, limit=10)

        # Assert
        assert len(result) >= 2
        assert any(todo.title == "Todo 1" for todo in result)
        assert any(todo.title == "Todo 2" for todo in result)

    @pytest.mark.asyncio
    async def test_update_todo_exists(self, todo_repository):
        """Test updating an existing todo"""
        # Arrange - Create a todo first
        todo_data = TodoCreateRequest(title="Original Todo", description="Original description")
        created_todo = await todo_repository.create_todo(todo_data)
        
        update_data = TodoUpdateRequest(title="Updated Todo", description="Updated description")

        # Act
        result = await todo_repository.update_todo(created_todo.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_todo.id
        assert result.title == "Updated Todo"
        assert result.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_todo_not_exists(self, todo_repository):
        """Test updating a todo that doesn't exist"""
        # Arrange
        todo_id = 999999  # Non-existent ID
        update_data = TodoUpdateRequest(title="Updated Todo")

        # Act
        result = await todo_repository.update_todo(todo_id, update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_todo_exists(self, todo_repository):
        """Test deleting an existing todo"""
        # Arrange - Create a todo first
        todo_data = TodoCreateRequest(title="Todo to delete", description="This will be deleted")
        created_todo = await todo_repository.create_todo(todo_data)

        # Act
        result = await todo_repository.delete_todo(created_todo.id)

        # Assert
        assert result is True
        
        # Verify the todo is deleted
        deleted_todo = await todo_repository.get_todo_by_id(created_todo.id)
        assert deleted_todo is None

    @pytest.mark.asyncio
    async def test_delete_todo_not_exists(self, todo_repository):
        """Test deleting a todo that doesn't exist"""
        # Arrange
        todo_id = 999999  # Non-existent ID

        # Act
        result = await todo_repository.delete_todo(todo_id)

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_add_todo_item_todo_exists(self, todo_repository):
        """Test adding a todo item to an existing todo"""
        # Arrange - Create a todo first
        todo_data = TodoCreateRequest(title="Parent Todo", description="Parent todo")
        created_todo = await todo_repository.create_todo(todo_data)
        
        item_data = TodoItemsAddRequest(title="Test Item", description="This is a test item")

        # Act
        result = await todo_repository.add_todo_item(created_todo.id, item_data)

        # Assert
        assert result is not None
        assert result.title == "Test Item"
        assert result.description == "This is a test item"
        assert result.todo_id == created_todo.id
        assert result.completed is False

    @pytest.mark.asyncio
    async def test_add_todo_item_todo_not_exists(self, todo_repository):
        """Test adding a todo item to a non-existent todo"""
        # Arrange
        todo_id = 999999  # Non-existent ID
        item_data = TodoItemsAddRequest(title="Test Item")

        # Act
        result = await todo_repository.add_todo_item(todo_id, item_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_todo_items(self, todo_repository):
        """Test retrieving todo items with pagination"""
        # Arrange - Create a todo and add items to it
        todo_data = TodoCreateRequest(title="Parent Todo", description="Parent todo")
        created_todo = await todo_repository.create_todo(todo_data)
        
        item_data1 = TodoItemsAddRequest(title="Item 1", description="First item")
        item_data2 = TodoItemsAddRequest(title="Item 2", description="Second item")
        
        await todo_repository.add_todo_item(created_todo.id, item_data1)
        await todo_repository.add_todo_item(created_todo.id, item_data2)

        # Act
        result = await todo_repository.get_todo_items(created_todo.id, skip=0, limit=10)

        # Assert
        assert len(result) >= 2
        assert any(item.title == "Item 1" for item in result)
        assert any(item.title == "Item 2" for item in result)

    @pytest.mark.asyncio
    async def test_update_todo_item_exists(self, todo_repository):
        """Test updating an existing todo item"""
        # Arrange - Create a todo and add an item to it
        todo_data = TodoCreateRequest(title="Parent Todo", description="Parent todo")
        created_todo = await todo_repository.create_todo(todo_data)
        
        item_data = TodoItemsAddRequest(title="Original Item", description="Original description")
        created_item = await todo_repository.add_todo_item(created_todo.id, item_data)
        
        update_data = TodoItemUpdateRequest(title="Updated Item", completed=True)

        # Act
        result = await todo_repository.update_todo_item(created_todo.id, created_item.id, update_data)

        # Assert
        assert result is not None
        assert result.id == created_item.id
        assert result.title == "Updated Item"
        assert result.completed is True

    @pytest.mark.asyncio
    async def test_update_todo_item_not_exists(self, todo_repository):
        """Test updating a todo item that doesn't exist"""
        # Arrange - Create a todo first
        todo_data = TodoCreateRequest(title="Parent Todo", description="Parent todo")
        created_todo = await todo_repository.create_todo(todo_data)
        
        item_id = 999999  # Non-existent item ID
        update_data = TodoItemUpdateRequest(title="Updated Item")

        # Act
        result = await todo_repository.update_todo_item(created_todo.id, item_id, update_data)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_todo_item_exists(self, todo_repository):
        """Test deleting an existing todo item"""
        # Arrange - Create a todo and add an item to it
        todo_data = TodoCreateRequest(title="Parent Todo", description="Parent todo")
        created_todo = await todo_repository.create_todo(todo_data)
        
        item_data = TodoItemsAddRequest(title="Item to delete", description="This will be deleted")
        created_item = await todo_repository.add_todo_item(created_todo.id, item_data)

        # Act
        result = await todo_repository.delete_todo_item(created_todo.id, created_item.id)

        # Assert
        assert result is True
        
        # Verify the item is deleted
        items = await todo_repository.get_todo_items(created_todo.id)
        assert not any(item.id == created_item.id for item in items)

    @pytest.mark.asyncio
    async def test_delete_todo_item_not_exists(self, todo_repository):
        """Test deleting a todo item that doesn't exist"""
        # Arrange - Create a todo first
        todo_data = TodoCreateRequest(title="Parent Todo", description="Parent todo")
        created_todo = await todo_repository.create_todo(todo_data)
        
        item_id = 999999  # Non-existent item ID

        # Act
        result = await todo_repository.delete_todo_item(created_todo.id, item_id)

        # Assert
        assert result is False
