import uuid
from datetime import datetime
from sqlalchemy import String, Text, JSON, DateTime, ForeignKey, Boolean, Integer, ARRAY, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY as PG_ARRAY
from ..database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "dbgit_meta"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "dbgit_meta"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

class UserDatabaseRole(Base):
    __tablename__ = "user_database_roles"
    __table_args__ = {"schema": "dbgit_meta"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("dbgit_meta.users.id"), primary_key=True)
    database_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("dbgit_meta.tracked_databases.id"), primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("dbgit_meta.roles.id"), primary_key=True)
