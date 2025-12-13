"""
Video Service - Business Logic for Video Management

Handles video upload, caption generation, history management, and deletion.
Orchestrates file_handler, caption_service, and database operations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.video import Video
from app.schemas.video import VideoUploadResponse, VideoHistoryResponse, VideoResponse
from app.services.caption_service import get_caption_service
from app.utils.file_handler import (
    save_uploaded_video,
    delete_video_file,
    get_video_metadata,
)


class VideoService:
    """Service layer for video operations."""

    @staticmethod
    async def upload_video(
        db: Session,
        file: UploadFile,
        user_id: UUID,
        title: str,
    ) -> VideoUploadResponse:
        """
        Upload video, generate caption, and save to database.

        This method orchestrates the entire upload workflow:
        1. Save video file to disk
        2. Generate AI caption
        3. Extract video metadata
        4. Create database record
        5. Return response with all information

        Args:
            db: Database session
            file: Uploaded video file
            user_id: ID of user uploading the video
            title: Title for the video

        Returns:
            VideoUploadResponse with video data and caption

        Raises:
            HTTPException: If upload, caption generation, or database operation fails
        """
        file_path = None
        try:
            # Step 1: Save video file to disk
            print(f"[VideoService] Starting upload for user {user_id}: {title}")
            file_path, video_url, file_size = await save_uploaded_video(file)
            print(f"[VideoService] File saved: {file_path}")

            # Step 2: Generate AI caption from video
            caption_service = get_caption_service()
            caption = caption_service.generate_caption(file_path)
            print(f"[VideoService] Caption generated: {caption[:50]}...")

            # Step 3: Extract video metadata
            metadata = get_video_metadata(file_path)
            video_format = metadata.get("format", "mp4")
            duration = metadata.get("duration", "0:00")

            # Step 4: Create database record
            video = Video(
                user_id=user_id,
                title=title,
                caption=caption,
                original_filename=file.filename or "unknown.mp4",
                file_path=file_path,
                video_url=video_url,
                thumbnail_url=None,  # TODO: Implement thumbnail generation
                duration=duration,
                file_size=file_size,
                format=video_format,
            )

            db.add(video)
            db.commit()
            db.refresh(video)

            print(f"[VideoService] Video saved to database: {video.id}")

            # Step 5: Return response
            return VideoUploadResponse.from_video(video)

        except HTTPException:
            # Re-raise HTTP exceptions (from file_handler)
            # Cleanup file if database operation failed
            if file_path:
                delete_video_file(file_path)
            db.rollback()
            raise

        except Exception as e:
            # Cleanup on unexpected errors
            if file_path:
                delete_video_file(file_path)
            db.rollback()
            print(f"[VideoService] Upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Video upload failed: {str(e)}",
            )

    @staticmethod
    def get_user_videos(
        db: Session,
        user_id: UUID,
        page: int = 1,
        limit: int = 50,
    ) -> VideoHistoryResponse:
        """
        Get paginated list of user's videos.

        Args:
            db: Database session
            user_id: User ID to fetch videos for
            page: Page number (1-indexed)
            limit: Number of items per page (max 100)

        Returns:
            VideoHistoryResponse with videos and pagination info

        Raises:
            HTTPException: If invalid pagination parameters
        """
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be >= 1",
            )

        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100",
            )

        # Calculate offset
        offset = (page - 1) * limit

        # Query videos with pagination
        query = db.query(Video).filter(Video.user_id == user_id)
        total = query.count()

        videos = (
            query.order_by(desc(Video.created_at)).offset(offset).limit(limit).all()
        )

        print(
            f"[VideoService] Retrieved {len(videos)} videos for user {user_id} (page {page})"
        )

        return VideoHistoryResponse(
            videos=[VideoResponse.from_orm(video) for video in videos],
            total=total,
            page=page,
            limit=limit,
        )

    @staticmethod
    def get_video_by_id(
        db: Session,
        video_id: UUID,
        user_id: UUID,
    ) -> VideoResponse:
        """
        Get a specific video by ID.

        Args:
            db: Database session
            video_id: Video ID to retrieve
            user_id: User ID for ownership verification

        Returns:
            VideoResponse with video data

        Raises:
            HTTPException: If video not found or user doesn't own it
        """
        video = db.query(Video).filter(Video.id == video_id).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video not found: {video_id}",
            )

        # Verify ownership
        if video.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this video",
            )

        return VideoResponse.from_orm(video)

    @staticmethod
    def delete_video(
        db: Session,
        video_id: UUID,
        user_id: UUID,
    ) -> dict:
        """
        Delete a video (both file and database record).

        Args:
            db: Database session
            video_id: Video ID to delete
            user_id: User ID for ownership verification

        Returns:
            Dictionary with success message

        Raises:
            HTTPException: If video not found or user doesn't own it
        """
        video = db.query(Video).filter(Video.id == video_id).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video not found: {video_id}",
            )

        # Verify ownership
        if video.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this video",
            )

        # Delete file from disk
        file_deleted = delete_video_file(video.file_path)
        if not file_deleted:
            print(f"[VideoService] Warning: File not found on disk: {video.file_path}")

        # Delete from database
        db.delete(video)
        db.commit()

        print(f"[VideoService] Video deleted: {video_id}")

        return {
            "message": "Video deleted successfully",
            "video_id": str(video_id),
        }

    @staticmethod
    def clear_user_history(
        db: Session,
        user_id: UUID,
    ) -> dict:
        """
        Delete all videos for a user.

        Args:
            db: Database session
            user_id: User ID whose videos should be deleted

        Returns:
            Dictionary with success message and count

        Raises:
            HTTPException: If database operation fails
        """
        try:
            # Get all user videos
            videos = db.query(Video).filter(Video.user_id == user_id).all()

            if not videos:
                return {
                    "message": "No videos to delete",
                    "deleted_count": 0,
                }

            # Delete all files from disk
            deleted_count = 0
            for video in videos:
                if delete_video_file(video.file_path):
                    deleted_count += 1
                else:
                    print(f"[VideoService] Warning: File not found: {video.file_path}")

            # Delete all from database
            db.query(Video).filter(Video.user_id == user_id).delete()
            db.commit()

            print(f"[VideoService] Cleared {len(videos)} videos for user {user_id}")

            return {
                "message": "Video history cleared successfully",
                "deleted_count": len(videos),
            }

        except Exception as e:
            db.rollback()
            print(f"[VideoService] Failed to clear history: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to clear video history: {str(e)}",
            )


# Convenience functions for direct use


async def upload_user_video(
    db: Session,
    file: UploadFile,
    user_id: UUID,
    title: str,
) -> VideoUploadResponse:
    """
    Upload a video for a user.

    Args:
        db: Database session
        file: Video file to upload
        user_id: User uploading the video
        title: Video title

    Returns:
        VideoUploadResponse with upload results
    """
    return await VideoService.upload_video(db, file, user_id, title)


def get_user_video_history(
    db: Session,
    user_id: UUID,
    page: int = 1,
    limit: int = 50,
) -> VideoHistoryResponse:
    """
    Get user's video history with pagination.

    Args:
        db: Database session
        user_id: User ID
        page: Page number
        limit: Items per page

    Returns:
        VideoHistoryResponse with videos and pagination
    """
    return VideoService.get_user_videos(db, user_id, page, limit)
