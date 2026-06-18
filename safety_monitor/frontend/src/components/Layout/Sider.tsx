import { Layout as AntLayout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  VideoCameraOutlined,
  AlertOutlined,
  PlayCircleOutlined,
  SettingOutlined
} from '@ant-design/icons'
import { useAppStore } from '../../stores/appStore'

const { Sider } = AntLayout

const menuItems = [
  {
    key: '/dashboard',
    icon: <DashboardOutlined />,
    label: '数据大屏'
  },
  {
    key: '/monitor',
    icon: <VideoCameraOutlined />,
    label: '摄像头管理'
  },
  {
    key: '/alert',
    icon: <AlertOutlined />,
    label: '告警管理'
  },
  {
    key: '/playback',
    icon: <PlayCircleOutlined />,
    label: '录像回放'
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: '系统设置'
  }
]

const SiderComponent = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const collapsed = useAppStore((state) => state.collapsed)
  const setCollapsed = useAppStore((state) => state.setCollapsed)
  
  const currentPath = location.pathname === '/' ? '/dashboard' : location.pathname
  
  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={setCollapsed}
      style={{ overflow: 'auto', height: '100vh', position: 'fixed', left: 0, top: 0, bottom: 0 }}
    >
      <div style={{ 
        height: 64, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        color: '#fff',
        fontSize: collapsed ? 16 : 18,
        fontWeight: 'bold'
      }}>
        {collapsed ? '安全' : '工业安全监控'}
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[currentPath]}
        items={menuItems}
        onClick={({ key }) => navigate(key)}
      />
    </Sider>
  )
}

export default SiderComponent
