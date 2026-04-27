import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base

class SchemaVersion(Base):
    __tablename__ = "schema_versions"
    __table_args__ = {"schema": "dbgit_meta"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    database_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("dbgit_meta.tracked_databases.id"))
    commit_hash: Mapped[str | None] = mapped_column(String(64), ForeignKey("dbgit_meta.commits.hash"))
    table_name: Mapped[str] = mapped_column(Text, nullable=False)
    schema_ddl: Mapped[str] = mapped_column(Text, nullable=False)
    schema_hash: Mapped[str | None] = mapped_column(String(64))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
