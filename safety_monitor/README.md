# 工业安全监控系统 - Safety Monitor

基于 AI 视觉的工业安全监控系统，支持多摄像头接入、实时安全检测和告警管理。

## 功能特性

- 多摄像头统一管理（支持 ≤10 路摄像头）
- AI 安全检测（安全帽、危险区域入侵、烟火检测）
- 实时告警通知
- 数据统计报表
- 用户权限管理

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + TypeScript + Ant Design |
| 后端 | Python 3.10 + FastAPI |
| 数据库 | PostgreSQL |
| AI | PyTorch + YOLOv8 |

## 项目结构

```
safety_monitor/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/     # API路由
│   │   ├── models/  # 数据模型
│   │   ├── schemas/ # Pydantic模型
│   │   └── core/    # 核心模块
│   └── requirements.txt
├── frontend/         # React 前端
│   ├── src/
│   │   ├── api/     # API封装
│   │   ├── pages/   # 页面组件
│   │   └── stores/  # 状态管理
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 快速启动

### 方式一：Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 方式二：手动启动

**后端**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量
cp .env.example .env
# 编辑 .env 配置数据库

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 环境变量配置

### 后端 (.env)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/safety_monitor
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## API 文档

启动后端服务后，访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 默认账号

首次启动后，注册第一个管理员账号即可使用。

## 开发指南

请参考 [AGENT_CONSTITUTION.md](./AGENT_CONSTITUTION.md) 了解开发规范。

## License

MIT