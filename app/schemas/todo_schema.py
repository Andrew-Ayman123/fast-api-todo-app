from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TodoCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    
class TodoItemsAddRequest(BaseModel):
    title: str
    description: Optional[str] = None
    
class TodoItemUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    
    
class TodoItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    todo_items: Optional[List[TodoItemResponse]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
   
