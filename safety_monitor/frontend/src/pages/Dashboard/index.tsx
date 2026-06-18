import { Row, Col, Card, Statistic } from 'antd'
import { 
  VideoCameraOutlined, 
  AlertOutlined, 
  CheckCircleOutlined,
  WarningOutlined 
} from '@ant-design/icons'

const Dashboard = () => {
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>数据大屏</h1>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic
              title="在线摄像头"
              value={28}
              prefix={<VideoCameraOutlined style={{ color: '#52c41a' }} />}
              suffix="/ 32"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日告警"
              value={12}
              prefix={<AlertOutlined style={{ color: '#faad14' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已处理"
              value={10}
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理"
              value={2}
              prefix={<WarningOutlined style={{ color: '#ff4d4f' }} />}
            />
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="实时监控画面" style={{ height: 400 }}>
            <div style={{ 
              height: '100%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              background: '#f0f0f0',
              borderRadius: 8
            }}>
              <VideoCameraOutlined style={{ fontSize: 64, color: '#ccc' }} />
              <span style={{ marginLeft: 16, color: '#999' }}>实时视频流区域</span>
            </div>
          </Card>
        </Col>
      </Row>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="告警趋势">
            <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ccc' }}>
              图表区域
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="最近告警">
            <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ccc' }}>
              列表区域
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
