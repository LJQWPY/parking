import { Layout as AntLayout } from 'antd'
import { Outlet } from 'react-router-dom'
import Sider from './Sider'

const { Header, Content } = AntLayout

const Layout = () => {
  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider />
      <AntLayout>
        <Header style={{ 
          background: '#001529', 
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ color: '#fff', fontSize: 18, fontWeight: 500 }}>
            工业安全监控系统
          </div>
          <div style={{ color: '#fff' }}>
            欢迎使用
          </div>
        </Header>
        <Content style={{ margin: 16, padding: 24, background: '#fff', minHeight: 280 }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  )
}

export default Layout
