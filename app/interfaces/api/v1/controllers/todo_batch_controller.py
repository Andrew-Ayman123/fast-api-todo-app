"""FastAPI Todo API Controller."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.dependencies import get_todo_service
from app.exceptions.todo_exception import TodoListItemNotFoundError, TodoListNotFoundError
from app.middleware.jwt_middleware import JWTBearer
from app.models.todo_model import TodoListItemModel, TodoListModel
from app.schemas.todo_schema import (
    SuccessResponse,
    TodoListCreateManyRequest,
    TodoListDeleteManyRequest,
    TodoListItemCreateManyRequest,
    TodoListItemDeleteManyRequest,
    TodoListItemResponse,
    TodoListItemUpdateManyRequest,
    TodoListResponse,
    TodoListUpdateManyRequest,
)
from app.services.todo_service import TodoService
from app.utils.logger_util import get_logger

router = APIRouter(prefix="/todos-batch", tags=["todos-batch"])


def _convert_todo_to_response(todo: TodoListModel) -> TodoListResponse:
    """Convert TodoListModel to TodoListResponse for consistent API response.

    Args:
        todo (TodoListModel): The todo model to convert

    Returns:
        TodoListResponse: The converted todo response object

    """
    return TodoListResponse.model_validate(todo)


def _convert_todo_item_to_response(item: TodoListItemModel) -> TodoListItemResponse:
    """Convert TodoListItemModel to TodoListItemResponse for consistent API response.

    Args:
        item (TodoListItemModel): The todo item model to convert

    Returns:
        TodoListItemResponse: The converted todo item response object

    """
    return TodoListItemResponse.model_validate(item)


@router.post("/", dependencies=[Depends(JWTBearer())])
async def create_many_todo_lists(
    request: TodoListCreateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Request,
) -> SuccessResponse:
    """Create multiple todo lists at once.

    Args:
        todo_service (TodoService): The todo service dependency
        request (TodoListCreateManyRequest): List of todo lists to create
        req (Request): The request object containing user context

    Returns:
        SuccessResponse: Success message with created count

    Raises:
        HTTPException: 422 - Validation error if request data is invalid
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = req.state.user_id
        created_todos = await todo_service.create_many_todo_lists(request.todo_lists, user_id)
        return SuccessResponse(message=f"Successfully created {len(created_todos)} todo lists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create todo lists: {e!s}") from e


@router.put("/", dependencies=[Depends(JWTBearer())])
async def update_many_todo_lists(
    request: TodoListUpdateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Request,
) -> SuccessResponse:
    """Update multiple todo lists at once.

    Args:
        todo_service (TodoService): The todo service dependency
        request (TodoListUpdateManyRequest): List of updates with todo IDs and update data
        req (Request): The request object containing user context

    Returns:
        SuccessResponse: Success message with updated count

    Raises:
        HTTPException: 404 - One or more todos not found
        HTTPException: 422 - Validation error if request data is invalid
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = req.state.user_id
        updated_todos = await todo_service.update_many_todo_lists(request.updates, user_id)
        return SuccessResponse(message=f"Successfully updated {len(updated_todos)} todo lists")
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="One or more todos not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update todo lists: {e!s}") from e


@router.delete("/", status_code=200, dependencies=[Depends(JWTBearer())])
async def delete_many_todo_lists(
    request: TodoListDeleteManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Request,
) -> SuccessResponse:
    """Delete multiple todo lists at once.

    Args:
        todo_service (TodoService): The todo service dependency
        request (TodoListDeleteManyRequest): List of todo IDs to delete
        req (Request): The request object containing user context

    Returns:
        SuccessResponse: Success message with deleted count

    Raises:
        HTTPException: 404 - One or more todos not found
        HTTPException: 500 - Internal server error

    """
    try:
        get_logger().debug("Deleting todo lists with IDs: %s for user: %s", request.todo_ids)
        user_id = req.state.user_id
        await todo_service.delete_many_todo_lists(request.todo_ids, user_id)
        return SuccessResponse(message=f"Successfully deleted {len(request.todo_ids)} todo lists")
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="One or more todos not found") from e
    except Exception as e:

        get_logger().error("Error deleting todo lists: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete todo lists: {e!s}") from e


@router.post("/{todo_id}/items", dependencies=[Depends(JWTBearer())])
async def create_many_todo_list_items(
    todo_id: str,
    request: TodoListItemCreateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Request,
) -> SuccessResponse:
    """Add multiple items to a specific todo list.

    Args:
        todo_id (str): The unique identifier of the todo list
        todo_service (TodoService): The todo service dependency
        request (TodoListItemCreateManyRequest): List of todo items to add
        req (Request): The request object containing user context

    Returns:
        SuccessResponse: Success message with created count

    Raises:
        HTTPException: 404 - Todo list not found
        HTTPException: 422 - Validation error if request data is invalid
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = req.state.user_id
        created_items = await todo_service.create_many_todo_list_items(todo_id, request.items, user_id)
        return SuccessResponse(message=f"Successfully created {len(created_items)} todo items")
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo list not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create todo items: {e!s}") from e


@router.put("/{todo_id}/items", dependencies=[Depends(JWTBearer())])
async def update_many_todo_list_items(
    todo_id: str,
    request: TodoListItemUpdateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Request,
) -> SuccessResponse:
    """Update multiple items in a specific todo list.

    Args:
        todo_id (str): The unique identifier of the todo list
        todo_service (TodoService): The todo service dependency
        request (TodoListItemUpdateManyRequest): List of updates with item IDs and update data
        req (Request): The request object containing user context

    Returns:
        SuccessResponse: Success message with updated count

    Raises:
        HTTPException: 404 - Todo list or one or more items not found
        HTTPException: 422 - Validation error if request data is invalid
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = req.state.user_id
        updated_items = await todo_service.update_many_todo_list_items(todo_id, request.updates, user_id)
        return SuccessResponse(message=f"Successfully updated {len(updated_items)} todo items")
    except TodoListItemNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo list or one or more items not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update todo items: {e!s}") from e


@router.delete("/{todo_id}/items", status_code=200, dependencies=[Depends(JWTBearer())])
async def delete_many_todo_list_items(
    todo_id: str,
    request: TodoListItemDeleteManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Request,
) -> SuccessResponse:
    """Delete multiple items from a specific todo list.

    Args:
        todo_id (str): The unique identifier of the todo list
        todo_service (TodoService): The todo service dependency
        request (TodoListItemDeleteManyRequest): List of item IDs to delete
        req (Request): The request object containing user context

    Returns:
        SuccessResponse: Success message with deleted count

    Raises:
        HTTPException: 404 - Todo list or one or more items not found
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = req.state.user_id
        await todo_service.delete_many_todo_list_items(todo_id, request.item_ids, user_id)
        return SuccessResponse(message=f"Successfully deleted {len(request.item_ids)} todo items")
    except TodoListItemNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo list or one or more items not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete todo items: {e!s}") from e
