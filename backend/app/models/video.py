from sqlalchemy import String, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid
from uuid import UUID
from typing import Optional, TYPE_CHECKING

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Video metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # AI-generated caption (can be long)

    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # Server file path
    video_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # Public URL to access video
    thumbnail_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # Optional thumbnail

    # Video properties
    duration: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # Format: "5:32"
    file_size: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True
    )  # Size in bytes
    format: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # mp4, webm, ogg

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship with user
    user: Mapped["User"] = relationship("User", back_populates="videos")

    def __repr__(self):
        return f"<Video(id={self.id}, title={self.title}, user_id={self.user_id})>"
