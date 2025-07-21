

import uuid


class WrongEmailOrPasswordException(Exception):
    """Exception raised when the email or password is incorrect."""
    
    def __init__(self) -> None:
        """Initialize the exception with a default message."""
        super().__init__("Wrong email or password.")


class UserAlreadyExistsException(Exception):
    """Exception raised when a user with the same email already exists."""
    
    def __init__(self, email: str) -> None:
        """Initialize with the email that already exists."""
        self.email = email
        super().__init__(f"User with email {self.email} already exists.")

class UserIDNotFoundException(Exception):
    """Exception raised when a user is not found."""

    def __init__(self, user_id: uuid.UUID) -> None:
        """Initialize with the user ID that was not found."""
        self.user_id = user_id
        super().__init__(f"User with ID {self.user_id} not found.")