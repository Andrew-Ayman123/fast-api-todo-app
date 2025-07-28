"""Unit tests for TodoItemService.

This module contains unit tests for the TodoItemService class, testing its
interactions with the TodoItemRepositoryInterface.
"""

from uuid import UUID

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from app.schemas.todo_schema import (
    TodoListItemCreateManyRequest,
    TodoListItemDeleteManyRequest,
    TodoListItemsAddRequest,
    TodoListItemUpdateItem,
    TodoListItemUpdateManyRequest,
    TodoListItemUpdateRequest,
)


@pytest.mark.usefixtures("reset_user_data_function")
class TestTodoListItemsAPI:
    """System tests for Todo List Items endpoints."""

    @pytest.mark.asyncio
    async def test_add_todo_list_item(
        self,
        client: AsyncClient,
        auth_token_header: dict[str, str],
        todo_list_id: UUID,
    ) -> None:
        """Test successful todo list item creation."""
        payload = TodoListItemsAddRequest(title="Test Item", description="This is a test item")
        headers = auth_token_header

        response: Response = await client.post(
            f"/todos/{todo_list_id}/items",
            json=payload.model_dump(),
            headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == payload.title
        assert not data["completed"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_todo_list_items(
        self,
        client: AsyncClient,
        auth_token_header: dict[str, str],
        todo_list_id: UUID,
    ) -> None:
        """Test retrieving todo list items."""
        item_payload = TodoListItemsAddRequest(title="Test Item", description="This is a test item")
        await client.post(f"/todos/{todo_list_id}/items", json=item_payload.model_dump(), headers=auth_token_header)

        response: Response = await client.get(f"/todos/{todo_list_id}/items", headers=auth_token_header)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == item_payload.title

    @pytest.mark.asyncio
    async def test_update_todo_list_item(
        self,
        client: AsyncClient,
        auth_token_header: dict[str, str],
        todo_list_id: UUID,
    ) -> None:
        """Test updating a todo list item."""
        item_payload = TodoListItemsAddRequest(title="Test Item", description="This is a test item")
        add_response = await client.post(
            f"/todos/{todo_list_id}/items",
            json=item_payload.model_dump(),
            headers=auth_token_header,
        )
        item_id = add_response.json()["id"]

        update_payload = TodoListItemUpdateRequest(title="Updated Item", completed=True)
        response: Response = await client.put(
            f"/todos/{todo_list_id}/items/{item_id}",
            json=update_payload.model_dump(),
            headers=auth_token_header,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_payload.title
        assert data["completed"] == update_payload.completed

    @pytest.mark.asyncio
    async def test_delete_todo_list_item(
        self,
        client: AsyncClient,
        auth_token_header: dict[str, str],
        todo_list_id: UUID,
    ) -> None:
        """Test deleting a todo list item."""
        item_payload = TodoListItemsAddRequest(title="Test Item", description="This is a test item")
        add_response = await client.post(
            f"/todos/{todo_list_id}/items",
            json=item_payload.model_dump(),
            headers=auth_token_header,
        )
        item_id = add_response.json()["id"]

        response: Response = await client.delete(f"/todos/{todo_list_id}/items/{item_id}", headers=auth_token_header)

        assert response.status_code == status.HTTP_200_OK

        get_response = await client.get(f"/todos/{todo_list_id}/items", headers=auth_token_header)
        assert len(get_response.json()["data"]) == 0

    @pytest.mark.asyncio
    async def test_create_many_todo_list_items(
        self,
        client: AsyncClient,
        auth_token_header: dict[str, str],
        todo_list_id: UUID,
    ) -> None:
        """Test creating multiple todo list items at once."""
        payload = TodoListItemCreateManyRequest(
            items=[
                TodoListItemsAddRequest(title="Item 1", description="First item"),
                TodoListItemsAddRequest(title="Item 2", description="Second item"),
            ],
        )

        response: Response = await client.post(
            f"/todos-batch/{todo_list_id}/items",
            json=payload.model_dump(),
            headers=auth_token_header,
        )

        assert response.status_code == status.HTTP_200_OK

        get_response = await client.get(f"/todos/{todo_list_id}/items", headers=auth_token_header)
        assert len(get_response.json()["data"]) == len(payload.items)

    @pytest.mark.asyncio
    async def test_update_many_todo_list_items(
        self,
        client: AsyncClient,
        auth_token_header: dict[str, str],
        todo_list_id: UUID,
    ) -> None:
        """Test updating multiple todo list items at once."""
        create_payload = TodoListItemCreateManyRequest(
            items=[
                TodoListItemsAddRequest(title="Item 1", description="First item"),
                TodoListItemsAddRequest(title="Item 2", description="Second item"),
            ],
        )
        create_response = await client.post(
            f"/todos-batch/{todo_list_id}/items",
            json=create_payload.model_dump(),
            headers=auth_token_header,
        )
        assert create_response.status_code == status.HTTP_200_OK

        get_response = await client.get(f"/todos/{todo_list_id}/items", headers=auth_token_header)
        items = get_response.json()["data"]

        update_payload = TodoListItemUpdateManyRequest(
            updates=[
                TodoListItemUpdateItem(
                    id=items[0]["id"],
                    data=TodoListItemUpdateRequest(title="Updated Item 1", completed=True),
                ),
                TodoListItemUpdateItem(
                    id=items[1]["id"],
                    data=TodoListItemUpdateRequest(title="Updated Item 2", completed=True),
                ),
            ],
        )

        response: Response = await client.put(
            f"/todos-batch/{todo_list_id}/items",
            json=update_payload.model_dump(mode="json"),
            headers=auth_token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully updated 2 todo items"

        get_response = await client.get(f"/todos/{todo_list_id}/items", headers=auth_token_header)
        updated_items = get_response.json()["data"]
        assert updated_items[0]["title"] == "Updated Item 1"
        assert updated_items[0]["completed"] is True
        assert updated_items[1]["title"] == "Updated Item 2"
        assert updated_items[1]["completed"] is True

    @pytest.mark.asyncio
    async def test_delete_many_todo_list_items(
        self,
        client: AsyncClient,
        auth_token_header: dict[str, str],
        todo_list_id: UUID,
    ) -> None:
        """Test deleting multiple todo list items at once."""
        create_payload = TodoListItemCreateManyRequest(
            items=[
                TodoListItemsAddRequest(title="Item 1", description="First item"),
                TodoListItemsAddRequest(title="Item 2", description="Second item"),
            ],
        )
        await client.post(
            f"/todos-batch/{todo_list_id}/items",
            json=create_payload.model_dump(),
            headers=auth_token_header,
        )

        get_response = await client.get(f"/todos/{todo_list_id}/items", headers=auth_token_header)
        items = get_response.json()["data"]

        delete_payload = TodoListItemDeleteManyRequest(item_ids=[item["id"] for item in items])
        response: Response = await client.request(
            "DELETE",
            f"/todos-batch/{todo_list_id}/items",
            json=delete_payload.model_dump(mode="json"),
            headers=auth_token_header,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully deleted 2 todo items"

        get_response = await client.get(f"/todos/{todo_list_id}/items", headers=auth_token_header)
        assert len(get_response.json()["data"]) == 0
