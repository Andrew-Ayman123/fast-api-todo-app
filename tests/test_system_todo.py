"""Unit tests for TodoService.

This module contains unit tests for the TodoService class, testing its
interactions with the TodoRepositoryInterface.
"""

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from app.schemas.todo_schema import (
    TodoListCreateManyRequest,
    TodoListCreateRequest,
    TodoListDeleteManyRequest,
    TodoListUpdateItem,
    TodoListUpdateManyRequest,
    TodoListUpdateRequest,
)


@pytest.mark.usefixtures("reset_user_data_function")
class TestTodoListAPI:
    """System tests for Todo List endpoints."""

    @pytest.mark.asyncio
    async def test_create_todo_list(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test successful todo list creation."""
        payload = TodoListCreateRequest(
            title="Test Todo List",
            description="This is a test todo list",
        )

        response: Response = await client.post("/todos/", json=payload.model_dump(), headers=auth_token_header)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == payload.title
        assert data["description"] == payload.description
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_todo_lists(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test retrieving todo lists with pagination."""
        response: Response = await client.get("/todos/", headers=auth_token_header, params={"page": 1, "size": 10})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_get_todo_list_by_id(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test retrieving a specific todo list by ID."""
        create_payload = TodoListCreateRequest(
            title="Todo List for Retrieval",
            description="This todo list will be retrieved by ID",
        )
        create_response = await client.post("/todos/", json=create_payload.model_dump(), headers=auth_token_header)
        todo_id = create_response.json()["id"]

        response: Response = await client.get(f"/todos/{todo_id}", headers=auth_token_header)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == create_payload.title
        assert data["description"] == create_payload.description

    @pytest.mark.asyncio
    async def test_update_todo_list(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test updating a todo list."""
        create_payload = TodoListCreateRequest(
            title="Todo List to Update",
            description="This todo list will be updated",
        )
        create_response = await client.post("/todos/", json=create_payload.model_dump(), headers=auth_token_header)
        todo_id = create_response.json()["id"]

        update_payload = TodoListUpdateRequest(
            title="Updated Todo List Title",
        )
        response: Response = await client.put(
            f"/todos/{todo_id}",
            json=update_payload.model_dump(),
            headers=auth_token_header,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_payload.title
        assert data["description"] == update_payload.description

    @pytest.mark.asyncio
    async def test_delete_todo_list(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test deleting a todo list."""
        create_payload = TodoListCreateRequest(
            title="Todo List to Delete",
            description="This todo list will be deleted",
        )
        create_response = await client.post("/todos/", json=create_payload.model_dump(), headers=auth_token_header)
        todo_id = create_response.json()["id"]

        response: Response = await client.delete(f"/todos/{todo_id}", headers=auth_token_header)
        assert response.status_code == status.HTTP_200_OK

        verify_response = await client.get(f"/todos/{todo_id}", headers=auth_token_header)
        assert verify_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_many_todo_lists(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test batch creation of todo lists."""
        payload = TodoListCreateManyRequest(
            todo_lists=[
                TodoListCreateRequest(title="Batch Todo 1", description="First batch item"),
                TodoListCreateRequest(title="Batch Todo 2", description="Second batch item"),
            ],
        )
        response: Response = await client.post("/todos-batch/", json=payload.model_dump(), headers=auth_token_header)

        assert response.status_code == status.HTTP_200_OK

        response = await client.get("/todos/", headers=auth_token_header)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["data"]) >= 2

    @pytest.mark.asyncio
    async def test_update_many_todo_lists(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test batch update of todo lists."""
        create_response1 = await client.post(
            "/todos/",
            json=TodoListCreateRequest(title="Update Many 1").model_dump(),
            headers=auth_token_header,
        )
        create_response2 = await client.post(
            "/todos/",
            json=TodoListCreateRequest(title="Update Many 2").model_dump(),
            headers=auth_token_header,
        )
        id1 = create_response1.json()["id"]
        id2 = create_response2.json()["id"]

        payload = TodoListUpdateManyRequest(
            updates=[
                TodoListUpdateItem(
                    id=id1,
                    data=TodoListUpdateRequest(title="Updated Many 1", description="First updated"),
                ),
                TodoListUpdateItem(id=id2, data=TodoListUpdateRequest(title="Updated Many 2")),
            ],
        )
        response: Response = await client.put(
            "/todos-batch/",
            json=payload.model_dump(mode="json"),
            headers=auth_token_header,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Successfully updated 2 todo lists" in data["message"]

    @pytest.mark.asyncio
    async def test_delete_many_todo_lists(self, client: AsyncClient, auth_token_header: dict[str, str]) -> None:
        """Test batch deletion of todo lists."""
        create_response1 = await client.post(
            "/todos/",
            json=TodoListCreateRequest(title="Delete Many 1").model_dump(),
            headers=auth_token_header,
        )
        create_response2 = await client.post(
            "/todos/",
            json=TodoListCreateRequest(title="Delete Many 2").model_dump(),
            headers=auth_token_header,
        )
        id1 = create_response1.json()["id"]
        id2 = create_response2.json()["id"]

        payload = TodoListDeleteManyRequest(
            todo_ids=[
                id1,
                id2,
            ],
        )
        response = await client.request(
            "DELETE",
            "/todos-batch/",
            json=payload.model_dump(mode="json"),
            headers=auth_token_header,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Successfully deleted 2 todo lists" in data["message"]

        verify_response1 = await client.get(f"/todos/{id1}", headers=auth_token_header)
        verify_response2 = await client.get(f"/todos/{id2}", headers=auth_token_header)
        assert verify_response1.status_code == status.HTTP_404_NOT_FOUND
        assert verify_response2.status_code == status.HTTP_404_NOT_FOUND
