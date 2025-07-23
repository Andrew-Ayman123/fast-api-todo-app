"""Unit tests for TodoService.

This module contains unit tests for the TodoService class, testing its
interactions with the TodoRepositoryInterface.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy import text

from tests.test_dependencies import get_session_maker_test


class TestTodoListAPI:
    """System tests for Todo List endpoints."""

    @pytest_asyncio.fixture(scope="class")
    async def setup_and_teardown_class(self, client: AsyncClient) -> AsyncGenerator:
        """Clean up todos before and after tests."""
        session_maker = get_session_maker_test()
        async with session_maker() as session:
            await session.execute(text("DELETE FROM users"))
            await session.commit()

        user_payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123",
            "username": "Test User",
        }
        # Use the registration endpoint to create the user
        await client.post("/user/register", json=user_payload)
        yield

        # Clean after test
        async with session_maker() as session:
            await session.execute(text("DELETE FROM users"))
            await session.commit()

    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def setup_and_teardown_every_test(self, setup_and_teardown_class: AsyncGenerator) -> AsyncGenerator:  # noqa: ARG002
        """Clean up todos before and after tests."""
        # using setup_and_teardown_class to make sure it runs after the class setup
        session_maker = get_session_maker_test()
        async with session_maker() as session:
            await session.execute(text("DELETE FROM todos"))
            await session.commit()

        yield
        session_maker = get_session_maker_test()
        async with session_maker() as session:
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

    @pytest.mark.asyncio
    async def test_create_todo_list(self, client: AsyncClient, auth_token: str) -> None:
        """Test successful todo list creation."""
        payload = {"title": "Test Todo List", "description": "Test description"}
        headers = {"Authorization": f"Bearer {auth_token}"}
        response: Response = await client.post("/todos/", json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["description"] == payload["description"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_todo_lists(self, client: AsyncClient, auth_token: str) -> None:
        """Test retrieving todo lists with pagination."""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response: Response = await client.get("/todos/", headers=headers, params={"page": 1, "size": 10})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "size" in data
        assert "current_page" in data
        assert "total_pages" in data

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id(self, client: AsyncClient, auth_token: str) -> None:
        """Test retrieving a specific todo list by ID."""
        # First create a todo list to get its ID
        create_payload = {"title": "Test Get By ID"}
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response = await client.post("/todos/", json=create_payload, headers=headers)
        todo_id = create_response.json()["id"]

        response: Response = await client.get(f"/todos/{todo_id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == create_payload["title"]

    @pytest.mark.asyncio
    async def test_update_todo_list(self, client: AsyncClient, auth_token: str) -> None:
        """Test updating a todo list."""
        # First create a todo list
        create_payload = {"title": "Original Title"}
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response = await client.post("/todos/", json=create_payload, headers=headers)
        todo_id = create_response.json()["id"]

        # Update the todo list
        update_payload = {"title": "Updated Title", "description": "New description"}
        response: Response = await client.put(f"/todos/{todo_id}", json=update_payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_payload["title"]
        assert data["description"] == update_payload["description"]

    @pytest.mark.asyncio
    async def test_delete_todo_list(self, client: AsyncClient, auth_token: str) -> None:
        """Test deleting a todo list."""
        # First create a todo list
        create_payload = {"title": "To Be Deleted"}
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response = await client.post("/todos/", json=create_payload, headers=headers)
        todo_id = create_response.json()["id"]

        # Delete the todo list
        response: Response = await client.delete(f"/todos/{todo_id}", headers=headers)

        assert response.status_code == status.HTTP_200_OK

        # Verify it's deleted
        verify_response = await client.get(f"/todos/{todo_id}", headers=headers)
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_many_todo_lists(self, client: AsyncClient, auth_token: str) -> None:
        """Test batch creation of todo lists."""
        payload = {"todo_lists": [{"title": "Batch 1"}, {"title": "Batch 2", "description": "Second item"}]}
        headers = {"Authorization": f"Bearer {auth_token}"}
        response: Response = await client.post("/todos-batch/", json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Successfully created 2 todo lists" in data["message"]

    @pytest.mark.asyncio
    async def test_update_many_todo_lists(self, client: AsyncClient, auth_token: str) -> None:
        """Test batch update of todo lists."""
        # First create some todo lists
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response1 = await client.post("/todos/", json={"title": "Update Many 1"}, headers=headers)
        create_response2 = await client.post("/todos/", json={"title": "Update Many 2"}, headers=headers)
        id1 = create_response1.json()["id"]
        id2 = create_response2.json()["id"]

        # Update them
        payload = {
            "updates": [
                {"id": id1, "data": {"title": "Updated Many 1", "description": "First updated"}},
                {"id": id2, "data": {"title": "Updated Many 2"}},
            ],
        }
        response: Response = await client.put("/todos-batch/", json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Successfully updated 2 todo lists" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_many_todo_lists(self, client: AsyncClient, auth_token: str) -> None:
        """Test batch deletion of todo lists."""
        # First create some todo lists
        headers = {"Authorization": f"Bearer {auth_token}"}
        create_response1 = await client.post("/todos/", json={"title": "Delete Many 1"}, headers=headers)
        create_response2 = await client.post("/todos/", json={"title": "Delete Many 2"}, headers=headers)
        id1 = str(create_response1.json()["id"])
        id2 = str(create_response2.json()["id"])

        # Delete them
        payload = {"todo_ids": [id1, id2]}
        response = await client.request("DELETE", "/todos-batch/", json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Successfully deleted 2 todo lists" in data["message"]

        # Verify they're deleted
        verify_response1 = await client.get(f"/todos/{id1}", headers=headers)
        verify_response2 = await client.get(f"/todos/{id2}", headers=headers)
        assert verify_response1.status_code == status.HTTP_404_NOT_FOUND
        assert verify_response2.status_code == status.HTTP_404_NOT_FOUND
