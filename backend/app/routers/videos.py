"""
Video Router - HTTP API Endpoints for Video Management

Handles video upload, history, retrieval, and deletion endpoints.
All endpoints require authentication via JWT token.
"""

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query, Path, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.services.video_service import VideoService
from app.schemas.video import VideoUploadResponse, VideoHistoryResponse, VideoResponse


router = APIRouter()


@router.post(
    "/upload",
    response_model=VideoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload video and generate caption",
)
async def upload_video(
    file: UploadFile = File(..., description="Video file to upload (mp4, webm, ogg)"),
    title: str = Form(
        ..., min_length=1, max_length=500, description="Title for the video"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a video file and automatically generate an AI caption.

    **Process:**
    1. Validates file (size, type, extension)
    2. Saves video to server storage
    3. Generates AI caption from video content
    4. Extracts video metadata (duration, format, size)
    5. Saves all information to database

    **Required:**
    - `file`: Video file (multipart/form-data)
    - `title`: Video title (1-500 characters)
    - Authentication: Bearer token in Authorization header

    **Returns:**
    - Video information with AI-generated caption
    - Video URL for playback
    - Upload timestamp

    **Error codes:**
    - `400`: Invalid file (wrong type, extension)
    - `401`: Not authenticated
    - `413`: File too large (> 500MB)
    - `500`: Upload or caption generation failed

    **Example Request:**
    ```
    POST /api/videos/upload
    Authorization: Bearer <token>
    Content-Type: multipart/form-data

    file: <video-file>
    title: "My Accessibility Tutorial"
    ```
    """
    return await VideoService.upload_video(
        db=db,
        file=file,
        user_id=current_user.id,
        title=title,
    )


@router.get(
    "/history",
    response_model=VideoHistoryResponse,
    summary="Get user's video history",
)
async def get_video_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(50, ge=1, le=100, description="Items per page (max 100)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get paginated list of user's uploaded videos.

    **Query Parameters:**
    - `page`: Page number (default: 1, min: 1)
    - `limit`: Items per page (default: 50, min: 1, max: 100)

    **Returns:**
    - List of videos (newest first)
    - Total count
    - Pagination info

    **Authentication:** Required (Bearer token)

    **Error codes:**
    - `400`: Invalid pagination parameters
    - `401`: Not authenticated

    **Example:**
    ```
    GET /api/videos/history?page=1&limit=20
    Authorization: Bearer <token>
    ```

    **Response:**
    ```json
    {
      "videos": [...],
      "total": 42,
      "page": 1,
      "limit": 20
    }
    ```
    """
    return VideoService.get_user_videos(
        db=db,
        user_id=current_user.id,
        page=page,
        limit=limit,
    )


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
    summary="Get specific video by ID",
)
async def get_video(
    video_id: UUID = Path(..., description="Video UUID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a specific video by its ID.

    **Path Parameters:**
    - `video_id`: UUID of the video

    **Returns:**
    - Complete video information including caption and metadata

    **Authentication:** Required (Bearer token)

    **Ownership:** Only the video owner can access it

    **Error codes:**
    - `401`: Not authenticated
    - `403`: Not the video owner
    - `404`: Video not found

    **Example:**
    ```
    GET /api/videos/a1b2c3d4-e5f6-7890-abcd-ef1234567890
    Authorization: Bearer <token>
    ```
    """
    return VideoService.get_video_by_id(
        db=db,
        video_id=video_id,
        user_id=current_user.id,
    )


@router.delete(
    "/{video_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a video",
)
async def delete_video(
    video_id: UUID = Path(..., description="Video UUID to delete"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a video (both file and database record).

    **Process:**
    1. Verifies video ownership
    2. Deletes video file from storage
    3. Deletes database record

    **Path Parameters:**
    - `video_id`: UUID of video to delete

    **Returns:**
    - Success message with deleted video ID

    **Authentication:** Required (Bearer token)

    **Ownership:** Only the video owner can delete it

    **Error codes:**
    - `401`: Not authenticated
    - `403`: Not the video owner
    - `404`: Video not found
    - `500`: Deletion failed

    **Example:**
    ```
    DELETE /api/videos/a1b2c3d4-e5f6-7890-abcd-ef1234567890
    Authorization: Bearer <token>
    ```

    **Response:**
    ```json
    {
      "message": "Video deleted successfully",
      "video_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    }
    ```
    """
    return VideoService.delete_video(
        db=db,
        video_id=video_id,
        user_id=current_user.id,
    )


@router.delete(
    "/history/clear",
    status_code=status.HTTP_200_OK,
    summary="Clear all video history",
)
async def clear_video_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete all videos for the current user.

    **Process:**
    1. Retrieves all user's videos
    2. Deletes all video files from storage
    3. Deletes all database records

    **⚠️ Warning:** This action cannot be undone!

    **Returns:**
    - Success message with count of deleted videos

    **Authentication:** Required (Bearer token)

    **Error codes:**
    - `401`: Not authenticated
    - `500`: Deletion failed

    **Example:**
    ```
    DELETE /api/videos/history/clear
    Authorization: Bearer <token>
    ```

    **Response:**
    ```json
    {
      "message": "Video history cleared successfully",
      "deleted_count": 15
    }
    ```
    """
    return VideoService.clear_user_history(
        db=db,
        user_id=current_user.id,
    )
