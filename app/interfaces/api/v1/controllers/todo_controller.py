"""FastAPI Todo API Controller."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.dependencies import get_todo_service
from app.exceptions.todo_exception import TodoListItemNotFoundError, TodoListNotFoundError
from app.middleware.jwt_middleware import JWTBearer
from app.models.todo_model import TodoListItemModel, TodoListModel
from app.schemas.todo_schema import (
    PaginatedTodoListItemResponse,
    PaginatedTodoListResponse,
    SuccessResponse,
    TodoListCreateManyRequest,
    TodoListCreateRequest,
    TodoListDeleteManyRequest,
    TodoListItemCreateManyRequest,
    TodoListItemDeleteManyRequest,
    TodoListItemResponse,
    TodoListItemsAddRequest,
    TodoListItemUpdateManyRequest,
    TodoListItemUpdateRequest,
    TodoListResponse,
    TodoListUpdateManyRequest,
    TodoListUpdateRequest,
)
from app.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


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
async def create_todo_list(
    todo: TodoListCreateRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    request: Annotated[Request, Depends()],
) -> TodoListResponse:
    """Create a new todo list.

    Args:
        todo_service (TodoService): The todo service dependency
        todo (TodoListCreateRequest): Todo creation data including title and optional description
        request (Request): The request object containing user context

    Returns:
        TodoListResponse: The created todo with assigned ID

    Raises:
        HTTPException: 422 - Validation error if request data is invalid
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = request.state.user_id
        created_todo = await todo_service.create_todo_list(todo, user_id)
        return _convert_todo_to_response(created_todo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create todo list: {e!s}") from e


@router.get("/", dependencies=[Depends(JWTBearer())])
async def get_todo_lists(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    request: Annotated[Request, Depends()],
    page: int = 1,
    size: int = 20,
) -> PaginatedTodoListResponse:
    """Retrieve all todo lists with pagination.

    Args:
        todo_service (TodoService): The todo service dependency
        page (int, optional): Page number. Defaults to 1.
        size (int, optional): Page size. Defaults to 20.
        request (Request): The request object containing user context

    Returns:
        PaginatedTodoListResponse: Paginated list of todos

    Raises:
        HTTPException: 404 - Not Found

    """
    try:
        skip = (page - 1) * size
        user_id = request.state.user_id
        todos = await todo_service.get_all_todo_lists_without_items(user_id, skip, size)
        total = await todo_service.count_todo_lists(user_id)
        total = total if total is not None else (skip + len(todos))
        total_pages = (total + size - 1) // size if size > 0 else 1
        return PaginatedTodoListResponse(
            data=[_convert_todo_to_response(todo) for todo in todos],
            size=len(todos),
            current_page=page,
            total_pages=total_pages,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to retrieve todo lists: {e!s}") from e


@router.get("/{todo_id}", dependencies=[Depends(JWTBearer())])
async def get_todo_list_by_id(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    todo_id: str,
    request: Annotated[Request, Depends()],
) -> TodoListResponse:
    """Retrieve a specific todo by ID.

    Args:
        todo_service (TodoService): The todo service dependency
        todo_id (str): The unique identifier of the todo
        request (Request): The request object containing user context

    Returns:
        TodoListResponse: The requested todo

    Raises:
        HTTPException: 404 - Todo not found
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = request.state.user_id
        todo = await todo_service.get_todo_list_by_id(todo_id, user_id)
        return _convert_todo_to_response(todo)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve todo: {e!s}") from e


@router.put("/{todo_id}", dependencies=[Depends(JWTBearer())])
async def update_todo_list(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    todo_id: str,
    todo: TodoListUpdateRequest,
    request: Annotated[Request, Depends()],
) -> TodoListResponse:
    """Update an existing todo.

    Args:
        todo_service (TodoService): The todo service dependency
        todo_id (str): The unique identifier of the todo to update
        todo (TodoListUpdateRequest): Updated todo data (title, description, etc.)
        request (Request): The request object containing user context

    Returns:
        TodoListResponse: The updated todo

    Raises:
        HTTPException: 404 - Todo not found
        HTTPException: 422 - Validation error if request data is invalid

    """
    try:
        user_id = request.state.user_id
        updated_todo = await todo_service.update_todo_list(todo_id, todo, user_id)
        return _convert_todo_to_response(updated_todo)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update todo: {e!s}") from e


@router.delete("/{todo_id}", status_code=200, dependencies=[Depends(JWTBearer())])
async def delete_todo_list(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    todo_id: str,
    request: Annotated[Request, Depends()],
) -> None:
    """Delete a todo and all its items.

    Args:
        todo_service (TodoService): The todo service dependency
        todo_id (str): The unique identifier of the todo to delete
        request (Request): The request object containing user context

    Returns:
        None: HTTP 200 status on successful deletion

    Raises:
        HTTPException: 404 - Todo not found
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = request.state.user_id
        await todo_service.delete_todo_list(todo_id, user_id)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete todo: {e!s}") from e


@router.get("/{todo_id}/items", dependencies=[Depends(JWTBearer())])
async def get_todo_list_items(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    request: Annotated[Request, Depends()],
    todo_id: str,
    page: int = 1,
    size: int = 20,
) -> PaginatedTodoListItemResponse:
    """Retrieve all items from a specific todo with pagination.

    Args:
        todo_service (TodoService): The todo service dependency
        todo_id (str): The unique identifier of the todo
        page (int, optional): Page number. Defaults to 1.
        size (int, optional): Page size. Defaults to 20.
        request (Request): The request object containing user context

    Returns:
        PaginatedTodoListItemResponse: Paginated list of todo items

    Raises:
        HTTPException: 404 - Todo not found
        HTTPException: 500 - Internal server error

    """
    try:
        skip = (page - 1) * size
        user_id = request.state.user_id
        items = await todo_service.get_todo_list_items(todo_id, user_id, skip, size)
        total = await todo_service.count_todo_list_items(todo_id, user_id)
        total = total if total is not None else (skip + len(items))
        total_pages = (total + size - 1) // size if size > 0 else 1
        return PaginatedTodoListItemResponse(
            data=[_convert_todo_item_to_response(item) for item in items],
            size=len(items),
            current_page=page,
            total_pages=total_pages,
        )
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve todo items: {e!s}") from e


@router.post("/{todo_id}/items", dependencies=[Depends(JWTBearer())])
async def add_todo_list_item(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    todo_id: str,
    item: TodoListItemsAddRequest,
    request: Annotated[Request, Depends()],
) -> TodoListItemResponse:
    """Add a new item to a specific todo.

    Args:
        todo_service (TodoService): The todo service dependency
        todo_id (str): The unique identifier of the todo
        item (TodoListItemsAddRequest): Item creation data including title and optional completion status
        request (Request): The request object containing user context

    Returns:
        TodoListItemResponse: The created todo item with assigned ID

    Raises:
        HTTPException: 404 - Todo not found
        HTTPException: 422 - Validation error if request data is invalid
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = request.state.user_id
        created_item = await todo_service.add_todo_list_item(todo_id, item, user_id)
        return _convert_todo_item_to_response(created_item)
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add todo item: {e!s}") from e


@router.put("/{todo_id}/items/{item_id}", dependencies=[Depends(JWTBearer())])
async def update_todo_list_item(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    todo_id: str,
    item_id: str,
    item: TodoListItemUpdateRequest,
    request: Annotated[Request, Depends()],
) -> TodoListItemResponse:
    """Update a specific item within a todo.

    Args:
        todo_service (TodoService): The todo service dependency
        todo_id (str): The unique identifier of the todo
        item_id (str): The unique identifier of the item to update
        item (TodoListItemUpdateRequest): Updated item data (title, completion status, etc.)
        request (Request): The request object containing user context

    Returns:
        TodoListItemResponse: The updated todo item

    Raises:
        HTTPException: 404 - Todo or item not found
        HTTPException: 422 - Validation error if request data is invalid
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = request.state.user_id
        updated_item = await todo_service.update_todo_item(todo_id, item_id, item, user_id)
        return _convert_todo_item_to_response(updated_item)
    except TodoListItemNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo or item not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update todo item: {e!s}") from e


@router.delete("/{todo_id}/items/{item_id}", status_code=200, dependencies=[Depends(JWTBearer())])
async def delete_todo_list_item(
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    todo_id: str,
    item_id: str,
    request: Annotated[Request, Depends()],
) -> None:
    """Delete a specific item from a todo.

    Args:
        todo_service (TodoService): The todo service dependency
        todo_id (str): The unique identifier of the todo
        item_id (str): The unique identifier of the item to delete
        request (Request): The request object containing user context

    Returns:
        None: HTTP 200 status on successful deletion

    Raises:
        HTTPException: 404 - Todo or item not found
        HTTPException: 500 - Internal server error

    """
    try:
        user_id = request.state.user_id
        await todo_service.delete_todo_list_item(todo_id, item_id, user_id)
    except TodoListItemNotFoundError as e:
        raise HTTPException(status_code=404, detail="Todo or item not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete todo item: {e!s}") from e


@router.post("/batch", dependencies=[Depends(JWTBearer())])
async def create_many_todo_lists(
    request: TodoListCreateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Annotated[Request, Depends()],
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


@router.put("/batch", dependencies=[Depends(JWTBearer())])
async def update_many_todo_lists(
    request: TodoListUpdateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Annotated[Request, Depends()],
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


@router.delete("/batch", status_code=200, dependencies=[Depends(JWTBearer())])
async def delete_many_todo_lists(
    request: TodoListDeleteManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Annotated[Request, Depends()],
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
        user_id = req.state.user_id
        await todo_service.delete_many_todo_lists(request.todo_ids, user_id)
        return SuccessResponse(message=f"Successfully deleted {len(request.todo_ids)} todo lists")
    except TodoListNotFoundError as e:
        raise HTTPException(status_code=404, detail="One or more todos not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete todo lists: {e!s}") from e


@router.post("/{todo_id}/items/batch", dependencies=[Depends(JWTBearer())])
async def create_many_todo_list_items(
    todo_id: str,
    request: TodoListItemCreateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Annotated[Request, Depends()],
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


@router.put("/{todo_id}/items/batch", dependencies=[Depends(JWTBearer())])
async def update_many_todo_list_items(
    todo_id: str,
    request: TodoListItemUpdateManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Annotated[Request, Depends()],
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


@router.delete("/{todo_id}/items/batch", status_code=200, dependencies=[Depends(JWTBearer())])
async def delete_many_todo_list_items(
    todo_id: str,
    request: TodoListItemDeleteManyRequest,
    todo_service: Annotated[TodoService, Depends(get_todo_service)],
    req: Annotated[Request, Depends()],
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
