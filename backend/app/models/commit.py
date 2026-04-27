import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from ..database import Base

class Commit(Base):
    __tablename__ = "commits"
    __table_args__ = {"schema": "dbgit_meta"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    parent_hash: Mapped[str | None] = mapped_column(String(64), ForeignKey("dbgit_meta.commits.hash"))
    branch_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("dbgit_meta.branches.id"))
    database_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("dbgit_meta.tracked_databases.id"))
    author_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("dbgit_meta.users.id"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    tables_affected: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    stats: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_merge_commit: Mapped[bool] = mapped_column(Boolean, default=False)
    merge_source_hash: Mapped[str | None] = mapped_column(String(64))
