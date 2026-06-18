import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, Descriptions, Tag, Space, Switch } from 'antd'
import { ArrowLeftOutlined, VideoCameraOutlined, PlayCircleOutlined, PauseCircleOutlined, SafetyCertificateOutlined } from '@ant-design/icons'
import { cameraApi, getStreamUrl } from '../../api/camera'
import type { WrappedResponse } from '../../api/types'

const MonitorDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [camera, setCamera] = useState<{
    id: string
    name: string
    location: string
    status: string
    streamUrl: string
    lastHeartbeat: string
    resolution: string
    fps: number
  } | null>(null)
  const [isStreaming, setIsStreaming] = useState(false)
  const [isDetectionEnabled, setIsDetectionEnabled] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (id) {
      loadCameraInfo()
    }
  }, [id])

  const loadCameraInfo = async () => {
    setLoading(true)
    try {
      const response = await cameraApi.getById(parseInt(id!)) as unknown as WrappedResponse<any>
      if (response.code === 200) {
        setCamera({
          id: response.data.id.toString(),
          name: response.data.name,
          location: response.data.location || '未设置',
          status: response.data.status || 'offline',
          streamUrl: getStreamUrl(response.data.id, isDetectionEnabled),
          lastHeartbeat: response.data.last_updated || '未知',
          resolution: '1920x1080',
          fps: 30
        })
        setIsStreaming(response.data.status === 'online')
      }
    } catch (error) {
      console.error('加载摄像头信息失败:', error)
      setCamera({
        id: id!,
        name: `摄像头 ${id}`,
        location: '测试位置',
        status: 'offline',
        streamUrl: getStreamUrl(parseInt(id!), isDetectionEnabled),
        lastHeartbeat: '2024-01-15 10:30:00',
        resolution: '1920x1080',
        fps: 30
      })
    } finally {
      setLoading(false)
    }
  }

  const toggleStream = async (checked: boolean) => {
    if (!id) return
    setLoading(true)
    try {
      if (checked) {
        const response = await cameraApi.startStream(parseInt(id)) as unknown as WrappedResponse<any>
        if (response.code === 200) {
          setIsStreaming(true)
          setCamera(prev => prev ? { ...prev, status: 'online', streamUrl: getStreamUrl(parseInt(id), isDetectionEnabled) } : null)
        }
      } else {
        const response = await cameraApi.stopStream(parseInt(id)) as unknown as WrappedResponse<any>
        if (response.code === 200) {
          setIsStreaming(false)
          setCamera(prev => prev ? { ...prev, status: 'offline' } : null)
        }
      }
    } catch (error) {
      console.error('切换摄像头状态失败:', error)
      setIsStreaming(!checked)
    } finally {
      setLoading(false)
    }
  }

  const toggleDetection = async (checked: boolean) => {
    if (!id) return
    setLoading(true)
    try {
      const response = await cameraApi.toggleDetection(parseInt(id), checked) as unknown as WrappedResponse<any>
      if (response.code === 200) {
        setIsDetectionEnabled(checked)
        setCamera(prev => prev ? { ...prev, streamUrl: getStreamUrl(parseInt(id), checked) } : null)
      }
    } catch (error) {
      console.error('切换AI检测状态失败:', error)
      setIsDetectionEnabled(!checked)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div>加载中...</div>
  }

  if (!camera) {
    return <div>摄像头不存在</div>
  }

  const statusColor = {
    online: 'green',
    offline: 'gray',
    error: 'red'
  }[camera.status] || 'gray'

  const statusText = {
    online: '在线',
    offline: '离线',
    error: '异常'
  }[camera.status] || '未知'

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
      <Card title="摄像头详情" extra={
        <Space>
          <span style={{ marginRight: 8 }}>视频流</span>
          <Switch
            checked={isStreaming}
            onChange={toggleStream}
            loading={loading}
            checkedChildren={<PlayCircleOutlined />}
            unCheckedChildren={<PauseCircleOutlined />}
          />
          {isStreaming && (
            <>
              <span style={{ marginRight: 8, marginLeft: 16 }}>AI检测</span>
              <Switch
                checked={isDetectionEnabled}
                onChange={toggleDetection}
                loading={loading}
                checkedChildren={<SafetyCertificateOutlined />}
              />
            </>
          )}
        </Space>
      }>
        <Descriptions column={2}>
          <Descriptions.Item label="ID">{camera.id}</Descriptions.Item>
          <Descriptions.Item label="名称">{camera.name}</Descriptions.Item>
          <Descriptions.Item label="位置">{camera.location}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={statusColor}>{statusText}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="分辨率">{camera.resolution}</Descriptions.Item>
          <Descriptions.Item label="帧率">{camera.fps} FPS</Descriptions.Item>
          <Descriptions.Item label="AI检测" span={2}>
            <Tag color={isDetectionEnabled ? 'green' : 'gray'}>
              {isDetectionEnabled ? '已启用' : '已禁用'}
            </Tag>
            <span style={{ marginLeft: 8, color: '#999', fontSize: 12 }}>
              (安全帽检测 · 烟火检测 · 区域入侵)
            </span>
          </Descriptions.Item>
          <Descriptions.Item label="最后心跳" span={2}>
            {camera.lastHeartbeat}
          </Descriptions.Item>
        </Descriptions>
      </Card>
      <Card title="实时视频流" style={{ marginTop: 16 }}>
        <div style={{
          height: 480,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#1a1a1a',
          borderRadius: 8,
          overflow: 'hidden'
        }}>
          {isStreaming ? (
            <img
              src={camera.streamUrl}
              alt="实时视频流"
              style={{
                maxWidth: '100%',
                maxHeight: '100%',
                objectFit: 'contain'
              }}
            />
          ) : (
            <Space direction="vertical">
              <VideoCameraOutlined style={{ fontSize: 64, color: '#666' }} />
              <span style={{ color: '#999' }}>
                {camera.status === 'online' ? '点击开启视频流' : '摄像头离线'}
              </span>
            </Space>
          )}
        </div>
        {isDetectionEnabled && isStreaming && (
          <div style={{ marginTop: 16, padding: 12, background: '#fffbe6', borderRadius: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <SafetyCertificateOutlined style={{ color: '#faad14', marginRight: 8 }} />
              <span style={{ color: '#d48806', fontWeight: 'bold' }}>AI检测已启用</span>
              <span style={{ color: '#999', marginLeft: 8 }}>- 正在进行安全装备检测、烟火检测和危险区域入侵检测</span>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}

export default MonitorDetail