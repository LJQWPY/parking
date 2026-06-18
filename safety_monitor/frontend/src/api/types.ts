// 用户类型
export interface User {
  id: number
  username: string
  nickname?: string
  avatar?: string
  role: 'admin' | 'user'
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 登录响应
export interface LoginResponse {
  token: string
  user: User
}

// 摄像头类型
export interface Camera {
  id: number
  name: string
  location?: string
  status?: string
  streamUrl?: string
  lastHeartbeat?: string
  last_updated?: string
  ip_address?: string
  zone_id?: number
  created_at?: string
}

// 告警类型
export interface Alert {
  id: number
  camera_id: number
  zone_id?: number
  alert_type: string
  level: string
  description?: string
  message?: string
  image_url?: string
  video_url?: string
  is_handled: boolean
  handled_by?: string
  handled_at?: string
  created_at: string
  resolvedAt?: string
}

// 通用API响应
export interface ApiResponse<T> {
  code: number
  data: T
  message: string
}

// 分页参数
export interface PaginationParams {
  page: number
  pageSize: number
}

// 分页响应
export interface PaginatedResponse<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

// API响应包装类型
export interface WrappedResponse<T> {
  code: number
  message: string
  data: T
}