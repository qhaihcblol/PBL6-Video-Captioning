// API Response Types matching backend schemas

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface UserWithToken extends User {
  token: string;
  message: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface VideoResponse {
  id: string;
  title: string;
  caption: string;
  video_url?: string;
  thumbnail_url?: string;
  duration?: string;
  file_size?: number;
  format?: string;
  created_at: string;
  timestamp?: string; // ISO format for frontend compatibility
}

export interface VideoHistoryResponse {
  videos: VideoResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface SampleVideo {
  id: string;
  title: string;
  description?: string;
  caption: string;
  video_url: string;
  thumbnail_url?: string;
  duration?: string;
  display_order: number;
  is_active: boolean;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}
