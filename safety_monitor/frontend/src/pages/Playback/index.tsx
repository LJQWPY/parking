import { useState, useEffect } from 'react'
import { Card, Row, Col, DatePicker, Select, Table, Button, Space, Tag, Modal, message } from 'antd'
import { PlayCircleOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import { cameraApi } from '../../api/camera'
import { recordingApi, Recording } from '../../api/recording'

const { RangePicker } = DatePicker

const Playback = () => {
  const [cameras, setCameras] = useState<any[]>([])
  const [recordings, setRecordings] = useState<Recording[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedCamera, setSelectedCamera] = useState<number | null>(null)
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)
  const [playing, setPlaying] = useState<Recording | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  useEffect(() => {
    fetchCameras()
    fetchRecordings()
  }, [])

  const fetchCameras = async () => {
    try {
      const res = await cameraApi.getList({ page: 1, pageSize: 100 })
      const data = (res as any).data?.data || (res as any).data || []
      setCameras(data)
    } catch (error) {
      console.error('获取摄像头失败:', error)
    }
  }

  const fetchRecordings = async () => {
    setLoading(true)
    try {
      const params: any = { skip: (page - 1) * pageSize, limit: pageSize }
      if (selectedCamera) {
        params.camera_id = selectedCamera
      }
      if (dateRange) {
        params.start_date = dateRange[0].toISOString()
        params.end_date = dateRange[1].toISOString()
      }
      const res = await recordingApi.list(params)
      setRecordings((res as any).data || [])
    } catch (error) {
      console.error('获取录像失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    setPage(1)
    fetchRecordings()
  }

  const handleReset = () => {
    setSelectedCamera(null)
    setDateRange(null)
    setPage(1)
    fetchRecordings()
  }

  const handlePlay = (record: Recording) => {
    setPlaying(record)
  }

  const handleClosePlayer = () => {
    setPlaying(null)
  }

  const handleDelete = async (id: number) => {
    try {
      await recordingApi.delete(id)
      message.success('删除成功')
      fetchRecordings()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const formatDuration = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
    }
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
  }

  const columns = [
    {
      title: '摄像头',
      dataIndex: 'camera_name',
      key: 'camera_name',
      width: 150
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 180,
      render: (text: string) => dayjs(text).format('YYYY-MM-DD HH:mm:ss')
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      width: 180,
      render: (text: string) => text ? dayjs(text).format('YYYY-MM-DD HH:mm:ss') : '-'
    },
    {
      title: '时长',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
      render: (text: number) => text ? formatDuration(text) : '-'
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (text: number) => text ? formatFileSize(text) : '-'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const colors: Record<string, string> = {
          recording: 'blue',
          completed: 'green',
          failed: 'red'
        }
        const labels: Record<string, string> = {
          recording: '录制中',
          completed: '已完成',
          failed: '失败'
        }
        return <Tag color={colors[status] || 'default'}>{labels[status] || status}</Tag>
      }
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: Recording) => (
        <Space>
          <Button
            type="link"
            icon={<PlayCircleOutlined />}
            onClick={() => handlePlay(record)}
            disabled={record.status !== 'completed'}
          >
            播放
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div>
      <Card title="录像回放" style={{ marginBottom: 16 }}>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Select
              placeholder="选择摄像头"
              style={{ width: '100%' }}
              allowClear
              value={selectedCamera}
              onChange={setSelectedCamera}
            >
              {cameras.map(cam => (
                <Select.Option key={cam.id} value={cam.id}>{cam.name}</Select.Option>
              ))}
            </Select>
          </Col>
          <Col span={8}>
            <RangePicker
              style={{ width: '100%' }}
              value={dateRange}
              onChange={(dates) => setDateRange(dates as [dayjs.Dayjs, dayjs.Dayjs] | null)}
              showTime
            />
          </Col>
          <Col span={10}>
            <Space>
              <Button type="primary" onClick={handleSearch}>查询</Button>
              <Button onClick={handleReset}>重置</Button>
              <Button icon={<ReloadOutlined />} onClick={fetchRecordings}>刷新</Button>
            </Space>
          </Col>
        </Row>

        <Table
          columns={columns}
          dataSource={recordings}
          rowKey="id"
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: recordings.length,
            onChange: (p, ps) => {
              setPage(p)
              setPageSize(ps)
              fetchRecordings()
            }
          }}
        />
      </Card>

      <Modal
        title="录像播放"
        open={!!playing}
        onCancel={handleClosePlayer}
        footer={null}
        width={900}
        destroyOnClose
      >
        {playing && (
          <div style={{ textAlign: 'center' }}>
            <video
              src={playing.file_path}
              controls
              autoPlay
              style={{ width: '100%', maxHeight: '70vh' }}
            />
            <div style={{ marginTop: 16 }}>
              <p><strong>摄像头：</strong>{playing.camera_name}</p>
              <p><strong>录制时间：</strong>{dayjs(playing.start_time).format('YYYY-MM-DD HH:mm:ss')}</p>
              {playing.duration && <p><strong>时长：</strong>{formatDuration(playing.duration)}</p>}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default Playback
