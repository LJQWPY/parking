import request from './request'
import type { Alert, PaginationParams, PaginatedResponse } from './types'

export const alertApi = {
  getList: (params: PaginationParams & { status?: string; level?: string }) => {
    return request.get<PaginatedResponse<Alert>>('/alerts', { params })
  },
  
  getById: (id: number) => {
    return request.get<Alert>(`/alerts/${id}`)
  },
  
  updateStatus: (id: number, status: string) => {
    return request.put(`/alerts/${id}/status`, { status })
  },
  
  resolve: (id: number, remark?: string) => {
    return request.put(`/alerts/${id}/resolve`, { remark })
  },
  
  getStatistics: () => {
    return request.get('/alerts/statistics')
  }
}
