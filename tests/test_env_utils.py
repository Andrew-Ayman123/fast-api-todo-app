"""Unit tests for environment utility functions."""
from unittest.mock import patch

import pytest

from app.utils.env_util import get_env, get_env_bool, get_env_int


class TestEnvUtils:
    """Unit tests for environment utility functions."""

    def test_get_env_with_existing_variable(self) -> None:
        """Test getting an environment variable that exists."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "test_value"

            result = get_env("TEST_VAR")

            mock_getenv.assert_called_once_with("TEST_VAR", None)
            assert result == "test_value"

    def test_get_env_with_default_value(self) -> None:
        """Test getting an environment variable with a default value."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "default_value"

            result = get_env("NON_EXISTENT_VAR", "default_value")

            mock_getenv.assert_called_once_with("NON_EXISTENT_VAR", "default_value")
            assert result == "default_value"

    def test_get_env_with_none_value(self) -> None:
        """Test getting an environment variable that doesn't exist without default."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = None

            result = get_env("NON_EXISTENT_VAR")

            mock_getenv.assert_called_once_with("NON_EXISTENT_VAR", None)
            assert result is None

    def test_get_env_int_with_valid_integer(self) -> None:
        """Test getting an environment variable as integer with valid value."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "42"

            result = get_env_int("TEST_INT_VAR")

            mock_getenv.assert_called_once_with("TEST_INT_VAR", None)
            assert result == 42
            assert isinstance(result, int)

    def test_get_env_int_with_default_value(self) -> None:
        """Test getting an environment variable as integer with default value."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = 100

            result = get_env_int("NON_EXISTENT_INT_VAR", 100)

            mock_getenv.assert_called_once_with("NON_EXISTENT_INT_VAR", 100)
            assert result == 100
            assert isinstance(result, int)


    def test_get_env_bool_with_true_string(self) -> None:
        """Test getting an environment variable as boolean with 'true' value."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "true"

            result = get_env_bool("TEST_BOOL_VAR")

            mock_getenv.assert_called_once_with("TEST_BOOL_VAR", None)
            assert result is True
            assert isinstance(result, bool)

    def test_get_env_bool_case_insensitive(self) -> None:
        """Test that get_env_bool is case insensitive for string values."""
        test_cases = [
            ("True", True),
            ("TRUE", True),
            ("tRuE", True),
            ("False", False),
            ("FALSE", False),
            ("fAlSe", False),
            ("Yes", True),
            ("YES", True),
            ("yEs", True),
            ("No", False),
            ("NO", False),
            ("nO", False),
        ]

        for input_value, expected_result in test_cases:
            with patch("os.getenv") as mock_getenv:
                mock_getenv.return_value = input_value

                result = get_env_bool("TEST_VAR")

                assert result is expected_result, f"Failed for input '{input_value}'"

    def test_get_env_int_with_invalid_string_should_raise_error(self) -> None:
        """Test that get_env_int raises ValueError for invalid integer strings."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "not_a_number"

            with pytest.raises(ValueError):
                get_env_int("INVALID_INT_VAR")

    def test_get_env_int_with_float_string_should_raise_error(self) -> None:
        """Test that get_env_int raises ValueError for float strings."""
        with patch("os.getenv") as mock_getenv:
            mock_getenv.return_value = "42.5"

            with pytest.raises(ValueError):
                get_env_int("FLOAT_VAR")
