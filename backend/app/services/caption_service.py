"""
Caption Service - AI Caption Generation for Videos

Currently using MOCK implementation for testing.
TODO: Replace with real AI model (Salesforce/blip-image-captioning-large) later.
"""

import random
from typing import Optional
import os


class CaptionService:
    """
    Service for generating captions from videos using AI.

    Current implementation: MOCK (returns random captions)
    Future implementation: Real AI model integration
    """

    # Mock captions pool for testing
    MOCK_CAPTIONS = [
        "A person is explaining web accessibility standards in a well-lit room with clear audio.",
        "The instructor demonstrates ARIA attributes using code examples displayed on screen.",
        "Tutorial showing keyboard navigation techniques for screen readers and assistive technologies.",
        "Video demonstration of WCAG 2.1 compliance testing tools and accessibility evaluation methods.",
        "Speaker discusses the importance of semantic HTML for screen reader compatibility.",
        "Presentation covering color contrast requirements and visual accessibility guidelines.",
        "Developer walking through accessible form design with proper label associations.",
        "Tutorial on implementing skip navigation links and landmark regions for better accessibility.",
        "Demonstration of how to test websites using popular screen reader software like NVDA and JAWS.",
        "Expert explaining the differences between WCAG levels A, AA, and AAA conformance.",
    ]

    def __init__(self):
        """Initialize the caption service."""
        self.model_loaded = False  # Mock flag
        print("[CaptionService] Initialized with MOCK implementation")

    @staticmethod
    def generate_caption(video_path: str) -> str:
        """
        Generate a caption for the given video.

        Args:
            video_path: Path to the video file

        Returns:
            Generated caption text

        Note:
            Current implementation returns random mock captions.
            Real implementation will:
            1. Extract frames from video using OpenCV
            2. Run frames through BLIP model
            3. Return AI-generated caption
        """
        # Verify file exists (basic validation)
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Mock processing delay (simulate AI thinking time)
        # In real implementation, this is where heavy AI processing happens
        print(f"[CaptionService] Generating caption for: {video_path}")

        # Return random caption from pool
        caption = random.choice(CaptionService.MOCK_CAPTIONS)
        print(f"[CaptionService] Generated caption: {caption[:50]}...")

        return caption

    @staticmethod
    def extract_video_frame(
        video_path: str, frame_position: float = 0.5
    ) -> Optional[str]:
        """
        Extract a frame from video for caption generation.

        Args:
            video_path: Path to the video file
            frame_position: Position to extract (0.0 to 1.0, where 0.5 is middle)

        Returns:
            Path to extracted frame image, or None if failed

        Note:
            Mock implementation - returns None.
            Real implementation will use OpenCV to extract frames.
        """
        print(
            f"[CaptionService] MOCK: Would extract frame at position {frame_position}"
        )
        return None

    def load_model(self):
        """
        Load the AI model for caption generation.

        Note:
            Mock implementation - does nothing.
            Real implementation will:
            - Load Salesforce/blip-image-captioning-large model
            - Initialize on CPU/GPU based on config
            - Cache model for subsequent requests
        """
        print("[CaptionService] MOCK: Model 'loaded' (fake)")
        self.model_loaded = True

    def unload_model(self):
        """
        Unload the AI model to free memory.

        Note:
            Mock implementation - does nothing.
            Real implementation will release model from memory.
        """
        print("[CaptionService] MOCK: Model 'unloaded' (fake)")
        self.model_loaded = False


# Singleton instance for reuse
_caption_service_instance: Optional[CaptionService] = None


def get_caption_service() -> CaptionService:
    """
    Get or create the caption service singleton.

    Returns:
        CaptionService instance
    """
    global _caption_service_instance
    if _caption_service_instance is None:
        _caption_service_instance = CaptionService()
    return _caption_service_instance
