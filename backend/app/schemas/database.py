from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class DatabaseCreate(BaseModel):
    name: str = Field(..., description="Name of the tracked database")
    connection_url: str = Field(..., description="PostgreSQL connection string")
    config: dict = Field(default_factory=dict, description="Additional configuration")

class DatabaseResponse(DatabaseCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
