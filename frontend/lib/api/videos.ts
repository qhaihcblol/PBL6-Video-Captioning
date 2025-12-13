import apiClient from "../api-client";
import type { VideoHistoryResponse, VideoResponse } from "../types";

/**
 * Video upload progress callback
 */
export type UploadProgressCallback = (progress: number) => void;

/**
 * Video API functions
 */
export const videosApi = {
  /**
   * Upload a video file and get AI-generated caption
   *
   * @param file - Video file to upload
   * @param title - Title for the video
   * @param onProgress - Optional callback for upload progress (0-100)
   * @returns Promise with video data including AI caption
   */
  uploadVideo: async (
    file: File,
    title: string,
    onProgress?: UploadProgressCallback
  ): Promise<VideoResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("title", title);

    const response = await apiClient.post<VideoResponse>(
      "/api/videos/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(percentCompleted);
          }
        },
      }
    );

    return response.data;
  },

  /**
   * Get user's video history with pagination
   *
   * @param page - Page number (1-indexed, default: 1)
   * @param limit - Items per page (default: 50, max: 100)
   * @returns Promise with paginated video list
   */
  getVideoHistory: async (
    page: number = 1,
    limit: number = 50
  ): Promise<VideoHistoryResponse> => {
    const response = await apiClient.get<VideoHistoryResponse>(
      "/api/videos/history",
      {
        params: { page, limit },
      }
    );

    return response.data;
  },

  /**
   * Get a specific video by ID
   *
   * @param videoId - UUID of the video
   * @returns Promise with video data
   */
  getVideoById: async (videoId: string): Promise<VideoResponse> => {
    const response = await apiClient.get<VideoResponse>(
      `/api/videos/${videoId}`
    );

    return response.data;
  },

  /**
   * Delete a specific video
   *
   * @param videoId - UUID of the video to delete
   * @returns Promise with success message
   */
  deleteVideo: async (
    videoId: string
  ): Promise<{ message: string; video_id: string }> => {
    const response = await apiClient.delete<{
      message: string;
      video_id: string;
    }>(`/api/videos/${videoId}`);

    return response.data;
  },

  /**
   * Clear all video history for current user
   *
   * @returns Promise with success message and deleted count
   */
  clearHistory: async (): Promise<{
    message: string;
    deleted_count: number;
  }> => {
    const response = await apiClient.delete<{
      message: string;
      deleted_count: number;
    }>("/api/videos/history/clear");

    return response.data;
  },
};

/**
 * Convenience functions for common operations
 */

/**
 * Upload video with automatic progress tracking
 */
export const uploadVideoWithProgress = async (
  file: File,
  title: string,
  onProgress: UploadProgressCallback
): Promise<VideoResponse> => {
  return videosApi.uploadVideo(file, title, onProgress);
};

/**
 * Get first page of video history
 */
export const getRecentVideos = async (
  limit: number = 10
): Promise<VideoHistoryResponse> => {
  return videosApi.getVideoHistory(1, limit);
};

/**
 * Delete video and return success status
 */
export const deleteVideoById = async (videoId: string): Promise<boolean> => {
  try {
    await videosApi.deleteVideo(videoId);
    return true;
  } catch (error) {
    console.error("Failed to delete video:", error);
    return false;
  }
};
