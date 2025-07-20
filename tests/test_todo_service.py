import pytest
from unittest.mock import Mock, AsyncMock
from app.services.todo_service import TodoService
from app.models.todo_model import TodoModel, TodoItemModel
from app.schemas.todo_schema import TodoCreateRequest, TodoUpdateRequest, TodoItemsAddRequest, TodoItemUpdateRequest
from app.repositories.todo_repository import TodoRepositoryInterface
from datetime import datetime


class TestTodoService:
    """Unit tests for TodoService with mocked repository"""

    @pytest.fixture
    def mock_repository(self):
        """Fixture to provide a mocked TodoRepository"""
        repository = Mock(spec=TodoRepositoryInterface)
        # Configure all methods as async methods
        repository.create_todo = AsyncMock()
        repository.get_todo_by_id = AsyncMock()
        repository.get_all_todos = AsyncMock()
        repository.update_todo = AsyncMock()
        repository.delete_todo = AsyncMock()
        repository.add_todo_item = AsyncMock()
        repository.get_todo_items = AsyncMock()
        repository.update_todo_item = AsyncMock()
        repository.delete_todo_item = AsyncMock()
        return repository

    @pytest.fixture
    def todo_service(self, mock_repository):
        """Fixture to provide a TodoService instance with mocked repository"""
        return TodoService(mock_repository)

    @pytest.fixture
    def sample_todo_model(self):
        """Fixture to provide a sample TodoModel"""
        return TodoModel(
            id=1,
            title="Test Todo",
            description="This is a test todo",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def sample_todo_item_model(self):
        """Fixture to provide a sample TodoItemModel"""
        return TodoItemModel(
            id=1,
            todo_id=1,
            title="Test Item",
            description="This is a test item",
            completed=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.mark.asyncio
    async def test_create_todo(self, todo_service, mock_repository, sample_todo_model):
        """Test creating a new todo item"""
        # Arrange
        todo_data = TodoCreateRequest(title="Test Todo", description="This is a test todo")
        mock_repository.create_todo.return_value = sample_todo_model

        # Act
        result = await todo_service.create_todo(todo_data)

        # Assert
        mock_repository.create_todo.assert_called_once_with(todo_data)
        assert result == sample_todo_model
        assert result.title == "Test Todo"
        assert result.description == "This is a test todo"

    @pytest.mark.asyncio
    async def test_get_todo_by_id_exists(self, todo_service, mock_repository, sample_todo_model):
        """Test retrieving a todo item by ID when it exists"""
        # Arrange
        todo_id = 1
        mock_repository.get_todo_by_id.return_value = sample_todo_model

        # Act
        result = await todo_service.get_todo(todo_id)

        # Assert
        mock_repository.get_todo_by_id.assert_called_once_with(todo_id)
        assert result == sample_todo_model

    @pytest.mark.asyncio
    async def test_get_todo_by_id_not_exists(self, todo_service, mock_repository):
        """Test retrieving a todo item by ID when it doesn't exist"""
        # Arrange
        todo_id = 999
        mock_repository.get_todo_by_id.return_value = None

        # Act
        result = await todo_service.get_todo(todo_id)

        # Assert
        mock_repository.get_todo_by_id.assert_called_once_with(todo_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_todos(self, todo_service, mock_repository, sample_todo_model):
        """Test retrieving all todo items with pagination"""
        # Arrange
        todos_list = [sample_todo_model, sample_todo_model]
        mock_repository.get_all_todos.return_value = todos_list

        # Act
        result = await todo_service.get_all_todos(skip=0, limit=10)

        # Assert
        mock_repository.get_all_todos.assert_called_once_with(0, 10)
        assert result == todos_list
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_todos_default_params(self, todo_service, mock_repository):
        """Test retrieving all todo items with default pagination"""
        # Arrange
        mock_repository.get_all_todos.return_value = []

        # Act
        result = await todo_service.get_all_todos()

        # Assert
        mock_repository.get_all_todos.assert_called_once_with(0, 100)
        assert result == []

    @pytest.mark.asyncio
    async def test_update_todo_exists(self, todo_service, mock_repository, sample_todo_model):
        """Test updating an existing todo item"""
        # Arrange
        todo_id = 1
        update_data = TodoUpdateRequest(title="Updated Todo", description="Updated description")
        updated_todo = TodoModel(
            id=1,
            title="Updated Todo",
            description="Updated description",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repository.update_todo.return_value = updated_todo

        # Act
        result = await todo_service.update_todo(todo_id, update_data)

        # Assert
        mock_repository.update_todo.assert_called_once_with(todo_id, update_data)
        assert result == updated_todo
        assert result.title == "Updated Todo"

    @pytest.mark.asyncio
    async def test_update_todo_not_exists(self, todo_service, mock_repository):
        """Test updating a todo item that doesn't exist"""
        # Arrange
        todo_id = 999
        update_data = TodoUpdateRequest(title="Updated Todo")
        mock_repository.update_todo.return_value = None

        # Act
        result = await todo_service.update_todo(todo_id, update_data)

        # Assert
        mock_repository.update_todo.assert_called_once_with(todo_id, update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_todo_exists(self, todo_service, mock_repository):
        """Test deleting a todo item that exists"""
        # Arrange
        todo_id = 1
        mock_repository.delete_todo.return_value = True

        # Act
        result = await todo_service.delete_todo(todo_id)

        # Assert
        mock_repository.delete_todo.assert_called_once_with(todo_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_todo_not_exists(self, todo_service, mock_repository):
        """Test deleting a todo item that doesn't exist"""
        # Arrange
        todo_id = 999
        mock_repository.delete_todo.return_value = False

        # Act
        result = await todo_service.delete_todo(todo_id)

        # Assert
        mock_repository.delete_todo.assert_called_once_with(todo_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_add_todo_item(self, todo_service, mock_repository, sample_todo_item_model):
        """Test adding a todo item"""
        # Arrange
        todo_id = 1
        item_data = TodoItemsAddRequest(title="Test Item", description="This is a test item")
        mock_repository.add_todo_item.return_value = sample_todo_item_model

        # Act
        result = await todo_service.add_todo_item(todo_id, item_data)

        # Assert
        mock_repository.add_todo_item.assert_called_once_with(todo_id, item_data)
        assert result == sample_todo_item_model

    @pytest.mark.asyncio
    async def test_add_todo_item_not_exists(self, todo_service, mock_repository):
        """Test adding a todo item to non-existent todo"""
        # Arrange
        todo_id = 999
        item_data = TodoItemsAddRequest(title="Test Item")
        mock_repository.add_todo_item.return_value = None

        # Act
        result = await todo_service.add_todo_item(todo_id, item_data)

        # Assert
        mock_repository.add_todo_item.assert_called_once_with(todo_id, item_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_todo_items(self, todo_service, mock_repository, sample_todo_item_model):
        """Test retrieving todo items with pagination"""
        # Arrange
        todo_id = 1
        items_list = [sample_todo_item_model]
        mock_repository.get_todo_items.return_value = items_list

        # Act
        result = await todo_service.get_todo_items(todo_id, skip=0, limit=10)

        # Assert
        mock_repository.get_todo_items.assert_called_once_with(todo_id, 0, 10)
        assert result == items_list

    @pytest.mark.asyncio
    async def test_get_todo_items_default_params(self, todo_service, mock_repository):
        """Test retrieving todo items with default pagination"""
        # Arrange
        todo_id = 1
        mock_repository.get_todo_items.return_value = []

        # Act
        result = await todo_service.get_todo_items(todo_id)

        # Assert
        mock_repository.get_todo_items.assert_called_once_with(todo_id, 0, 100)
        assert result == []

    @pytest.mark.asyncio
    async def test_update_todo_item_exists(self, todo_service, mock_repository, sample_todo_item_model):
        """Test updating an existing todo item"""
        # Arrange
        todo_id = 1
        item_id = 1
        item_data = TodoItemUpdateRequest(title="Updated Item", completed=True)
        updated_item = TodoItemModel(
            id=1,
            todo_id=1,
            title="Updated Item",
            description="This is a test item",
            completed=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_repository.update_todo_item.return_value = updated_item

        # Act
        result = await todo_service.update_todo_item(todo_id, item_id, item_data)

        # Assert
        mock_repository.update_todo_item.assert_called_once_with(todo_id, item_id, item_data)
        assert result == updated_item
        assert result.completed is True

    @pytest.mark.asyncio
    async def test_update_todo_item_not_exists(self, todo_service, mock_repository):
        """Test updating a todo item that doesn't exist"""
        # Arrange
        todo_id = 1
        item_id = 999
        item_data = TodoItemUpdateRequest(title="Updated Item")
        mock_repository.update_todo_item.return_value = None

        # Act
        result = await todo_service.update_todo_item(todo_id, item_id, item_data)

        # Assert
        mock_repository.update_todo_item.assert_called_once_with(todo_id, item_id, item_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_todo_item_exists(self, todo_service, mock_repository):
        """Test deleting a todo item that exists"""
        # Arrange
        todo_id = 1
        item_id = 1
        mock_repository.delete_todo_item.return_value = True

        # Act
        result = await todo_service.delete_todo_item(todo_id, item_id)

        # Assert
        mock_repository.delete_todo_item.assert_called_once_with(todo_id, item_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_todo_item_not_exists(self, todo_service, mock_repository):
        """Test deleting a todo item that doesn't exist"""
        # Arrange
        todo_id = 1
        item_id = 999
        mock_repository.delete_todo_item.return_value = False

        # Act
        result = await todo_service.delete_todo_item(todo_id, item_id)

        # Assert
        mock_repository.delete_todo_item.assert_called_once_with(todo_id, item_id)
        assert result is False
