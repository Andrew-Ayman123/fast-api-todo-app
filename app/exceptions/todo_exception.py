"""Custom exceptions for the Todo application."""

import uuid


class TodoListNotFoundError(Exception):
    """Exception raised when a todo list is not found."""

    def __init__(self, todo_id: uuid.UUID) -> None:
        """Initialize with the todo ID that was not found.

        Args:
            todo_id (uuid.UUID): ID of the todo list that was not found.

        """
        self.todo_id = todo_id
        super().__init__(f"Todo list with ID {self.todo_id} not found.")


class TodoListItemNotFoundError(Exception):
    """Exception raised when a todo item is not found in a todo list."""

    def __init__(self, todo_id: uuid.UUID, item_id: uuid.UUID) -> None:
        """Initialize with the todo ID and item ID that were not found.

        Args:
            todo_id (uuid.UUID): ID of the todo list that was not found.
            item_id (uuid.UUID): ID of the todo item that was not found.

        """
        self.todo_id = todo_id
        self.item_id = item_id
        super().__init__(f"Todo item with ID {self.item_id} in todo list {self.todo_id} not found.")
