"""System tests for User API endpoints."""

import logging
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy import text

from tests.test_dependencies import get_session_maker_test

logger = logging.getLogger(__name__)


class TestUserAPI:
    """System tests for user registration, login, and profile endpoints."""

    token: str = ""

    @pytest_asyncio.fixture(scope="class", autouse=True)
    async def setup_and_teardown_class(self) -> AsyncGenerator:
        """Delete all users before all tests and after all tests in this class."""
        session_maker = get_session_maker_test()
        async with session_maker() as session:
            await session.execute(text("DELETE FROM todos"))
            await session.commit()
        yield
        async with session_maker() as session:
            await session.execute(text("DELETE FROM todos"))
            await session.commit()

    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient) -> None:
        """Test successful user registration."""
        payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123",
            "username": "Test User",
        }
        response: Response = await client.post("/user/register", json=payload, follow_redirects=False)

        assert response.url == "http://testserver/api/v1/user/register"
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.json()
        assert response.json()["email"] == payload["email"]

    @pytest.mark.asyncio
    async def test_register_user_conflict(self, client: AsyncClient) -> None:
        """Test registering a user that already exists returns conflict."""
        payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123",
            "username": "Test User",
        }
        response: Response = await client.post("/user/register", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_user(self, client: AsyncClient) -> None:
        """Test successful login of a registered user."""
        payload = {
            "email": "testuser@example.com",
            "password": "TestPassword123",
        }
        response: Response = await client.post("/user/login", json=payload)

        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.json()

        # Save the token for the next test
        self.__class__.token = response.json()["token"]

    @pytest.mark.asyncio
    async def test_login_wrong_credentials(self, client: AsyncClient) -> None:
        """Test login failure with incorrect credentials."""
        payload = {
            "email": "testuser@example.com",
            "password": "WrongPassword",
        }
        response: Response = await client.post("/user/login", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Wrong email or password"

    @pytest.mark.asyncio
    async def test_get_profile_success(self, client: AsyncClient) -> None:
        """Test successful retrieval of user profile with valid JWT."""
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        response: Response = await client.get("/user/profile", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "testuser@example.com"

    @pytest.mark.asyncio
    async def test_get_profile_unauthorized(self, client: AsyncClient) -> None:
        """Test unauthorized access to profile without token."""
        response: Response = await client.get("/user/profile")

        assert response.status_code == status.HTTP_403_FORBIDDEN
