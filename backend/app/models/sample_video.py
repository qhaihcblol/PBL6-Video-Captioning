from sqlalchemy import String, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import uuid
from uuid import UUID
from typing import Optional

from app.database import Base


class SampleVideo(Base):
    __tablename__ = "sample_videos"

    id: Mapped[UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    # Video information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    caption: Mapped[str] = mapped_column(Text, nullable=False)

    # URLs
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Properties
    duration: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )  # Format: "5:32"

    # Display settings
    display_order: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<SampleVideo(id={self.id}, title={self.title}, order={self.display_order})>"
