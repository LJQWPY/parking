import request from './request'

export interface Recording {
  id: number
  camera_id: number
  camera_name?: string
  file_path: string
  start_time: string
  end_time?: string
  duration?: number
  file_size?: number
  status: string
  created_at: string
}

export const recordingApi = {
  list: (params?: {
    camera_id?: number
    start_date?: string
    end_date?: string
    status?: string
    skip?: number
    limit?: number
  }) => {
    return request.get('/recordings', { params })
  },

  get: (id: number) => {
    return request.get(`/recordings/${id}`)
  },

  create: (data: Partial<Recording>) => {
    return request.post('/recordings', data)
  },

  update: (id: number, data: Partial<Recording>) => {
    return request.put(`/recordings/${id}`, data)
  },

  delete: (id: number) => {
    return request.delete(`/recordings/${id}`)
  },

  getByCamera: (cameraId: number, date?: string) => {
    return request.get(`/recordings/cameras/${cameraId}/recordings`, {
      params: date ? { date } : {}
    })
  }
}
