import { useState, useEffect } from 'react'
import { Table, Tag, Button, Space, Card, Badge, Statistic, Row, Col } from 'antd'
import { WarningOutlined, CheckCircleOutlined, ClockCircleOutlined, WarningFilled } from '@ant-design/icons'
import type { Alert } from '../../api/types'

const AlertPage = () => {
  const [loading, setLoading] = useState(false)
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [stats, setStats] = useState({ total: 0, high: 0, medium: 0, low: 0, unhandled: 0 })

  useEffect(() => {
    loadAlerts()
    loadStats()
  }, [])

  const loadAlerts = async () => {
    setLoading(true)
    try {
      const mockAlerts: Alert[] = [
        {
          id: 1,
          camera_id: 1,
          alert_type: 'no_helmet',
          level: 'medium',
          description: '检测到未佩戴安全帽 (置信度: 0.85)',
          is_handled: false,
          created_at: '2024-01-15 10:32:15'
        },
        {
          id: 2,
          camera_id: 2,
          alert_type: 'intrusion',
          level: 'high',
          description: '检测到危险区域入侵 - 高压区 (置信度: 0.92)',
          is_handled: false,
          created_at: '2024-01-15 10:30:45'
        },
        {
          id: 3,
          camera_id: 1,
          alert_type: 'fire',
          level: 'high',
          description: '检测到火焰 (置信度: 0.88)',
          is_handled: true,
          handled_by: 'admin',
          handled_at: '2024-01-15 10:25:00',
          created_at: '2024-01-15 10:20:00'
        },
        {
          id: 4,
          camera_id: 3,
          alert_type: 'person',
          level: 'low',
          description: '检测到人员 (置信度: 0.75)',
          is_handled: true,
          handled_by: 'admin',
          handled_at: '2024-01-15 10:15:00',
          created_at: '2024-01-15 10:10:00'
        },
        {
          id: 5,
          camera_id: 1,
          alert_type: 'smoke',
          level: 'high',
          description: '检测到烟雾 (置信度: 0.90)',
          is_handled: false,
          created_at: '2024-01-15 10:18:30'
        }
      ]
      setAlerts(mockAlerts)
    } catch (error) {
      console.error('加载告警失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      setStats({
        total: 5,
        high: 3,
        medium: 1,
        low: 1,
        unhandled: 3
      })
    } catch (error) {
      console.error('加载统计失败:', error)
    }
  }

  const handleAlert = (alertId: number) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, is_handled: true, handled_by: 'admin', handled_at: new Date().toLocaleString() } : alert
    ))
    setStats(prev => ({ ...prev, unhandled: prev.unhandled - 1 }))
  }

  const levelConfig: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
    high: { color: 'red', text: '严重', icon: <WarningFilled /> },
    medium: { color: 'orange', text: '警告', icon: <WarningOutlined /> },
    low: { color: 'yellow', text: '提示', icon: <ClockCircleOutlined /> }
  }

  const typeConfig: Record<string, string> = {
    fire: '火焰检测',
    smoke: '烟雾检测',
    no_helmet: '未佩戴安全帽',
    intrusion: '区域入侵',
    person: '人员检测'
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '告警类型',
      dataIndex: 'alert_type',
      key: 'alert_type',
      render: (type: string) => (
        <Tag color="blue">{typeConfig[type] || type}</Tag>
      )
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      render: (level: string) => {
        const config = levelConfig[level]
        return config ? <Tag color={config.color}>{config.icon} {config.text}</Tag> : <Tag>{level}</Tag>
      }
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: '摄像头',
      dataIndex: 'camera_id',
      key: 'camera_id',
      render: (id: number) => `摄像头 ${id}`
    },
    {
      title: '状态',
      dataIndex: 'is_handled',
      key: 'is_handled',
      render: (handled: boolean) => (
        handled 
          ? <Tag color="green"><CheckCircleOutlined /> 已处理</Tag>
          : <Tag color="red"><WarningOutlined /> 未处理</Tag>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at'
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Alert) => (
        <Space>
          {!record.is_handled && (
            <Button 
              type="primary" 
              size="small"
              onClick={() => handleAlert(record.id)}
            >
              处理
            </Button>
          )}
          {record.handled_by && (
            <span style={{ color: '#999', fontSize: 12 }}>
              处理人: {record.handled_by}
            </span>
          )}
        </Space>
      )
    }
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>告警管理</h1>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic title="总告警数" value={stats.total} prefix={<WarningOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="严重告警" value={stats.high} prefix={<WarningFilled />} valueStyle={{ color: '#f5222d' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="警告告警" value={stats.medium} prefix={<WarningOutlined />} valueStyle={{ color: '#fa8c16' }} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="未处理" value={stats.unhandled} prefix={<ClockCircleOutlined />} valueStyle={{ color: '#faad14' }} />
            {stats.unhandled > 0 && (
              <Badge dot color="red" style={{ position: 'absolute', top: 10, right: 10 }} />
            )}
          </Card>
        </Col>
      </Row>

      <Card>
        <Table
          columns={columns}
          dataSource={alerts}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}

export default AlertPage