"""Unit tests for UserRepositoryInterface.

This module contains unit tests for the UserRepositoryInterface using a concrete
test implementation to verify the expected behavior of all interface methods.
"""

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from app.models.user_model import UserModel
from app.repositories.user_pg_repository_impl import UserPGRepository
from tests.test_dependencies import get_session_maker_test


class TestUserRepository:
    """Test suite for UserPGRepository."""

    @pytest_asyncio.fixture
    async def user_repo(self) -> AsyncGenerator[UserPGRepository, None]:
        """Create a fresh test repository instance for each test."""
        session_maker = get_session_maker_test()
        async with session_maker() as session:
            repo = UserPGRepository(session=session)
            yield repo

    @pytest.fixture
    def sample_user_data(self) -> dict[str, str]:
        """Sample user data for testing."""
        return {"email": "test@example.com", "username": "testuser", "password_hash": "hashed_password_123"}

    @pytest_asyncio.fixture(autouse=True)
    async def cleanup_user_table(self, user_repo: UserPGRepository) -> AsyncGenerator[None, None]:
        """Automatically clear the user table before and after each test."""
        yield
        await user_repo.session.execute(text("DELETE FROM users"))
        await user_repo.session.commit()

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_repo: UserPGRepository,
        sample_user_data: dict[str, str],
    ) -> None:
        """Test successful user creation."""
        result = await user_repo.create_user(**sample_user_data)
        assert result is not None
        assert isinstance(result, UserModel)
        assert result.email == sample_user_data["email"]
        assert result.username == sample_user_data["username"]
        assert result.password == sample_user_data["password_hash"]
        assert isinstance(result.id, uuid.UUID)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self,
        user_repo: UserPGRepository,
        sample_user_data: dict[str, str],
    ) -> None:
        """Test user creation with duplicate email should fail."""
        # Create first user
        first_user = await user_repo.create_user(**sample_user_data)
        assert first_user is not None

        with pytest.raises(IntegrityError):
            await user_repo.create_user(**sample_user_data)

        # Roll back the session after the exception
        await user_repo.session.rollback()

        # count number of users in the db, should be 1
        result = await user_repo.session.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar_one()

        assert count == 1, "There should be only one user in the database after duplicate creation attempt."

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self,
        user_repo: UserPGRepository,
        sample_user_data: dict[str, str],
    ) -> None:
        """Test successful user retrieval by ID."""
        # Create a user first
        created_user = await user_repo.create_user(**sample_user_data)
        assert created_user is not None

        # Retrieve the user by ID
        result = await user_repo.get_user_by_id(created_user.id)

        assert result is not None
        assert result.id == created_user.id
        assert result.email == sample_user_data["email"]
        assert result.username == sample_user_data["username"]
        assert result.password == sample_user_data["password_hash"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_repo: UserPGRepository) -> None:
        """Test user retrieval by ID when user doesn't exist."""
        non_existent_id = uuid.uuid4()

        result = await user_repo.get_user_by_id(non_existent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(
        self,
        user_repo: UserPGRepository,
        sample_user_data: dict[str, str],
    ) -> None:
        """Test successful user retrieval by email."""
        # Create a user first
        created_user = await user_repo.create_user(**sample_user_data)
        assert created_user is not None

        # Retrieve the user by email
        result = await user_repo.get_user_by_email(sample_user_data["email"])

        assert result is not None
        assert result.id == created_user.id
        assert result.email == sample_user_data["email"]
        assert result.username == sample_user_data["username"]
        assert result.password == sample_user_data["password_hash"]

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_repo: UserPGRepository) -> None:
        """Test user retrieval by email when user doesn't exist."""
        non_existent_email = "nonexistent@example.com"

        result = await user_repo.get_user_by_email(non_existent_email)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_multiple_users(self, user_repo: UserPGRepository) -> None:
        """Test creating multiple users with different data."""
        users_data = [
            {"email": "user1@example.com", "username": "user1", "password_hash": "hash1"},
            {"email": "user2@example.com", "username": "user2", "password_hash": "hash2"},
            {"email": "user3@example.com", "username": "user3", "password_hash": "hash3"},
        ]

        created_users = []
        for user_data in users_data:
            user = await user_repo.create_user(**user_data)
            assert user is not None
            created_users.append(user)

        # Verify all users can be retrieved
        for i, user in enumerate(created_users):
            retrieved_by_id = await user_repo.get_user_by_id(user.id)
            retrieved_by_email = await user_repo.get_user_by_email(users_data[i]["email"])

            assert retrieved_by_id is not None
            assert retrieved_by_email is not None
            assert retrieved_by_id.id == retrieved_by_email.id == user.id

    @pytest.mark.asyncio
    async def test_email_case_sensitivity(
        self,
        user_repo: UserPGRepository,
        sample_user_data: dict[str, str],
    ) -> None:
        """Test email case sensitivity behavior."""
        # Create user with lowercase email
        lower_email = sample_user_data["email"].lower()
        user_data = sample_user_data.copy()
        user_data["email"] = lower_email

        created_user = await user_repo.create_user(**user_data)
        assert created_user is not None

        # Try to retrieve with different case
        upper_email = lower_email.upper()
        result = await user_repo.get_user_by_email(upper_email)

        # This test depends on your business logic - adjust assertion as needed
        # Most systems treat emails as case-insensitive
        assert result is None  # Assuming case-sensitive implementation
