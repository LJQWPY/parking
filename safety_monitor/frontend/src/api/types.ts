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
  location: string
  status: 'online' | 'offline' | 'error'
  streamUrl?: string
  lastHeartbeat?: string
}

// 告警类型
export interface Alert {
  id: number
  cameraId: number
  cameraName: string
  type: 'fire' | 'smoke' | 'intrusion' | 'temperature' | 'humidity'
  level: 'low' | 'medium' | 'high' | 'critical'
  message: string
  status: 'pending' | 'processing' | 'resolved'
  createdAt: string
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
