import { useState } from 'react'
import { Table, Tag, Button, Space, Select, Card } from 'antd'
import { CheckOutlined, CloseOutlined } from '@ant-design/icons'
import type { Alert } from '../../api/types'

const { Option } = Select

const AlertPage = () => {
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)
  
  const levelColorMap: Record<string, string> = {
    low: 'blue',
    medium: 'orange',
    high: 'red',
    critical: 'red'
  }
  
  const levelTextMap: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重'
  }
  
  const statusColorMap: Record<string, string> = {
    pending: 'orange',
    processing: 'blue',
    resolved: 'green'
  }
  
  const statusTextMap: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决'
  }
  
  const typeTextMap: Record<string, string> = {
    fire: '火灾',
    smoke: '烟雾',
    intrusion: '入侵',
    temperature: '温度异常',
    humidity: '湿度异常'
  }
  
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '摄像头',
      dataIndex: 'cameraName',
      key: 'cameraName'
    },
    {
      title: '告警类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => typeTextMap[type] || type
    },
    {
      title: '告警级别',
      dataIndex: 'level',
      key: 'level',
      render: (level: string) => (
        <Tag color={levelColorMap[level]}>{levelTextMap[level]}</Tag>
      )
    },
    {
      title: '消息',
      dataIndex: 'message',
      key: 'message'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={statusColorMap[status]}>{statusTextMap[status]}</Tag>
      )
    },
    {
      title: '时间',
      dataIndex: 'createdAt',
      key: 'createdAt'
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Alert) => (
        <Space>
          {record.status === 'pending' && (
            <Button 
              type="link" 
              icon={<CheckOutlined />}
              size="small"
            >
              处理
            </Button>
          )}
          {record.status !== 'resolved' && (
            <Button 
              type="link" 
              icon={<CloseOutlined />}
              size="small"
            >
              关闭
            </Button>
          )}
        </Space>
      )
    }
  ]
  
  // 模拟数据
  const mockData: Alert[] = [
    { id: 1, cameraId: 1, cameraName: '1号车间摄像头', type: 'fire', level: 'critical', message: '检测到明火', status: 'pending', createdAt: '2024-01-15 10:30:00' },
    { id: 2, cameraId: 2, cameraName: '2号车间摄像头', type: 'smoke', level: 'high', message: '检测到烟雾', status: 'processing', createdAt: '2024-01-15 10:25:00' },
    { id: 3, cameraId: 3, cameraName: '仓库摄像头', type: 'intrusion', level: 'medium', message: '检测到人员入侵', status: 'resolved', createdAt: '2024-01-15 09:00:00', resolvedAt: '2024-01-15 09:30:00' },
    { id: 4, cameraId: 4, cameraName: '大门摄像头', type: 'temperature', level: 'low', message: '温度偏高', status: 'pending', createdAt: '2024-01-15 08:00:00' },
  ]
  
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>告警管理</h1>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <span>状态筛选:</span>
            <Select 
              placeholder="选择状态" 
              allowClear
              style={{ width: 150 }}
              onChange={(value) => setStatusFilter(value)}
            >
              <Option value="pending">待处理</Option>
              <Option value="processing">处理中</Option>
              <Option value="resolved">已解决</Option>
            </Select>
          </Space>
        </div>
        <Table
          columns={columns}
          dataSource={mockData.filter(item => !statusFilter || item.status === statusFilter)}
          rowKey="id"
        />
      </Card>
    </div>
  )
}

export default AlertPage
