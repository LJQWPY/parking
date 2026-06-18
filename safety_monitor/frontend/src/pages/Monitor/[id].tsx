import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Descriptions, Tag, Space } from 'antd'
import { ArrowLeftOutlined, VideoCameraOutlined } from '@ant-design/icons'

const MonitorDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  
  // 模拟数据
  const mockCamera = {
    id: id,
    name: '1号车间摄像头',
    location: 'A区1号车间',
    status: 'online',
    streamUrl: 'rtsp://example.com/stream',
    lastHeartbeat: '2024-01-15 10:30:00',
    resolution: '1920x1080',
    fps: 30
  }
  
  const statusColor = {
    online: 'green',
    offline: 'gray',
    error: 'red'
  }[mockCamera.status] || 'gray'
  
  const statusText = {
    online: '在线',
    offline: '离线',
    error: '异常'
  }[mockCamera.status] || '未知'
  
  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/monitor')}
        >
          返回
        </Button>
      </div>
      <Card title="摄像头详情">
        <Descriptions column={2}>
          <Descriptions.Item label="ID">{mockCamera.id}</Descriptions.Item>
          <Descriptions.Item label="名称">{mockCamera.name}</Descriptions.Item>
          <Descriptions.Item label="位置">{mockCamera.location}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={statusColor}>{statusText}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="分辨率">{mockCamera.resolution}</Descriptions.Item>
          <Descriptions.Item label="帧率">{mockCamera.fps} FPS</Descriptions.Item>
          <Descriptions.Item label="最后心跳" span={2}>
            {mockCamera.lastHeartbeat}
          </Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="实时视频流" style={{ marginTop: 16 }}>
        <div style={{ 
          height: 400, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: '#f0f0f0',
          borderRadius: 8
        }}>
          <Space direction="vertical">
            <VideoCameraOutlined style={{ fontSize: 64, color: '#ccc' }} />
            <span style={{ color: '#999' }}>视频流ID: {id}</span>
          </Space>
        </div>
      </Card>
    </div>
  )
}

export default MonitorDetail
