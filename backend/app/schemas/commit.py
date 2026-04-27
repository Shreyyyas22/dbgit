from pydantic import BaseModel, Field
from typing import Any
from uuid import UUID
from datetime import datetime

class ChangeEventCreate(BaseModel):
    operation: str = Field(..., description="INSERT, UPDATE, or DELETE")
    table_name: str
    schema_name: str = "public"
    row_pk: dict[str, Any]
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    changed_columns: list[str] | None = None

class CommitCreate(BaseModel):
    branch_id: UUID
    author_id: UUID | None = None
    message: str
    change_events: list[ChangeEventCreate]

class CommitResponse(BaseModel):
    id: UUID
    hash: str
    parent_hash: str | None
    branch_id: UUID | None
    database_id: UUID | None
    author_id: UUID | None
    message: str
    committed_at: datetime
    tables_affected: list[str]
    stats: dict[str, Any]

    class Config:
        from_attributes = True
