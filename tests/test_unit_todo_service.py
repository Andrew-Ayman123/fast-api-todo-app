"""Unit tests for TodoService.

This module contains unit tests for the TodoService class, testing its
interactions with the TodoRepositoryInterface.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions.todo_exception import TodoListItemNotFoundError, TodoListNotFoundError
from app.models.todo_model import TodoListItemModel, TodoListModel
from app.schemas.todo_schema import (
    TodoListCreateRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateItem,
    TodoListItemUpdateRequest,
    TodoListUpdateItem,
    TodoListUpdateRequest,
)
from app.services.todo_service import TodoService


class TestTodoService:
    """Test suite for TodoService with mocked repository."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up for each test method."""
        self.mock_repo = MagicMock()
        self.mock_repo.create_todo_list = AsyncMock()
        self.mock_repo.get_todo_list_by_id = AsyncMock()
        self.mock_repo.get_all_todo_lists = AsyncMock(return_value=[])
        self.mock_repo.update_todo_list = AsyncMock()
        self.mock_repo.delete_todo_list = AsyncMock(return_value=True)
        self.mock_repo.add_todo_list_item = AsyncMock()
        self.mock_repo.get_todo_list_items = AsyncMock(return_value=[])
        self.mock_repo.update_todo_list_item = AsyncMock()
        self.mock_repo.delete_todo_list_item = AsyncMock(return_value=True)
        self.mock_repo.count_todo_lists = AsyncMock(return_value=0)
        self.mock_repo.count_todo_list_items = AsyncMock(return_value=0)

        self.service = TodoService(todo_repository=self.mock_repo)
        self.user_id = uuid.uuid4()
        self.todo_id = uuid.uuid4()
        self.item_id = uuid.uuid4()

    @pytest.mark.asyncio
    async def test_create_todo_list_success(self) -> None:
        """Test successful creation of a todo list."""
        test_data = TodoListCreateRequest(title="Test List", description="Test description")
        expected_result = TodoListModel(
            id=uuid.uuid4(),
            user_id=(self.user_id),
            title="Test List",
            description="Test description",
        )

        self.mock_repo.create_todo_list.return_value = expected_result

        result = await self.service.create_todo_list(test_data, self.user_id)

        self.mock_repo.create_todo_list.assert_called_once_with(test_data, (self.user_id))
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id_success(self) -> None:
        """Test successful retrieval of a todo list by ID."""
        expected_todo = TodoListModel(
            id=(self.todo_id),
            user_id=(self.user_id),
            title="Test List",
            description="Test description",
        )
        self.mock_repo.get_todo_list_by_id.return_value = expected_todo

        result = await self.service.get_todo_list_by_id(self.todo_id, self.user_id)

        self.mock_repo.get_todo_list_by_id.assert_called_once_with((self.todo_id), (self.user_id))
        assert result == expected_todo

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id_not_found(self) -> None:
        """Test retrieval of non-existent todo list raises error."""
        self.mock_repo.get_todo_list_by_id.return_value = None

        with pytest.raises(TodoListNotFoundError):
            await self.service.get_todo_list_by_id(self.todo_id, self.user_id)

    @pytest.mark.asyncio
    async def test_get_all_todo_lists_without_items(self) -> None:
        """Test retrieval of all todo lists without items."""
        mock_todos = [
            TodoListModel(id=uuid.uuid4(), user_id=(self.user_id), title="List 1"),
            TodoListModel(id=uuid.uuid4(), user_id=(self.user_id), title="List 2"),
        ]
        self.mock_repo.get_all_todo_lists.return_value = mock_todos

        result = await self.service.get_all_todo_lists_without_items(self.user_id, skip=0, limit=10)

        assert result == mock_todos

    @pytest.mark.asyncio
    async def test_update_todo_list_success(self) -> None:
        """Test successful update of a todo list."""
        update_data = TodoListUpdateRequest(title="Updated Title", description="Updated description")
        expected_result = TodoListModel(
            id=(self.todo_id),
            user_id=(self.user_id),
            title="Updated Title",
            description="Updated description",
        )
        self.mock_repo.update_todo_list.return_value = expected_result

        result = await self.service.update_todo_list(self.todo_id, update_data, self.user_id)

        self.mock_repo.update_todo_list.assert_called_once_with(
            (self.todo_id),
            update_data,
            (self.user_id),
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_update_todo_list_not_found(self) -> None:
        """Test update of non-existent todo list raises error."""
        update_data = TodoListUpdateRequest(title="Updated Title")
        self.mock_repo.update_todo_list.return_value = None

        with pytest.raises(TodoListNotFoundError):
            await self.service.update_todo_list(self.todo_id, update_data, self.user_id)

    @pytest.mark.asyncio
    async def test_delete_todo_list_success(self) -> None:
        """Test successful deletion of a todo list."""
        await self.service.delete_todo_list(self.todo_id, self.user_id)

        self.mock_repo.delete_todo_list.assert_called_once_with((self.todo_id), (self.user_id))

    @pytest.mark.asyncio
    async def test_delete_todo_list_not_found(self) -> None:
        """Test deletion of non-existent todo list raises error."""
        self.mock_repo.delete_todo_list.return_value = False

        with pytest.raises(TodoListNotFoundError):
            await self.service.delete_todo_list(self.todo_id, self.user_id)

    @pytest.mark.asyncio
    async def test_add_todo_list_item_success(self) -> None:
        """Test successful addition of a todo list item."""
        item_data = TodoListItemsAddRequest(title="Item 1", description="Test item")
        expected_item = TodoListItemModel(
            id=uuid.uuid4(),
            todo_id=(self.todo_id),
            title="Item 1",
            description="Test item",
        )
        self.mock_repo.add_todo_list_item.return_value = expected_item

        result = await self.service.add_todo_list_item(self.todo_id, item_data, self.user_id)

        self.mock_repo.add_todo_list_item.assert_called_once_with(
            (self.todo_id),
            item_data,
            (self.user_id),
        )
        assert result == expected_item

    @pytest.mark.asyncio
    async def test_add_todo_list_item_list_not_found(self) -> None:
        """Test adding item to non-existent todo list raises error."""
        item_data = TodoListItemsAddRequest(title="Item 1")
        self.mock_repo.add_todo_list_item.return_value = None

        with pytest.raises(TodoListNotFoundError):
            await self.service.add_todo_list_item(self.todo_id, item_data, self.user_id)

    @pytest.mark.asyncio
    async def test_get_todo_list_items(self) -> None:
        """Test retrieval of todo list items."""
        mock_items = [
            TodoListItemModel(id=uuid.uuid4(), todo_id=(self.todo_id), title="Item 1"),
            TodoListItemModel(id=uuid.uuid4(), todo_id=(self.todo_id), title="Item 2"),
        ]
        self.mock_repo.get_todo_list_items.return_value = mock_items

        result = await self.service.get_todo_list_items(self.todo_id, self.user_id, skip=0, limit=10)

        assert result == mock_items

    @pytest.mark.asyncio
    async def test_update_todo_item_success(self) -> None:
        """Test successful update of a todo item."""
        update_data = TodoListItemUpdateRequest(title="Updated Item", completed=True)
        expected_item = TodoListItemModel(
            id=(self.item_id),
            todo_id=(self.todo_id),
            title="Updated Item",
            completed=True,
        )
        self.mock_repo.update_todo_list_item.return_value = expected_item

        result = await self.service.update_todo_item(self.todo_id, self.item_id, update_data, self.user_id)

        self.mock_repo.update_todo_list_item.assert_called_once_with(
            (self.todo_id),
            (self.item_id),
            update_data,
            (self.user_id),
        )
        assert result == expected_item

    @pytest.mark.asyncio
    async def test_update_todo_item_not_found(self) -> None:
        """Test update of non-existent todo item raises error."""
        update_data = TodoListItemUpdateRequest(title="Updated Item")
        self.mock_repo.update_todo_list_item.return_value = None

        with pytest.raises(TodoListItemNotFoundError):
            await self.service.update_todo_item(self.todo_id, self.item_id, update_data, self.user_id)

    @pytest.mark.asyncio
    async def test_delete_todo_list_item_success(self) -> None:
        """Test successful deletion of a todo item."""
        await self.service.delete_todo_list_item(self.todo_id, self.item_id, self.user_id)

        self.mock_repo.delete_todo_list_item.assert_called_once_with(
            (self.todo_id),
            (self.item_id),
            (self.user_id),
        )

    @pytest.mark.asyncio
    async def test_delete_todo_list_item_not_found(self) -> None:
        """Test deletion of non-existent todo item raises error."""
        self.mock_repo.delete_todo_list_item.return_value = False

        with pytest.raises(TodoListItemNotFoundError):
            await self.service.delete_todo_list_item(self.todo_id, self.item_id, self.user_id)

    @pytest.mark.asyncio
    async def test_count_todo_lists(self) -> None:
        """Test counting todo lists for a user."""
        self.mock_repo.count_todo_lists.return_value = 5

        result = await self.service.count_todo_lists(self.user_id)

        self.mock_repo.count_todo_lists.assert_called_once_with(self.user_id)
        assert result == 5

    @pytest.mark.asyncio
    async def test_count_todo_list_items(self) -> None:
        """Test counting items in a todo list."""
        self.mock_repo.count_todo_list_items.return_value = 3

        result = await self.service.count_todo_list_items(self.todo_id, self.user_id)

        self.mock_repo.count_todo_list_items.assert_called_once_with((self.todo_id), (self.user_id))
        assert result == 3

    @pytest.mark.asyncio
    async def test_create_many_todo_lists(self) -> None:
        """Test creating multiple todo lists."""
        todo_data = [
            TodoListCreateRequest(title="List 1"),
            TodoListCreateRequest(title="List 2"),
        ]
        mock_results = [
            TodoListModel(id=uuid.uuid4(), user_id=(self.user_id), title="List 1"),
            TodoListModel(id=uuid.uuid4(), user_id=(self.user_id), title="List 2"),
        ]
        self.mock_repo.create_todo_list.side_effect = mock_results

        result = await self.service.create_many_todo_lists(todo_data, self.user_id)

        assert self.mock_repo.create_todo_list.call_count == 2
        assert result == mock_results

    @pytest.mark.asyncio
    async def test_update_many_todo_lists(self) -> None:
        """Test updating multiple todo lists."""
        updates = [
            TodoListUpdateItem(id=self.todo_id, data=TodoListUpdateRequest(title="Updated 1")),
            TodoListUpdateItem(id=uuid.uuid4(), data=TodoListUpdateRequest(title="Updated 2")),
        ]
        mock_results = [
            TodoListModel(id=(self.todo_id), user_id=(self.user_id), title="Updated 1"),
            TodoListModel(id=(str(updates[1].id)), user_id=(self.user_id), title="Updated 2"),
        ]
        self.mock_repo.update_todo_list.side_effect = mock_results

        result = await self.service.update_many_todo_lists(updates, self.user_id)

        assert self.mock_repo.update_todo_list.call_count == 2
        assert result == mock_results

    @pytest.mark.asyncio
    async def test_delete_many_todo_lists(self) -> None:
        """Test deleting multiple todo lists."""
        todo_ids = [self.todo_id, uuid.uuid4()]

        await self.service.delete_many_todo_lists(todo_ids, self.user_id)

        assert self.mock_repo.delete_todo_list.call_count == 2

    @pytest.mark.asyncio
    async def test_create_many_todo_list_items(self) -> None:
        """Test creating multiple todo list items."""
        items = [
            TodoListItemsAddRequest(title="Item 1"),
            TodoListItemsAddRequest(title="Item 2"),
        ]
        mock_results = [
            TodoListItemModel(id=uuid.uuid4(), todo_id=(self.todo_id), title="Item 1"),
            TodoListItemModel(id=uuid.uuid4(), todo_id=(self.todo_id), title="Item 2"),
        ]
        self.mock_repo.add_todo_list_item.side_effect = mock_results

        result = await self.service.create_many_todo_list_items(self.todo_id, items, self.user_id)

        assert self.mock_repo.add_todo_list_item.call_count == 2
        assert result == mock_results

    @pytest.mark.asyncio
    async def test_update_many_todo_list_items(self) -> None:
        """Test updating multiple todo list items."""
        updates = [
            TodoListItemUpdateItem(id=self.item_id, data=TodoListItemUpdateRequest(title="Updated 1")),
            TodoListItemUpdateItem(id=uuid.uuid4(), data=TodoListItemUpdateRequest(title="Updated 2")),
        ]
        mock_results = [
            TodoListItemModel(id=(self.item_id), todo_id=(self.todo_id), title="Updated 1"),
            TodoListItemModel(id=(updates[1].id), todo_id=(self.todo_id), title="Updated 2"),
        ]
        self.mock_repo.update_todo_list_item.side_effect = mock_results

        result = await self.service.update_many_todo_list_items(self.todo_id, updates, self.user_id)

        assert self.mock_repo.update_todo_list_item.call_count == 2
        assert result == mock_results

    @pytest.mark.asyncio
    async def test_delete_many_todo_list_items(self) -> None:
        """Test deleting multiple todo list items."""
        item_ids = [self.item_id, uuid.uuid4()]

        await self.service.delete_many_todo_list_items(self.todo_id, item_ids, self.user_id)

        assert self.mock_repo.delete_todo_list_item.call_count == 2
