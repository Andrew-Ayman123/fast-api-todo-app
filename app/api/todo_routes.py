from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.todo_model import TodoModel,TodoItemModel
from app.schemas.todo_schema import (
    TodoCreateRequest,
    TodoUpdateRequest,
    TodoItemsAddRequest,
    TodoItemUpdateRequest,
    TodoResponse,
    TodoItemResponse
)
from app.services.todo_service import TodoService
from app.dependencies import get_todo_service

router = APIRouter(prefix="/todos", tags=["todos"])

def _convert_todo_to_response(todo: TodoModel) -> TodoResponse:
    """Convert TodoModel to TodoResponse for consistent API response."""
    return TodoResponse(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
        todo_items=[_convert_todo_item_to_response(item) for item in todo.todo_items]
    )

def _convert_todo_item_to_response(item: TodoItemModel) -> TodoItemResponse:
    """Convert TodoItemModel to TodoItemResponse for consistent API response."""
    return TodoItemResponse(
        id=item.id,
        title=item.title,
        description=item.description,
        completed=item.completed,
        created_at=item.created_at,
        updated_at=item.updated_at
    )

@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo: TodoCreateRequest, todo_service: TodoService = Depends(get_todo_service)
):
    """
    Create a new todo list.
    
    Args:
        todo: Todo creation data including title and optional description
        
    Returns:
        The created todo with assigned ID
        
    Raises:
        422: Validation error if request data is invalid
    """
    created_todo = await todo_service.create_todo(todo)
    return _convert_todo_to_response(created_todo)

@router.get("/", response_model=List[TodoResponse])
async def get_todos(
    skip: int = 0,
    limit: int = 100,
    todo_service: TodoService = Depends(get_todo_service),
):
    """
    Retrieve all todo lists with pagination.
    
    Args:
        skip: Number of todos to skip (default: 0)
        limit: Maximum number of todos to return (default: 100)
        
    Returns:
        List of todos with pagination applied
    """
    return await todo_service.get_all_todos(skip, limit)

@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int, todo_service: TodoService = Depends(get_todo_service)
):
    """
    Retrieve a specific todo by ID.
    
    Args:
        todo_id: The unique identifier of the todo
        
    Returns:
        The requested todo
        
    Raises:
        404: Todo not found
    """
    todo = await todo_service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: int,
    todo: TodoUpdateRequest,
    todo_service: TodoService = Depends(get_todo_service),
):
    """
    Update an existing todo.
    
    Args:
        todo_id: The unique identifier of the todo to update
        todo: Updated todo data (title, description, etc.)
        
    Returns:
        The updated todo
        
    Raises:
        404: Todo not found
        422: Validation error if request data is invalid
    """
    updated_todo = await todo_service.update_todo(todo_id, todo)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo

@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int, todo_service: TodoService = Depends(get_todo_service)
):
    """
    Delete a todo and all its items.
    
    Args:
        todo_id: The unique identifier of the todo to delete
        
    Returns:
        Success message
        
    Raises:
        404: Todo not found
    """
    success = await todo_service.delete_todo(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}

@router.get("/{todo_id}/items", response_model=List[TodoItemResponse])
async def get_todo_items(
    todo_id: int,
    skip: int = 0,
    limit: int = 100,
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Retrieve all items from a specific todo with pagination.
    
    Args:
        todo_id: The unique identifier of the todo
        skip: Number of items to skip (default: 0)
        limit: Maximum number of items to return (default: 100)
        
    Returns:
        List of todo items with pagination applied
        
    Raises:
        404: Todo not found
    """
    return await todo_service.get_todo_items(todo_id, skip, limit)

@router.post("/{todo_id}/items", response_model=TodoItemResponse)
async def add_todo_item(
    todo_id: int,
    item: TodoItemsAddRequest,
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Add a new item to a specific todo.
    
    Args:
        todo_id: The unique identifier of the todo
        item: Item creation data including title and optional completion status
        
    Returns:
        The created todo item with assigned ID
        
    Raises:
        404: Todo not found
        422: Validation error if request data is invalid
    """
    added_item = await todo_service.add_todo_item(todo_id, item)
    if not added_item:
        raise HTTPException(status_code=404, detail="Todo not found")
    return added_item

@router.put("/{todo_id}/items/{item_id}", response_model=TodoItemResponse)
async def update_todo_item(
    todo_id: int,
    item_id: int,
    item: TodoItemUpdateRequest,
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Update a specific item within a todo.
    
    Args:
        todo_id: The unique identifier of the todo
        item_id: The unique identifier of the item to update
        item: Updated item data (title, completion status, etc.)
        
    Returns:
        The updated todo item
        
    Raises:
        404: Todo or item not found
        422: Validation error if request data is invalid
    """
    updated_item = await todo_service.update_todo_item(todo_id, item_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Todo or item not found")
    return updated_item

@router.delete("/{todo_id}/items/{item_id}")
async def delete_todo_item(
    todo_id: int,
    item_id: int,
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Delete a specific item from a todo.
    
    Args:
        todo_id: The unique identifier of the todo
        item_id: The unique identifier of the item to delete
        
    Returns:
        Success message
        
    Raises:
        404: Todo or item not found
    """
    success = await todo_service.delete_todo_item(todo_id, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo or item not found")
    return {"message": "Todo item deleted successfully"}
