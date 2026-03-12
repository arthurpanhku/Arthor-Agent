from datetime import datetime

from sqlmodel import Field, SQLModel


class AuditLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str | None = Field(default=None, index=True)  # ID or username
    action: str = Field(index=True)
    resource: str = Field(index=True)
    details: str | None = None
    ip_address: str | None = None
