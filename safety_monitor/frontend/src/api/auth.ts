import request from './request'
import type { LoginRequest, LoginResponse, User } from './types'

export const authApi = {
  login: (data: LoginRequest) => {
    return request.post<LoginResponse>('/auth/login', data)
  },
  
  logout: () => {
    return request.post('/auth/logout')
  },
  
  getCurrentUser: () => {
    return request.get<User>('/auth/current')
  },
  
  updatePassword: (oldPassword: string, newPassword: string) => {
    return request.post('/auth/password', { oldPassword, newPassword })
  }
}
