import uuid
import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Resume(Base):
    """
    CareerOS Infinity parsed Resume database model.
    Supports document versioning, pgvector search embeddings, and raw text storage.
    """
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False
    )
    raw_text: Mapped[str] = mapped_column(
        String,
        nullable=False
    )
    resume_json: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False
    )
    embedding: Mapped[list] = mapped_column(
        Vector(1536),
        nullable=True
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False
    )
