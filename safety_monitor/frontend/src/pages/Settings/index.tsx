import { Card, Form, Input, Button, Switch, message } from 'antd'
import { SaveOutlined } from '@ant-design/icons'

const Settings = () => {
  const [form] = Form.useForm()
  
  const onFinish = () => {
    message.success('保存成功')
  }
  
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>系统设置</h1>
      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            systemName: '工业安全监控系统',
            companyName: '某某工业集团',
            contactEmail: 'admin@company.com',
            contactPhone: '400-888-8888'
          }}
        >
          <Form.Item label="系统名称" name="systemName">
            <Input />
          </Form.Item>
          <Form.Item label="企业名称" name="companyName">
            <Input />
          </Form.Item>
          <Form.Item label="联系邮箱" name="contactEmail">
            <Input />
          </Form.Item>
          <Form.Item label="联系电话" name="contactPhone">
            <Input />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
              保存
            </Button>
          </Form.Item>
        </Form>
      </Card>
      <Card title="告警设置">
        <Form layout="vertical">
          <Form.Item label="开启邮件通知">
            <Switch defaultChecked />
          </Form.Item>
          <Form.Item label="开启短信通知">
            <Switch />
          </Form.Item>
          <Form.Item label="告警阈值 - 温度 (°C)">
            <Input type="number" defaultValue="60" style={{ width: 200 }} />
          </Form.Item>
          <Form.Item label="告警阈值 - 湿度 (%)">
            <Input type="number" defaultValue="80" style={{ width: 200 }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<SaveOutlined />}>
              保存
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default Settings
