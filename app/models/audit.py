from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(index=True) # ID or username
    action: str = Field(index=True)
    resource: str = Field(index=True)
    details: Optional[str] = None
    ip_address: Optional[str] = None
