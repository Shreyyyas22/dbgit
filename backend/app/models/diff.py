import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from ..database import Base

class Diff(Base):
    __tablename__ = "diffs"
    __table_args__ = {"schema": "dbgit_meta"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_commit_hash: Mapped[str | None] = mapped_column(String(64))
    to_commit_hash: Mapped[str | None] = mapped_column(String(64))
    table_name: Mapped[str | None] = mapped_column(Text)
    diff_type: Mapped[str | None] = mapped_column(String(20))
    diff_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    row_count_added: Mapped[int] = mapped_column(Integer, default=0)
    row_count_removed: Mapped[int] = mapped_column(Integer, default=0)
    row_count_modified: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
