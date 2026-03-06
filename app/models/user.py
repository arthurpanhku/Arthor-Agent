from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None, index=True)
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    role: str = Field(default="user") # 'admin', 'auditor', 'user'

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
