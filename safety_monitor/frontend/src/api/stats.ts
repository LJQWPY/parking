import request from './request'

export const statsApi = {
  getOverview: () => {
    return request.get('/stats/overview')
  },
  
  getDistribution: () => {
    return request.get('/stats/distribution')
  },
  
  getDetections: (days: number = 30) => {
    return request.get('/stats/detections', { params: { days } })
  },
  
  getCompliance: () => {
    return request.get('/stats/compliance')
  },
  
  getTimeSeries: (metric: string, days: number = 7) => {
    return request.get('/stats/time-series', { params: { metric, days } })
  },
  
  getSummary: () => {
    return request.get('/stats/summary')
  }
}