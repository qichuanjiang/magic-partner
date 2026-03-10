# magic-partner

一个前后端分离的基础脚手架：

- 前端：Vue 3 + Vite + TypeScript + Vue Router + Axios + Vitest
- 后端：Python + FastAPI

## 目录结构

```text
magic-partner/
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
- `POST /api/images/analyze`：上传图片并返回分析结果

## 图片分析接口（image-upload-llm-analysis）

### 请求约束

- `Content-Type`：`multipart/form-data`
- 文件字段：`image`
- 可选字段：`prompt`
- 支持格式：`jpg/jpeg/png/webp`
- 大小限制：`<= 5MB`

### 运行模式

后端支持两种分析模式（默认 `mock`）：

- `IMAGE_ANALYZER_MODE=mock`：返回固定模拟结果，适合本地联调。
- `IMAGE_ANALYZER_MODE=openai`：调用 OpenAI Responses API。

当使用 `openai` 模式时，需要设置：

- `OPENAI_API_KEY`
- 可选 `IMAGE_ANALYZER_MODEL`（默认 `gpt-4.1-mini`）
- 可选 `IMAGE_ANALYZER_TIMEOUT_SEC`（默认 `15` 秒）

示例（macOS/Linux）：

```bash
cd backend
export IMAGE_ANALYZER_MODE=openai
export OPENAI_API_KEY=your_key_here
.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### 手工验证

```bash
curl -X POST "http://localhost:8080/api/images/analyze" \
  -F "image=@/path/to/demo.jpg"
```

## 后端测试

```bash
cd backend
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

## 前端测试

```bash
cd frontend
npm test
```

## 开发规范（Spec First）

- 规范目录：`specs/`
- 模板目录：`specs/templates/`
- 新需求目录：`specs/features/<feature-name>/`

开发前请先创建并填写：

- `spec.md`
- `tasks.md`
- `test-plan.md`

详细流程见：`specs/README.md`

## 治理文档

- `AGENTS.md`：仓库协作规则与执行约束
- `constitution.md`：项目治理原则、工程底线与决策准则

开始任何功能开发、接口调整或架构变更前，请先阅读 `AGENTS.md` 与 `constitution.md`。
