"""Unit tests for TodoItemService.

This module contains unit tests for the TodoItemService class, testing its
interactions with the TodoItemRepositoryInterface.
"""
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy import text

from tests.test_dependencies import get_session_maker_test


class TestTodoListItemsAPI:
    """System tests for Todo List Items endpoints."""

    @pytest_asyncio.fixture(scope="class")
    async def setup_and_teardown_class(self, client: AsyncClient) -> AsyncGenerator:
        """Clean up users before and after tests."""
        session_maker = get_session_maker_test()
        async with session_maker() as session:
            await session.execute(text("DELETE FROM users"))
            await session.commit()
        user_payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123",
            "username": "Test User",
        }
        # Create test user
        await client.post("/user/register", json=user_payload)
        yield
        # Clean after test
        async with session_maker() as session:
            await session.execute(text("DELETE FROM users"))
            await session.commit()

    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def setup_and_teardown_every_test(self, setup_and_teardown_class: AsyncGenerator) -> AsyncGenerator:  # noqa: ARG002
        """Clean up todos and items before and after tests."""
        # using setup_and_teardown_class to make sure it runs after the class setup
        session_maker = get_session_maker_test()
        async with session_maker() as session:
            await session.execute(text("DELETE FROM todo_items"))
            await session.execute(text("DELETE FROM todos"))
            await session.commit()
        yield
        async with session_maker() as session:
            await session.execute(text("DELETE FROM todo_items"))
            await session.execute(text("DELETE FROM todos"))
            await session.commit()

    @pytest_asyncio.fixture()
    async def auth_token(self, client: AsyncClient) -> str:
        """Fixture to get auth token for tests."""
        payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123",
            "username": "Test User",
        }
        response = await client.post("/user/login", json=payload)
        return response.json()["token"]

    @pytest_asyncio.fixture()
    async def test_todo_list(self, client: AsyncClient, auth_token: str) -> dict:
        """Fixture to create a test todo list."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"title": "Test Todo List", "description": "Test description"}
        response = await client.post("/todos/", json=payload, headers=headers)
        return response.json()

    @pytest.mark.asyncio
    async def test_add_todo_list_item(self, client: AsyncClient, auth_token: str, test_todo_list: dict) -> None:
        """Test successful todo list item creation."""
        todo_id = test_todo_list["id"]
        payload = {"title": "Test Item"}
        headers = {"Authorization": f"Bearer {auth_token}"}

        response: Response = await client.post(f"/todos/{todo_id}/items", json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == payload["title"]
        assert not data["completed"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_todo_list_items(self, client: AsyncClient, auth_token: str, test_todo_list: dict) -> None:
        """Test retrieving todo list items."""
        todo_id = test_todo_list["id"]
        headers = {"Authorization": f"Bearer {auth_token}"}

        # First add an item
        item_payload = {"title": "Test Item"}
        await client.post(f"/todos/{todo_id}/items", json=item_payload, headers=headers)

        # Then get items
        response: Response = await client.get(f"/todos/{todo_id}/items", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == item_payload["title"]

    @pytest.mark.asyncio
    async def test_update_todo_list_item(self, client: AsyncClient, auth_token: str, test_todo_list: dict) -> None:
        """Test updating a todo list item."""
        todo_id = test_todo_list["id"]
        headers = {"Authorization": f"Bearer {auth_token}"}

        # First add an item
        item_payload = {"title": "Test Item", "completed": False}
        add_response = await client.post(f"/todos/{todo_id}/items", json=item_payload, headers=headers)
        item_id = add_response.json()["id"]

        # Then update the item
        update_payload = {"title": "Updated Item", "completed": True}
        response: Response = await client.put(f"/todos/{todo_id}/items/{item_id}", json=update_payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_payload["title"]
        assert data["completed"] == update_payload["completed"]

    @pytest.mark.asyncio
    async def test_delete_todo_list_item(self, client: AsyncClient, auth_token: str, test_todo_list: dict) -> None:
        """Test deleting a todo list item."""
        todo_id = test_todo_list["id"]
        headers = {"Authorization": f"Bearer {auth_token}"}

        # First add an item
        item_payload = {"title": "Test Item", "completed": False}
        add_response = await client.post(f"/todos/{todo_id}/items", json=item_payload, headers=headers)
        item_id = add_response.json()["id"]

        # Then delete the item
        response: Response = await client.delete(f"/todos/{todo_id}/items/{item_id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK

        # Verify item is deleted
        get_response = await client.get(f"/todos/{todo_id}/items", headers=headers)
        assert len(get_response.json()["data"]) == 0

    @pytest.mark.asyncio
    async def test_create_many_todo_list_items(
        self, client: AsyncClient, auth_token: str, test_todo_list: dict,
    ) -> None:
        """Test creating multiple todo list items at once."""
        todo_id = test_todo_list["id"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"items": [{"title": "Item 1", "completed": False}, {"title": "Item 2", "completed": True}]}

        response: Response = await client.post(f"/todos-batch/{todo_id}/items", json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully created 2 todo items"

        # Verify items were created
        get_response = await client.get(f"/todos/{todo_id}/items", headers=headers)
        assert len(get_response.json()["data"]) == 2

    @pytest.mark.asyncio
    async def test_update_many_todo_list_items(
        self, client: AsyncClient, auth_token: str, test_todo_list: dict,
    ) -> None:
        """Test updating multiple todo list items at once."""
        todo_id = test_todo_list["id"]
        headers = {"Authorization": f"Bearer {auth_token}"}

        # First create items
        create_payload = {"items": [{"title": "Item 1", "completed": False}, {"title": "Item 2", "completed": False}]}
        create_response = await client.post(f"/todos-batch/{todo_id}/items", json=create_payload, headers=headers)
        assert create_response.status_code == status.HTTP_200_OK

        # Get the created item IDs
        get_response = await client.get(f"/todos/{todo_id}/items", headers=headers)
        items = get_response.json()["data"]

        # Prepare update payload
        update_payload = {
            "updates": [
                {"id": items[0]["id"], "data": {"title": "Updated Item 1", "completed": True}},
                {"id": items[1]["id"], "data": {"title": "Updated Item 2", "completed": True}},
            ],
        }

        # Update items
        response: Response = await client.put(f"/todos-batch/{todo_id}/items", json=update_payload, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully updated 2 todo items"

        # Verify updates
        get_response = await client.get(f"/todos/{todo_id}/items", headers=headers)
        updated_items = get_response.json()["data"]
        assert updated_items[0]["title"] == "Updated Item 1"
        assert updated_items[0]["completed"] is True
        assert updated_items[1]["title"] == "Updated Item 2"
        assert updated_items[1]["completed"] is True

    @pytest.mark.asyncio
    async def test_delete_many_todo_list_items(
        self, client: AsyncClient, auth_token: str, test_todo_list: dict,
    ) -> None:
        """Test deleting multiple todo list items at once."""
        todo_id = test_todo_list["id"]
        headers = {"Authorization": f"Bearer {auth_token}"}

        # First create items
        create_payload = {"items": [{"title": "Item 1", "completed": False}, {"title": "Item 2", "completed": False}]}
        await client.post(f"/todos-batch/{todo_id}/items", json=create_payload, headers=headers)

        # Get the created item IDs
        get_response = await client.get(f"/todos/{todo_id}/items", headers=headers)
        items = get_response.json()["data"]
        item_ids = [item["id"] for item in items]

        # Delete items
        delete_payload = {"item_ids": item_ids}
        response: Response = await client.request(
            "DELETE", f"/todos-batch/{todo_id}/items", json=delete_payload, headers=headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully deleted 2 todo items"

        # Verify deletion
        get_response = await client.get(f"/todos/{todo_id}/items", headers=headers)
        assert len(get_response.json()["data"]) == 0
