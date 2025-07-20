from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.todo_model import TodoModel, TodoItemModel
from app.schemas.todo_schema import TodoCreateRequest, TodoUpdateRequest, TodoItemsAddRequest, TodoItemUpdateRequest

class TodoRepositoryInterface(ABC):
    
    @abstractmethod
    async def create_todo(self, todo_data: TodoCreateRequest) -> TodoModel:
        pass
    
    @abstractmethod
    async def get_todo_by_id(self, todo_id: int) -> Optional[TodoModel]:
        pass
    
    @abstractmethod
    async def get_all_todos(self, skip: int = 0, limit: int = 100) -> List[TodoModel]:
        pass
    
    @abstractmethod
    async def update_todo(self, todo_id: int, todo_data: TodoUpdateRequest) -> Optional[TodoModel]:
        pass
    
    @abstractmethod
    async def delete_todo(self, todo_id: int) -> bool:
        pass
    
    @abstractmethod
    async def add_todo_item(self, todo_id: int, item_data: TodoItemsAddRequest) -> Optional[TodoItemModel]:
        pass
    
    @abstractmethod
    async def get_todo_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> List[TodoItemModel]:
        pass
    
    @abstractmethod
    async def update_todo_item(self, todo_id: int, item_id: int, item_data: TodoItemUpdateRequest) -> Optional[TodoItemModel]:
        pass
    
    @abstractmethod
    async def delete_todo_item(self, todo_id: int, item_id: int) -> bool:
        pass
