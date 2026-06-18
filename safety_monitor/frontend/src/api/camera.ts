import request from './request'
import type { Camera, PaginationParams, PaginatedResponse } from './types'

export const cameraApi = {
  getList: (params: PaginationParams) => {
    return request.get<PaginatedResponse<Camera>>('/cameras', { params })
  },
  
  getById: (id: number) => {
    return request.get<Camera>(`/cameras/${id}`)
  },
  
  create: (data: Partial<Camera>) => {
    return request.post('/cameras', data)
  },
  
  update: (id: number, data: Partial<Camera>) => {
    return request.put(`/cameras/${id}`, data)
  },
  
  delete: (id: number) => {
    return request.delete(`/cameras/${id}`)
  },
  
  getStreamUrl: (id: number) => {
    return request.get<string>(`/cameras/${id}/stream`)
  }
}
