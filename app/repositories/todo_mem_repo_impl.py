from typing import List, Optional
from app.models.todo_model import TodoModel, TodoItemModel
from app.schemas.todo_schema import TodoCreateRequest, TodoUpdateRequest, TodoItemsAddRequest, TodoItemUpdateRequest
from app.repositories.todo_repository import TodoRepositoryInterface
from datetime import datetime

class TodoMemoryRepository(TodoRepositoryInterface):

    def __init__(self):
        self.todos: List[TodoModel] = []
        self._next_todo_id = 1
        self._next_item_id = 1
    
    async def create_todo(self, todo_data: TodoCreateRequest) -> TodoModel:
        todo = TodoModel(
            id=self._next_todo_id,
            title=todo_data.title,
            description=todo_data.description,
            todo_items=[]
        )
        self.todos.append(todo)
        self._next_todo_id += 1
        return todo

    async def get_todo_by_id(self, todo_id: int) -> Optional[TodoModel]:
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None
    
    async def get_all_todos(self, skip: int = 0, limit: int = 100) -> List[TodoModel]:
        return self.todos[skip:skip + limit]
    
    async def update_todo(self, todo_id: int, todo_data: TodoUpdateRequest) -> Optional[TodoModel]:
        todo = await self.get_todo_by_id(todo_id)
        if not todo:
            return None
        
        if todo_data.title is not None:
            todo.title = todo_data.title
        if todo_data.description is not None:
            todo.description = todo_data.description
        
        return todo
    
    async def delete_todo(self, todo_id: int) -> bool:
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                return True
        return False
    
    async def add_todo_item(self, todo_id: int, item_data: TodoItemsAddRequest) -> Optional[TodoItemModel]:
        todo = await self.get_todo_by_id(todo_id)
        if not todo:
            return None
        
        item = TodoItemModel(
            id=self._next_item_id,
            title=item_data.title,
            description=item_data.description,
            completed=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        todo.todo_items.append(item)
        self._next_item_id += 1
        return item
    
    async def get_todo_items(self, todo_id: int, skip: int = 0, limit: int = 100) -> List[TodoItemModel]:
        todo = await self.get_todo_by_id(todo_id)
        if not todo:
            return []
        return todo.todo_items[skip:skip + limit]
    
    async def update_todo_item(self, todo_id: int, item_id: int, item_data: TodoItemUpdateRequest) -> Optional[TodoItemModel]:
        todo = await self.get_todo_by_id(todo_id)
        if not todo:
            return None
        
        for item in todo.todo_items:
            if item.id == item_id:
                if item_data.title is not None:
                    item.title = item_data.title
                if item_data.description is not None:
                    item.description = item_data.description
                if item_data.completed is not None:
                    item.completed = item_data.completed
                item.updated_at = datetime.now()
                return item
        return None
    
    async def delete_todo_item(self, todo_id: int, item_id: int) -> bool:
        todo = await self.get_todo_by_id(todo_id)
        if not todo:
            return False
        
        for i, item in enumerate(todo.todo_items):
            if item.id == item_id:
                del todo.todo_items[i]
                return True
        return False
