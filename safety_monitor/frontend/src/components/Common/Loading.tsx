import { Spin } from 'antd'

const Loading = () => {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      background: '#f0f2f5'
    }}>
      <Spin size="large" tip="加载中..." />
    </div>
  )
}

export default Loading
