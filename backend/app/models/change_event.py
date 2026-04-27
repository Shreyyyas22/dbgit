import uuid
from sqlalchemy import String, Text, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from ..database import Base

class ChangeEvent(Base):
    __tablename__ = "change_events"
    __table_args__ = {"schema": "dbgit_meta"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commit_hash: Mapped[str | None] = mapped_column(String(64), ForeignKey("dbgit_meta.commits.hash"))
    operation: Mapped[str] = mapped_column(String(10), nullable=False)
    table_name: Mapped[str] = mapped_column(Text, nullable=False)
    schema_name: Mapped[str] = mapped_column(Text, nullable=False, default='public')
    row_pk: Mapped[dict] = mapped_column(JSONB, nullable=False)
    before_state: Mapped[dict | None] = mapped_column(JSONB)
    after_state: Mapped[dict | None] = mapped_column(JSONB)
    changed_columns: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    sequence_num: Mapped[int] = mapped_column(BigInteger, nullable=False)
    lsn: Mapped[str | None] = mapped_column(String)  # PG_LSN represented as string here
