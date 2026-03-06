# fullstack-python-vue-starter

一个前后端分离的基础脚手架：

- 前端：Vue 3 + Vite + TypeScript + Pinia + Vue Router + Axios
- 后端：Python + FastAPI

## 目录结构

```text
fullstack-python-vue-starter/
├── backend/   # FastAPI
└── frontend/  # Vue3 应用
```

## 环境要求

- Python 3.10+
- Node.js 18+

## 启动方式

### 1. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows 用 .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

默认地址：`http://localhost:8080`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://localhost:5173`

前端开发服务器已配置代理：`/api -> http://localhost:8080`

## 示例接口

- `GET /api/health`：健康检查
- `GET /api/greeting?name=YourName`：问候接口
