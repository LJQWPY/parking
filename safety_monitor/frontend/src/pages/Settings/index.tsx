import { useState } from 'react'
import { Card, Form, Input, Switch, Button, Tabs, Divider, message, Select, InputNumber } from 'antd'

const { TabPane } = Tabs

const Settings = () => {
  const [form] = Form.useForm()
  const [detectionForm] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const handleSaveBasic = async (_values: any) => {
    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      message.success('保存成功')
    } catch (error) {
      message.error('保存失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveDetection = async (_values: any) => {
    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      message.success('保存成功')
    } catch (error) {
      message.error('保存失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h1 style={{ marginBottom: 24 }}>系统设置</h1>
      
      <Tabs defaultActiveKey="basic">
        <TabPane tab="基本设置" key="basic">
          <Card title="基本设置">
            <Form
              form={form}
              layout="vertical"
              initialValues={{
                systemName: '工业安全监控系统',
                systemVersion: '1.0.0',
                autoRefresh: true,
                refreshInterval: 30,
                language: 'zh-CN'
              }}
              onFinish={handleSaveBasic}
            >
              <Form.Item label="系统名称" name="systemName">
                <Input placeholder="请输入系统名称" />
              </Form.Item>
              
              <Form.Item label="系统版本" name="systemVersion">
                <Input disabled />
              </Form.Item>
              
              <Form.Item label="自动刷新" name="autoRefresh" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Form.Item label="刷新间隔(秒)" name="refreshInterval">
                <InputNumber min={10} max={300} />
              </Form.Item>
              
              <Form.Item label="界面语言" name="language">
                <Select>
                  <Select.Option value="zh-CN">简体中文</Select.Option>
                  <Select.Option value="en-US">English</Select.Option>
                </Select>
              </Form.Item>
              
              <Button type="primary" htmlType="submit" loading={loading}>
                保存设置
              </Button>
            </Form>
          </Card>
          
          <Card title="通知设置" style={{ marginTop: 24 }}>
            <Form
              layout="vertical"
              initialValues={{
                emailNotification: true,
                smsNotification: false,
                pushNotification: true
              }}
              onFinish={handleSaveBasic}
            >
              <Form.Item label="邮件通知" name="emailNotification" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Form.Item label="短信通知" name="smsNotification" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Form.Item label="推送通知" name="pushNotification" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Button type="primary" htmlType="submit" loading={loading}>
                保存设置
              </Button>
            </Form>
          </Card>
        </TabPane>
        
        <TabPane tab="AI检测设置" key="detection">
          <Card title="检测参数配置">
            <Form
              form={detectionForm}
              layout="vertical"
              initialValues={{
                confidenceThreshold: 0.5,
                detectionInterval: 1,
                enableHelmetDetection: true,
                enableFireDetection: true,
                enableZoneDetection: true,
                maxDetectionPerFrame: 10
              }}
              onFinish={handleSaveDetection}
            >
              <Divider>检测开关</Divider>
              
              <Form.Item label="安全帽检测" name="enableHelmetDetection" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Form.Item label="烟火检测" name="enableFireDetection" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Form.Item label="区域入侵检测" name="enableZoneDetection" valuePropName="checked">
                <Switch />
              </Form.Item>
              
              <Divider>检测参数</Divider>
              
              <Form.Item 
                label="置信度阈值" 
                name="confidenceThreshold"
                extra="检测结果置信度低于此值将被过滤，范围 0-1"
              >
                <InputNumber min={0} max={1} step={0.1} style={{ width: 200 }} />
              </Form.Item>
              
              <Form.Item 
                label="检测间隔(秒)" 
                name="detectionInterval"
                extra="每隔多少秒执行一次AI检测"
              >
                <InputNumber min={1} max={60} style={{ width: 200 }} />
              </Form.Item>
              
              <Form.Item 
                label="单帧最大检测数" 
                name="maxDetectionPerFrame"
                extra="每帧最多检测的目标数量"
              >
                <InputNumber min={1} max={100} style={{ width: 200 }} />
              </Form.Item>
              
              <Button type="primary" htmlType="submit" loading={loading}>
                保存设置
              </Button>
            </Form>
          </Card>
          
          <Card title="告警阈值设置" style={{ marginTop: 24 }}>
            <Form layout="vertical">
              <Form.Item label="严重告警阈值">
                <InputNumber min={1} max={100} defaultValue={10} style={{ width: 200 }} />
                <span style={{ marginLeft: 8 }}>次/分钟</span>
              </Form.Item>
              
              <Form.Item label="告警持续时间">
                <InputNumber min={1} max={60} defaultValue={5} style={{ width: 200 }} />
                <span style={{ marginLeft: 8 }}>秒</span>
              </Form.Item>
              
              <Button type="primary" onClick={() => message.success('保存成功')}>
                保存设置
              </Button>
            </Form>
          </Card>
        </TabPane>
        
        <TabPane tab="录像设置" key="record">
          <Card title="录像存储设置">
            <Form layout="vertical">
              <Form.Item label="录像存储路径">
                <Input defaultValue="/data/recordings" />
              </Form.Item>
              
              <Form.Item label="录像保留天数">
                <InputNumber min={1} max={90} defaultValue={7} style={{ width: 200 }} />
                <span style={{ marginLeft: 8 }}>天</span>
              </Form.Item>
              
              <Form.Item label="录像分辨率">
                <Select defaultValue="1080p">
                  <Select.Option value="720p">720p (1280x720)</Select.Option>
                  <Select.Option value="1080p">1080p (1920x1080)</Select.Option>
                  <Select.Option value="4k">4K (3840x2160)</Select.Option>
                </Select>
              </Form.Item>
              
              <Form.Item label="录像帧率">
                <Select defaultValue="25">
                  <Select.Option value="15">15 FPS</Select.Option>
                  <Select.Option value="25">25 FPS</Select.Option>
                  <Select.Option value="30">30 FPS</Select.Option>
                </Select>
              </Form.Item>
              
              <Button type="primary" onClick={() => message.success('保存成功')}>
                保存设置
              </Button>
            </Form>
          </Card>
          
          <Card title="存储空间" style={{ marginTop: 24 }}>
            <div style={{ marginBottom: 16 }}>
              <span>已使用: 256 GB / 1 TB</span>
              <div style={{ height: 8, background: '#f0f0f0', borderRadius: 4, marginTop: 8 }}>
                <div style={{ width: '25%', height: '100%', background: '#1890ff', borderRadius: 4 }} />
              </div>
            </div>
            <Button onClick={() => message.info('清理功能开发中')}>清理旧录像</Button>
          </Card>
        </TabPane>
        
        <TabPane tab="用户管理" key="user">
          <Card title="当前用户">
            <Form layout="vertical">
              <Form.Item label="用户名">
                <Input defaultValue="admin" disabled />
              </Form.Item>
              
              <Form.Item label="角色">
                <Input defaultValue="管理员" disabled />
              </Form.Item>
              
              <Form.Item label="修改密码">
                <Input.Password placeholder="请输入新密码" />
              </Form.Item>
              
              <Button type="primary" onClick={() => message.success('密码修改成功')}>
                修改密码
              </Button>
            </Form>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  )
}

export default Settings