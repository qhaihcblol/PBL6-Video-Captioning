from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==================== Video Schemas ====================


class VideoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)


class VideoCreate(VideoBase):
    """Schema for creating a video (will be populated after upload)"""

    pass


class VideoResponse(VideoBase):
    id: UUID
    caption: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VideoUploadResponse(VideoResponse):
    """Response after successful upload with caption"""

    timestamp: str  # ISO format string for frontend compatibility

    @classmethod
    def from_video(cls, video):
        return cls(
            id=video.id,
            title=video.title,
            caption=video.caption,
            video_url=video.video_url,
            thumbnail_url=video.thumbnail_url,
            duration=video.duration,
            file_size=video.file_size,
            format=video.format,
            created_at=video.created_at,
            timestamp=video.created_at.isoformat(),
        )


class VideoHistoryResponse(BaseModel):
    videos: List[VideoResponse]
    total: int
    page: int
    limit: int


# ==================== Sample Video Schemas ====================


class SampleVideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    caption: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration: Optional[str] = None


class SampleVideoResponse(SampleVideoBase):
    id: UUID
    display_order: int
    is_active: bool

    class Config:
        from_attributes = True


class SampleVideosResponse(BaseModel):
    samples: List[SampleVideoResponse]
