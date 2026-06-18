import { useState } from 'react'
import { Table, Tag, Button, Space, Input, Card } from 'antd'
import { SearchOutlined, EyeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import type { Camera } from '../../api/types'

const Monitor = () => {
  const navigate = useNavigate()
  const [loading] = useState(false)
  const [searchText, setSearchText] = useState('')
  
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          online: 'green',
          offline: 'gray',
          error: 'red'
        }
        const textMap: Record<string, string> = {
          online: '在线',
          offline: '离线',
          error: '异常'
        }
        return <Tag color={colorMap[status]}>{textMap[status]}</Tag>
      }
    },
    {
      title: '最后心跳',
      dataIndex: 'lastHeartbeat',
      key: 'lastHeartbeat'
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Camera) => (
        <Space>
          <Button 
            type="link" 
            icon={<EyeOutlined />}
            onClick={() => navigate(`/monitor/${record.id}`)}
          >
            查看
          </Button>
        </Space>
      )
    }
  ]
  
  // 模拟数据
  const mockData: Camera[] = [
    { id: 1, name: '1号车间摄像头', location: 'A区1号车间', status: 'online', lastHeartbeat: '2024-01-15 10:30:00' },
    { id: 2, name: '2号车间摄像头', location: 'A区2号车间', status: 'online', lastHeartbeat: '2024-01-15 10:30:00' },
    { id: 3, name: '仓库摄像头', location: 'B区仓库', status: 'offline', lastHeartbeat: '2024-01-15 09:00:00' },
    { id: 4, name: '大门摄像头', location: '厂区大门', status: 'error', lastHeartbeat: '2024-01-15 08:00:00' },
    { id: 5, name: '办公楼摄像头', location: 'C区办公楼', status: 'online', lastHeartbeat: '2024-01-15 10:30:00' },
  ]
  
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>摄像头管理</h1>
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Input
            placeholder="搜索摄像头..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 300 }}
          />
        </div>
        <Table
          columns={columns}
          dataSource={mockData.filter(item => 
            item.name.includes(searchText) || (item.location && item.location.includes(searchText))
          )}
          rowKey="id"
          loading={loading}
        />
      </Card>
    </div>
  )
}

export default Monitor
