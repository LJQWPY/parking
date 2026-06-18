import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Table, Tag, Progress } from 'antd'
import { 
  VideoCameraOutlined, 
  AlertOutlined, 
  WarningOutlined, 
  CheckCircleOutlined,
  SafetyOutlined,
  RiseOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'

interface WeekStat {
  date: string
  count: number
}

interface ViolationType {
  type: string
  count: number
}

const Dashboard = () => {
  const [loading, setLoading] = useState(true)
  const [overview, setOverview] = useState<{
    total_cameras: number
    online_cameras: number
    today_alerts: number
    urgent_alerts: number
    week_stats: WeekStat[]
  }>({
    total_cameras: 0,
    online_cameras: 0,
    today_alerts: 0,
    urgent_alerts: 0,
    week_stats: []
  })
  const [compliance, setCompliance] = useState<{
    compliance_rate: number
    helmet_wearing: { wearing: number; not_wearing: number }
    violation_types: ViolationType[]
  }>({
    compliance_rate: 0,
    helmet_wearing: { wearing: 0, not_wearing: 0 },
    violation_types: []
  })
  const [recentAlerts] = useState([
    { id: 1, type: 'no_helmet', level: 'medium', time: '10:32:15', camera: 1 },
    { id: 2, type: 'intrusion', level: 'high', time: '10:30:45', camera: 2 },
    { id: 3, type: 'fire', level: 'high', time: '10:20:00', camera: 1 },
    { id: 4, type: 'smoke', level: 'high', time: '10:18:30', camera: 1 },
  ])

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      // 模拟数据加载
      setOverview({
        total_cameras: 8,
        online_cameras: 6,
        today_alerts: 23,
        urgent_alerts: 3,
        week_stats: [
          { date: '06-12', count: 15 },
          { date: '06-13', count: 22 },
          { date: '06-14', count: 18 },
          { date: '06-15', count: 25 },
          { date: '06-16', count: 20 },
          { date: '06-17', count: 28 },
          { date: '06-18', count: 23 }
        ]
      })
      
      setCompliance({
        compliance_rate: 92.5,
        helmet_wearing: { wearing: 87, not_wearing: 13 },
        violation_types: [
          { type: '未佩戴安全帽', count: 42 },
          { type: '危险区域入侵', count: 28 },
          { type: '烟火隐患', count: 12 },
          { type: '其他违规', count: 18 }
        ]
      })
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const typeMap: Record<string, { text: string; color: string }> = {
    fire: { text: '火焰', color: 'red' },
    smoke: { text: '烟雾', color: 'orange' },
    no_helmet: { text: '未戴安全帽', color: 'gold' },
    intrusion: { text: '入侵', color: 'purple' },
    person: { text: '人员', color: 'blue' }
  }

  const levelMap: Record<string, { text: string; color: string }> = {
    high: { text: '严重', color: 'red' },
    medium: { text: '警告', color: 'orange' },
    low: { text: '提示', color: 'green' }
  }

  const alertColumns: ColumnsType<any> = [
    {
      title: '时间',
      dataIndex: 'time',
      key: 'time',
      width: 100
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color={typeMap[type]?.color || 'default'}>
          {typeMap[type]?.text || type}
        </Tag>
      )
    },
    {
      title: '级别',
      dataIndex: 'level',
      key: 'level',
      render: (level: string) => (
        <Tag color={levelMap[level]?.color || 'default'}>
          {levelMap[level]?.text || level}
        </Tag>
      )
    },
    {
      title: '摄像头',
      dataIndex: 'camera',
      key: 'camera',
      render: (id: number) => `摄像头 ${id}`
    }
  ]

  return (
    <div style={{ padding: 24, background: '#f0f2f5', minHeight: '100vh' }}>
      <h1 style={{ marginBottom: 24 }}>安全监控数据大屏</h1>
      
      {/* 概览统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="摄像头总数"
              value={overview.total_cameras}
              prefix={<VideoCameraOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8, color: '#52c41a' }}>
              在线: {overview.online_cameras} | 离线: {overview.total_cameras - overview.online_cameras}
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="今日告警"
              value={overview.today_alerts}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
            <div style={{ marginTop: 8 }}>
              较昨日 <span style={{ color: '#f5222d' }}>+5</span> <RiseOutlined style={{ color: '#f5222d' }} />
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="紧急告警"
              value={overview.urgent_alerts}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
            <div style={{ marginTop: 8, color: '#f5222d' }}>
              需要立即处理
            </div>
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic
              title="安全合规率"
              value={compliance.compliance_rate}
              suffix="%"
              prefix={<SafetyOutlined />}
              valueStyle={{ color: compliance.compliance_rate >= 90 ? '#52c41a' : '#faad14' }}
            />
            <Progress 
              percent={compliance.compliance_rate} 
              showInfo={false}
              strokeColor={compliance.compliance_rate >= 90 ? '#52c41a' : '#faad14'}
              size="small"
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        {/* 一周告警趋势 */}
        <Col span={12}>
          <Card title="一周告警趋势" loading={loading}>
            <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', height: 150 }}>
              {overview.week_stats.map((item: any, index: number) => (
                <div key={index} style={{ textAlign: 'center', flex: 1 }}>
                  <div style={{ 
                    background: '#1890ff', 
                    width: 30, 
                    height: Math.max(item.count * 4, 20), 
                    margin: '0 auto',
                    borderRadius: 4
                  }} />
                  <div style={{ marginTop: 4, fontSize: 12, color: '#666' }}>{item.count}</div>
                  <div style={{ fontSize: 10, color: '#999' }}>{item.date}</div>
                </div>
              ))}
            </div>
          </Card>
        </Col>
        
        {/* 安全装备佩戴率 */}
        <Col span={12}>
          <Card title="安全装备佩戴统计" loading={loading}>
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Progress 
                    type="circle" 
                    percent={compliance.helmet_wearing.wearing} 
                    strokeColor="#52c41a"
                    format={(percent) => (
                      <span style={{ fontSize: 20 }}>
                        {percent}%
                        <div style={{ fontSize: 12, color: '#666' }}>佩戴率</div>
                      </span>
                    )}
                  />
                </div>
              </Col>
              <Col span={12}>
                <div style={{ paddingTop: 20 }}>
                  <div style={{ marginBottom: 16 }}>
                    <span style={{ color: '#52c41a' }}>● 已佩戴: {compliance.helmet_wearing.wearing}%</span>
                  </div>
                  <div>
                    <span style={{ color: '#f5222d' }}>● 未佩戴: {compliance.helmet_wearing.not_wearing}%</span>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 违规类型分布 */}
        <Col span={12}>
          <Card title="违规类型分布" loading={loading}>
            {compliance.violation_types.map((item: any, index: number) => (
              <div key={index} style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span>{item.type}</span>
                  <span style={{ color: '#666' }}>{item.count}次</span>
                </div>
                <Progress 
                  percent={Math.round(item.count / compliance.violation_types[0].count * 100)} 
                  strokeColor={['#f5222d', '#fa8c16', '#faad14', '#52c41a'][index]}
                  showInfo={false}
                />
              </div>
            ))}
          </Card>
        </Col>
        
        {/* 最新告警列表 */}
        <Col span={12}>
          <Card title="最新告警" loading={loading} extra={<a href="/alert">查看全部</a>}>
            <Table
              columns={alertColumns}
              dataSource={recentAlerts}
              rowKey="id"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* 系统状态 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={24}>
          <Card title="系统状态">
            <Row gutter={16}>
              <Col span={6}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />
                  <div>
                    <div style={{ fontWeight: 'bold' }}>数据库连接</div>
                    <div style={{ color: '#52c41a' }}>正常</div>
                  </div>
                </div>
              </Col>
              <Col span={6}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />
                  <div>
                    <div style={{ fontWeight: 'bold' }}>AI检测服务</div>
                    <div style={{ color: '#52c41a' }}>运行中</div>
                  </div>
                </div>
              </Col>
              <Col span={6}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />
                  <div>
                    <div style={{ fontWeight: 'bold' }}>视频流服务</div>
                    <div style={{ color: '#52c41a' }}>正常</div>
                  </div>
                </div>
              </Col>
              <Col span={6}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 20 }} />
                  <div>
                    <div style={{ fontWeight: 'bold' }}>云端同步</div>
                    <div style={{ color: '#52c41a' }}>已连接</div>
                  </div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard