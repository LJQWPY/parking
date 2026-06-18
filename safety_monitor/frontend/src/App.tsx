import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import AppRoutes from './router'

const App = () => {
  return (
    <BrowserRouter>
      <ConfigProvider locale={zhCN}>
        <AppRoutes />
      </ConfigProvider>
    </BrowserRouter>
  )
}

export default App
