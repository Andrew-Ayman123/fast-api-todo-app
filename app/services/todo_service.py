from typing import List, Optional
from app.models.todo_model import TodoModel, TodoItemModel
from app.schemas.todo_schema import TodoCreateRequest, TodoUpdateRequest, TodoItemsAddRequest, TodoItemUpdateRequest
from app.repositories.todo_repository import TodoRepositoryInterface

class TodoService:
    
    def __init__(self, todo_repository: TodoRepositoryInterface):
        self.todo_repository = todo_repository
    
    async def create_todo(self, todo_data: TodoCreateRequest) -> TodoModel:
        todo = await self.todo_repository.create_todo(todo_data)
        return todo

    async def get_todo(self, todo_id: int) -> Optional[TodoModel]:
        todo = await self.todo_repository.get_todo_by_id(todo_id)
        return todo if todo else None

    async def get_all_todos(self, skip: int = 0, limit: int = 100) -> List[TodoModel]:
        todos = await self.todo_repository.get_all_todos(skip, limit)
        return todos

    async def update_todo(self, todo_id: int, todo_data: TodoUpdateRequest) -> Optional[TodoModel]:
        todo = await self.todo_repository.update_todo(todo_id, todo_data)
        return todo if todo else None

    async def delete_todo(self, todo_id: int) -> bool:
        return await self.todo_repository.delete_todo(todo_id)
    
    async def add_todo_item(self, todo_id: int, item_data: TodoItemsAddRequest) -> Optional[TodoItemModel]:
        item = await self.todo_repository.add_todo_item(todo_id, item_data)
        return item if item else None

    async def get_todo_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> List[TodoItemModel]:
        items = await self.todo_repository.get_todo_items(todo_id, skip, limit)
        return items

    async def update_todo_item(self, todo_id: int, item_id: int, item_data: TodoItemUpdateRequest) -> Optional[TodoItemModel]:
        item = await self.todo_repository.update_todo_item(todo_id, item_id, item_data)
        return item if item else None

    async def delete_todo_item(self, todo_id: int, item_id: int) -> bool:
        return await self.todo_repository.delete_todo_item(todo_id, item_id)
    