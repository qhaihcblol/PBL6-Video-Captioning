"""
File Handler Utility - Video Upload and Management

Handles file validation, storage, and metadata extraction for video uploads.
"""

import os
import uuid
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException, status

from app.config import settings


class FileHandler:
    """Utility class for handling file uploads and storage."""

    # Allowed MIME types for video files
    ALLOWED_MIME_TYPES = [
        "video/mp4",
        "video/webm",
        "video/ogg",
        "video/quicktime",  # .mov files
        "video/x-msvideo",  # .avi files
    ]

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Validate uploaded file for size, extension, and MIME type.

        Args:
            file: FastAPI UploadFile object

        Raises:
            HTTPException: If file validation fails
        """
        # Check if file exists
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided",
            )

        # Check if filename exists
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # Check file extension
        file_ext = FileHandler._get_file_extension(file.filename)
        if file_ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{file_ext}' not allowed. Allowed: {', '.join(settings.allowed_extensions_list)}",
            )

        # Check MIME type
        if file.content_type not in FileHandler.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.content_type}. Expected video file.",
            )

        # Note: File size will be checked during save operation
        print(f"[FileHandler] File validation passed: {file.filename}")

    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Generate a unique filename using UUID while preserving extension.

        Args:
            original_filename: Original filename from upload

        Returns:
            Unique filename (e.g., "a1b2c3d4-e5f6.mp4")
        """
        file_ext = FileHandler._get_file_extension(original_filename)
        unique_name = f"{uuid.uuid4()}.{file_ext}"
        return unique_name

    @staticmethod
    async def save_file(
        file: UploadFile, subdirectory: str = "videos"
    ) -> Tuple[str, str, int]:
        """
        Save uploaded file to disk.

        Args:
            file: FastAPI UploadFile object
            subdirectory: Subdirectory within UPLOAD_DIR (default: "videos")

        Returns:
            Tuple of (file_path, video_url, file_size)
            - file_path: Relative path to file (e.g., "./uploads/videos/xxx.mp4")
            - video_url: Public URL path (e.g., "/uploads/videos/xxx.mp4")
            - file_size: File size in bytes

        Raises:
            HTTPException: If file save fails or exceeds size limit
        """
        # Create upload directory if not exists
        upload_dir = Path(settings.UPLOAD_DIR) / subdirectory
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Validate filename exists
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        # Generate unique filename
        unique_filename = FileHandler.generate_unique_filename(file.filename)
        file_path = upload_dir / unique_filename

        # Save file with size validation
        file_size = 0
        try:
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(8192):  # Read 8KB chunks
                    file_size += len(chunk)

                    # Check file size limit
                    if file_size > settings.MAX_FILE_SIZE:
                        # Clean up partial file (with block will auto-close)
                        buffer.flush()
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB",
                        )

                    buffer.write(chunk)

            print(f"[FileHandler] File saved: {file_path} ({file_size} bytes)")

        except HTTPException as e:
            # Clean up partial file if it exists
            if file_path.exists():
                os.remove(file_path)
            raise
        except Exception as e:
            # Clean up if save failed
            if file_path.exists():
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}",
            )

        # Generate public URL (for frontend access)
        video_url = f"/uploads/{subdirectory}/{unique_filename}"

        # Return relative path for database storage
        relative_path = str(file_path)

        return relative_path, video_url, file_size

    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from disk.

        Args:
            file_path: Path to file to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[FileHandler] File deleted: {file_path}")
                return True
            else:
                print(f"[FileHandler] File not found: {file_path}")
                return False
        except Exception as e:
            print(f"[FileHandler] Failed to delete file: {e}")
            return False

    @staticmethod
    def extract_video_metadata(file_path: str) -> dict:
        """
        Extract metadata from video file.

        Args:
            file_path: Path to video file

        Returns:
            Dictionary with metadata:
            - duration: Video duration string (e.g., "5:32")
            - format: Video format (e.g., "mp4")
            - width: Video width in pixels (optional)
            - height: Video height in pixels (optional)

        Note:
            Current implementation returns mock data.
            TODO: Implement real metadata extraction using ffprobe or moviepy
        """
        # Mock implementation for now
        file_ext = FileHandler._get_file_extension(file_path)

        metadata = {
            "duration": "0:00",  # Mock: Would use ffprobe to get real duration
            "format": file_ext,
            "width": None,  # Mock: Would extract from video
            "height": None,  # Mock: Would extract from video
        }

        print(f"[FileHandler] MOCK metadata extraction for: {file_path}")
        return metadata

    @staticmethod
    def _get_file_extension(filename: str) -> str:
        """
        Extract file extension from filename.

        Args:
            filename: File name (e.g., "video.mp4")

        Returns:
            Extension without dot (e.g., "mp4")
        """
        if not filename:
            return ""
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


# Convenience functions for direct use


async def save_uploaded_video(file: UploadFile) -> Tuple[str, str, int]:
    """
    Validate and save uploaded video file.

    Args:
        file: FastAPI UploadFile object

    Returns:
        Tuple of (file_path, video_url, file_size)
    """
    FileHandler.validate_file(file)
    return await FileHandler.save_file(file, subdirectory="videos")


def delete_video_file(file_path: str) -> bool:
    """
    Delete video file from disk.

    Args:
        file_path: Path to video file

    Returns:
        True if deleted successfully
    """
    return FileHandler.delete_file(file_path)


def get_video_metadata(file_path: str) -> dict:
    """
    Get video file metadata.

    Args:
        file_path: Path to video file

    Returns:
        Dictionary with video metadata
    """
    return FileHandler.extract_video_metadata(file_path)
