# Agent 宪法 - 工业安全监控系统开发准则
# 版本：1.0
# 日期：2026-06-18

## 核心原则

1. **架构锁定**：严格遵循 React + FastAPI + PostgreSQL 技术栈
2. **配置外置**：所有配置通过环境变量管理，禁止硬编码
3. **接口统一**：API响应格式 `{code, message, data}`
4. **安全第一**：JWT认证保护所有敏感接口
5. **日志记录**：关键操作必须记录结构化日志
6. **自检优先**：代码完成后必须自检再提交
7. **渐进开发**：按 P0 → P1 → P2 优先级分阶段

## 技术规范

### 后端 (Python FastAPI)
- 启动命令：`uvicorn app.main:app --reload`
- 模型路径：`backend/app/ml/models/`
- 检测器接口：`detect(frame)` 返回 `{bbox, class, confidence, timestamp}`

### 前端 (React + TypeScript)
- 组件命名：大驼峰 `VideoPlayer.tsx`
- 状态管理：Zustand
- API请求：统一Axios封装，自动携带Token

### 数据库 (PostgreSQL)
- 必须字段：`id, created_at, updated_at`
- 外键关系必须明确
- 敏感数据必须加密存储

## 开发优先级

### P0 核心功能
- 用户认证（登录/注册/权限）
- 摄像头管理（增删改查/状态监控）
- 基础告警（创建/查询/处理）

### P1 重要功能
- AI安全检测（安全帽/入侵/烟火）
- 实时告警通知
- 实时视频预览

### P2 增强功能
- 数据统计报表
- 录像回放
- 系统设置

## 代码自检清单

每次代码编写后必须检查：
- [ ] 架构目录结构正确
- [ ] 无硬编码配置
- [ ] 异常处理完整
- [ ] 日志记录到位
- [ ] TypeScript类型完整（前端）
- [ ] API测试通过
