"""Unit tests for the TodoService class."""

import pytest
import pytest_asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from app.exceptions.todo_exception import TodoListItemNotFoundError, TodoListNotFoundError
from app.models.todo_model import TodoListItemModel, TodoListModel
from app.repositories.todo_repository_interface import TodoRepositoryInterface
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateRequest,
    TodoListUpdateRequest,
)
from app.services.todo_service import TodoService


@pytest.mark.asyncio
class TestTodoService:
    """Test suite for TodoService class."""

    @pytest.fixture
    def mock_todo_repository(self):
        """Create a mock todo repository for testing."""
        return AsyncMock(spec=TodoRepositoryInterface)

    @pytest.fixture
    def todo_service(self, mock_todo_repository):
        """Create a TodoService instance with mocked repository."""
        return TodoService(todo_repository=mock_todo_repository)

    @pytest.fixture
    def sample_todo_list_model(self):
        """Create a sample TodoListModel for testing."""
        return TodoListModel(
            id=1,
            title="Test Todo List",
            description="Test description",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

    @pytest.fixture
    def sample_todo_item_model(self):
        """Create a sample TodoListItemModel for testing."""
        return TodoListItemModel(
            id=1,
            todo_id=1,
            title="Test Todo Item",
            description="Test item description",
            completed=False,
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 1, 12, 0, 0),
        )

    @pytest.fixture
    def sample_todo_create_request(self):
        """Create a sample TodoListCreateRequest for testing."""
        return TodoListCreateRequest(
            title="New Todo List",
            description="New description"
        )

    @pytest.fixture
    def sample_todo_update_request(self):
        """Create a sample TodoListUpdateRequest for testing."""
        return TodoListUpdateRequest(
            title="Updated Todo List",
            description="Updated description"
        )

    @pytest.fixture
    def sample_item_add_request(self):
        """Create a sample TodoListItemsAddRequest for testing."""
        return TodoListItemsAddRequest(
            title="New Todo Item",
            description="New item description"
        )

    @pytest.fixture
    def sample_item_update_request(self):
        """Create a sample TodoListItemUpdateRequest for testing."""
        return TodoListItemUpdateRequest(
            title="Updated Todo Item",
            description="Updated item description",
            completed=True
        )

    # Tests for create_todo_list
    async def test_create_todo_list_success(self, todo_service, mock_todo_repository, sample_todo_create_request, sample_todo_list_model):
        """Test successful creation of a todo list."""
        mock_todo_repository.create_todo_list.return_value = sample_todo_list_model

        result = await todo_service.create_todo_list(sample_todo_create_request)

        mock_todo_repository.create_todo_list.assert_called_once_with(sample_todo_create_request)
        assert result == sample_todo_list_model

    # Tests for get_todo_list_by_id
    async def test_get_todo_list_by_id_success(self, todo_service, mock_todo_repository, sample_todo_list_model):
        """Test successful retrieval of a todo list by ID."""
        mock_todo_repository.get_todo_list_by_id.return_value = sample_todo_list_model

        result = await todo_service.get_todo_list_by_id(1)

        mock_todo_repository.get_todo_list_by_id.assert_called_once_with(1)
        assert result == sample_todo_list_model

    async def test_get_todo_list_by_id_not_found(self, todo_service, mock_todo_repository):
        """Test TodoListNotFoundError when todo list is not found."""
        mock_todo_repository.get_todo_list_by_id.return_value = None

        with pytest.raises(TodoListNotFoundError) as exc_info:
            await todo_service.get_todo_list_by_id(999)

        mock_todo_repository.get_todo_list_by_id.assert_called_once_with(999)
        assert exc_info.value.todo_id == 999

    # Tests for get_all_todo_lists_without_items
    async def test_get_all_todo_lists_without_items_default_params(self, todo_service, mock_todo_repository, sample_todo_list_model):
        """Test retrieval of all todo lists with default pagination parameters."""
        expected_todos = [sample_todo_list_model]
        mock_todo_repository.get_all_todo_lists.return_value = expected_todos

        result = await todo_service.get_all_todo_lists_without_items()

        mock_todo_repository.get_all_todo_lists.assert_called_once_with(0, 100)
        assert result == expected_todos

    async def test_get_all_todo_lists_without_items_custom_params(self, todo_service, mock_todo_repository, sample_todo_list_model):
        """Test retrieval of all todo lists with custom pagination parameters."""
        expected_todos = [sample_todo_list_model]
        mock_todo_repository.get_all_todo_lists.return_value = expected_todos

        result = await todo_service.get_all_todo_lists_without_items(skip=10, limit=50)

        mock_todo_repository.get_all_todo_lists.assert_called_once_with(10, 50)
        assert result == expected_todos

    async def test_get_all_todo_lists_without_items_empty_result(self, todo_service, mock_todo_repository):
        """Test retrieval of all todo lists when no todos exist."""
        mock_todo_repository.get_all_todo_lists.return_value = []

        result = await todo_service.get_all_todo_lists_without_items()

        mock_todo_repository.get_all_todo_lists.assert_called_once_with(0, 100)
        assert result == []

    # Tests for update_todo_list
    async def test_update_todo_list_success(self, todo_service, mock_todo_repository, sample_todo_update_request, sample_todo_list_model):
        """Test successful update of a todo list."""
        mock_todo_repository.update_todo_list.return_value = sample_todo_list_model

        result = await todo_service.update_todo_list(1, sample_todo_update_request)

        mock_todo_repository.update_todo_list.assert_called_once_with(1, sample_todo_update_request)
        assert result == sample_todo_list_model

    async def test_update_todo_list_not_found(self, todo_service, mock_todo_repository, sample_todo_update_request):
        """Test TodoListNotFoundError when updating non-existent todo list."""
        mock_todo_repository.update_todo_list.return_value = None

        with pytest.raises(TodoListNotFoundError) as exc_info:
            await todo_service.update_todo_list(999, sample_todo_update_request)

        mock_todo_repository.update_todo_list.assert_called_once_with(999, sample_todo_update_request)
        assert exc_info.value.todo_id == 999

    # Tests for delete_todo_list
    async def test_delete_todo_list_success(self, todo_service, mock_todo_repository):
        """Test successful deletion of a todo list."""
        mock_todo_repository.delete_todo_list.return_value = True

        result = await todo_service.delete_todo_list(1)

        mock_todo_repository.delete_todo_list.assert_called_once_with(1)
        assert result is None

    async def test_delete_todo_list_not_found(self, todo_service, mock_todo_repository):
        """Test TodoListNotFoundError when deleting non-existent todo list."""
        mock_todo_repository.delete_todo_list.return_value = False

        with pytest.raises(TodoListNotFoundError) as exc_info:
            await todo_service.delete_todo_list(999)

        mock_todo_repository.delete_todo_list.assert_called_once_with(999)
        assert exc_info.value.todo_id == 999

    # Tests for add_todo_list_item
    async def test_add_todo_list_item_success(self, todo_service, mock_todo_repository, sample_item_add_request, sample_todo_item_model):
        """Test successful addition of an item to a todo list."""
        mock_todo_repository.add_todo_list_item.return_value = sample_todo_item_model

        result = await todo_service.add_todo_list_item(1, sample_item_add_request)

        mock_todo_repository.add_todo_list_item.assert_called_once_with(1, sample_item_add_request)
        assert result == sample_todo_item_model

    async def test_add_todo_list_item_todo_not_found(self, todo_service, mock_todo_repository, sample_item_add_request):
        """Test TodoListNotFoundError when adding item to non-existent todo list."""
        mock_todo_repository.add_todo_list_item.return_value = None

        with pytest.raises(TodoListNotFoundError) as exc_info:
            await todo_service.add_todo_list_item(999, sample_item_add_request)

        mock_todo_repository.add_todo_list_item.assert_called_once_with(999, sample_item_add_request)
        assert exc_info.value.todo_id == 999

    # Tests for get_todo_list_items
    async def test_get_todo_list_items_default_params(self, todo_service, mock_todo_repository, sample_todo_item_model):
        """Test retrieval of todo list items with default pagination parameters."""
        expected_items = [sample_todo_item_model]
        mock_todo_repository.get_todo_list_items.return_value = expected_items

        result = await todo_service.get_todo_list_items(1)

        mock_todo_repository.get_todo_list_items.assert_called_once_with(1, 0, 100)
        assert result == expected_items

    async def test_get_todo_list_items_custom_params(self, todo_service, mock_todo_repository, sample_todo_item_model):
        """Test retrieval of todo list items with custom pagination parameters."""
        expected_items = [sample_todo_item_model]
        mock_todo_repository.get_todo_list_items.return_value = expected_items

        result = await todo_service.get_todo_list_items(1, skip=5, limit=25)

        mock_todo_repository.get_todo_list_items.assert_called_once_with(1, 5, 25)
        assert result == expected_items

    async def test_get_todo_list_items_empty_result(self, todo_service, mock_todo_repository):
        """Test retrieval of todo list items when no items exist."""
        mock_todo_repository.get_todo_list_items.return_value = []

        result = await todo_service.get_todo_list_items(1)

        mock_todo_repository.get_todo_list_items.assert_called_once_with(1, 0, 100)
        assert result == []

    # Tests for update_todo_item
    async def test_update_todo_item_success(self, todo_service, mock_todo_repository, sample_item_update_request, sample_todo_item_model):
        """Test successful update of a todo list item."""
        mock_todo_repository.update_todo_list_item.return_value = sample_todo_item_model

        result = await todo_service.update_todo_item(1, 1, sample_item_update_request)

        mock_todo_repository.update_todo_list_item.assert_called_once_with(1, 1, sample_item_update_request)
        assert result == sample_todo_item_model

    async def test_update_todo_item_not_found(self, todo_service, mock_todo_repository, sample_item_update_request):
        """Test TodoListItemNotFoundError when updating non-existent todo item."""
        mock_todo_repository.update_todo_list_item.return_value = None

        with pytest.raises(TodoListItemNotFoundError) as exc_info:
            await todo_service.update_todo_item(1, 999, sample_item_update_request)

        mock_todo_repository.update_todo_list_item.assert_called_once_with(1, 999, sample_item_update_request)
        assert exc_info.value.todo_id == 1
        assert exc_info.value.item_id == 999

    # Tests for delete_todo_list_item
    async def test_delete_todo_list_item_success(self, todo_service, mock_todo_repository):
        """Test successful deletion of a todo list item."""
        mock_todo_repository.delete_todo_list_item.return_value = True

        result = await todo_service.delete_todo_list_item(1, 1)

        mock_todo_repository.delete_todo_list_item.assert_called_once_with(1, 1)
        assert result is None

    async def test_delete_todo_list_item_not_found(self, todo_service, mock_todo_repository):
        """Test TodoListItemNotFoundError when deleting non-existent todo item."""
        mock_todo_repository.delete_todo_list_item.return_value = False

        with pytest.raises(TodoListItemNotFoundError) as exc_info:
            await todo_service.delete_todo_list_item(1, 999)

        mock_todo_repository.delete_todo_list_item.assert_called_once_with(1, 999)
        assert exc_info.value.todo_id == 1
        assert exc_info.value.item_id == 999

    # Edge case tests
    async def test_service_initialization(self, mock_todo_repository):
        """Test proper initialization of TodoService."""
        service = TodoService(todo_repository=mock_todo_repository)
        assert service.todo_repository == mock_todo_repository

    async def test_multiple_todo_lists(self, todo_service, mock_todo_repository):
        """Test handling multiple todo lists."""
        todo1 = TodoListModel(id=1, title="Todo 1", description="Description 1", created_at=datetime.now(), updated_at=datetime.now())
        todo2 = TodoListModel(id=2, title="Todo 2", description="Description 2", created_at=datetime.now(), updated_at=datetime.now())
        expected_todos = [todo1, todo2]
        
        mock_todo_repository.get_all_todo_lists.return_value = expected_todos

        result = await todo_service.get_all_todo_lists_without_items()

        assert len(result) == 2
        assert result == expected_todos

    async def test_multiple_todo_items(self, todo_service, mock_todo_repository):
        """Test handling multiple todo items."""
        item1 = TodoListItemModel(id=1, todo_id=1, title="Item 1", description="Description 1", completed=False, created_at=datetime.now(), updated_at=datetime.now())
        item2 = TodoListItemModel(id=2, todo_id=1, title="Item 2", description="Description 2", completed=True, created_at=datetime.now(), updated_at=datetime.now())
        expected_items = [item1, item2]
        
        mock_todo_repository.get_todo_list_items.return_value = expected_items

        result = await todo_service.get_todo_list_items(1)

        assert len(result) == 2
        assert result == expected_items

    # Tests for batch operations - Todo Lists
    async def test_create_many_todo_lists_success(self, todo_service, mock_todo_repository, sample_todo_create_request):
        """Test successful creation of multiple todo lists."""
        todo1 = TodoListModel(id=1, title="Todo 1", description="Description 1", created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        todo2 = TodoListModel(id=2, title="Todo 2", description="Description 2", created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        
        mock_todo_repository.create_todo_list.side_effect = [todo1, todo2]
        
        todo_requests = [sample_todo_create_request, sample_todo_create_request]
        result = await todo_service.create_many_todo_lists(todo_requests)
        
        assert len(result) == 2
        assert result == [todo1, todo2]
        assert mock_todo_repository.create_todo_list.call_count == 2

    async def test_update_many_todo_lists_success(self, todo_service, mock_todo_repository, sample_todo_update_request):
        """Test successful update of multiple todo lists."""
        todo1 = TodoListModel(id=1, title="Updated Todo 1", description="Updated Description 1", created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        todo2 = TodoListModel(id=2, title="Updated Todo 2", description="Updated Description 2", created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        
        mock_todo_repository.update_todo_list.side_effect = [todo1, todo2]
        
        # Create mock update objects
        update1 = MagicMock()
        update1.id = 1
        update1.data = sample_todo_update_request
        update2 = MagicMock()
        update2.id = 2
        update2.data = sample_todo_update_request
        
        updates = [update1, update2]
        result = await todo_service.update_many_todo_lists(updates)
        
        assert len(result) == 2
        assert result == [todo1, todo2]
        assert mock_todo_repository.update_todo_list.call_count == 2

    async def test_update_many_todo_lists_not_found(self, todo_service, mock_todo_repository, sample_todo_update_request):
        """Test TodoListNotFoundError when updating non-existent todo list."""
        mock_todo_repository.update_todo_list.return_value = None
        
        update1 = MagicMock()
        update1.id = 999
        update1.data = sample_todo_update_request
        
        with pytest.raises(TodoListNotFoundError) as exc_info:
            await todo_service.update_many_todo_lists([update1])
        
        assert exc_info.value.todo_id == 999

    async def test_delete_many_todo_lists_success(self, todo_service, mock_todo_repository):
        """Test successful deletion of multiple todo lists."""
        mock_todo_repository.delete_todo_list.return_value = True
        
        todo_ids = [1, 2, 3]
        await todo_service.delete_many_todo_lists(todo_ids)
        
        assert mock_todo_repository.delete_todo_list.call_count == 3

    async def test_delete_many_todo_lists_not_found(self, todo_service, mock_todo_repository):
        """Test TodoListNotFoundError when deleting non-existent todo list."""
        mock_todo_repository.delete_todo_list.return_value = False
        
        with pytest.raises(TodoListNotFoundError) as exc_info:
            await todo_service.delete_many_todo_lists([999])
        
        assert exc_info.value.todo_id == 999

    # Tests for batch operations - Todo List Items
    async def test_create_many_todo_list_items_success(self, todo_service, mock_todo_repository, sample_item_add_request):
        """Test successful creation of multiple todo list items."""
        item1 = TodoListItemModel(id=1, todo_id=1, title="Item 1", description="Description 1", completed=False, created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        item2 = TodoListItemModel(id=2, todo_id=1, title="Item 2", description="Description 2", completed=False, created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        
        mock_todo_repository.add_todo_list_item.side_effect = [item1, item2]
        
        item_requests = [sample_item_add_request, sample_item_add_request]
        result = await todo_service.create_many_todo_list_items(1, item_requests)
        
        assert len(result) == 2
        assert result == [item1, item2]
        assert mock_todo_repository.add_todo_list_item.call_count == 2

    async def test_create_many_todo_list_items_todo_not_found(self, todo_service, mock_todo_repository, sample_item_add_request):
        """Test TodoListNotFoundError when adding items to non-existent todo list."""
        mock_todo_repository.add_todo_list_item.return_value = None
        
        with pytest.raises(TodoListNotFoundError) as exc_info:
            await todo_service.create_many_todo_list_items(999, [sample_item_add_request])
        
        assert exc_info.value.todo_id == 999

    async def test_update_many_todo_list_items_success(self, todo_service, mock_todo_repository, sample_item_update_request):
        """Test successful update of multiple todo list items."""
        item1 = TodoListItemModel(id=1, todo_id=1, title="Updated Item 1", description="Updated Description 1", completed=True, created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        item2 = TodoListItemModel(id=2, todo_id=1, title="Updated Item 2", description="Updated Description 2", completed=True, created_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc), updated_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
        
        mock_todo_repository.update_todo_list_item.side_effect = [item1, item2]
        
        # Create mock update objects
        update1 = MagicMock()
        update1.id = 1
        update1.data = sample_item_update_request
        update2 = MagicMock()
        update2.id = 2
        update2.data = sample_item_update_request
        
        updates = [update1, update2]
        result = await todo_service.update_many_todo_list_items(1, updates)
        
        assert len(result) == 2
        assert result == [item1, item2]
        assert mock_todo_repository.update_todo_list_item.call_count == 2

    async def test_update_many_todo_list_items_not_found(self, todo_service, mock_todo_repository, sample_item_update_request):
        """Test TodoListItemNotFoundError when updating non-existent todo list item."""
        mock_todo_repository.update_todo_list_item.return_value = None
        
        update1 = MagicMock()
        update1.id = 999
        update1.data = sample_item_update_request
        
        with pytest.raises(TodoListItemNotFoundError) as exc_info:
            await todo_service.update_many_todo_list_items(1, [update1])
        
        assert exc_info.value.todo_id == 1
        assert exc_info.value.item_id == 999

    async def test_delete_many_todo_list_items_success(self, todo_service, mock_todo_repository):
        """Test successful deletion of multiple todo list items."""
        mock_todo_repository.delete_todo_list_item.return_value = True
        
        item_ids = [1, 2, 3]
        await todo_service.delete_many_todo_list_items(1, item_ids)
        
        assert mock_todo_repository.delete_todo_list_item.call_count == 3

    async def test_delete_many_todo_list_items_not_found(self, todo_service, mock_todo_repository):
        """Test TodoListItemNotFoundError when deleting non-existent todo list item."""
        mock_todo_repository.delete_todo_list_item.return_value = False
        
        with pytest.raises(TodoListItemNotFoundError) as exc_info:
            await todo_service.delete_many_todo_list_items(1, [999])
        
        assert exc_info.value.todo_id == 1
        assert exc_info.value.item_id == 999
