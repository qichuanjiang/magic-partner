# 仓库协作指南

## 项目结构
- `backend/`：FastAPI 后端服务，入口文件为 `main.py`，测试文件位于 `backend/tests/`。
- `frontend/`：Vue 3 + Vite + TypeScript 前端应用，主要目录包括 `src/api`、`src/views`、`src/router`、`src/stores`、`src/assets`。
- `specs/`：采用 Spec-first 流程的文档与功能规格说明。
- 新功能规格请放在 `specs/features/<feature-name>/` 下，并包含以下文件：
  - `spec.md`
  - `tasks.md`
  - `test-plan.md`
- 新建功能规格时，默认基于 `specs/templates/` 下的正式模板创建，不应省略模板中的“宪法对齐检查”部分
- `.github/pull_request_template.md`：PR 模板，包含必填检查项和规格文档引用要求。

## 治理约束
- 所有开发、重构、测试、评审与文档更新，必须遵循根目录下的 `constitution.md`
- 若局部实现习惯与 `constitution.md` 冲突，以 `constitution.md` 为准
- 任何非微小改动都应先补齐规格文档，并在规格中完成“宪法对齐检查”后再进入实现阶段
- 所有新功能或 Bug 修复，默认遵循“先写失败测试，再实现代码，再重构”的顺序
- 后端优先使用 FastAPI 原生能力；前端优先使用 Vue 3、Vite 及其官方推荐工具
- 避免不必要的抽象层、无关路由、无关状态管理和超出规格范围的功能添加
- 所有错误必须显式处理，不允许依赖隐式失败路径

## 构建、测试与本地开发
- 后端初始化与运行：
  - `cd backend && python -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - `uvicorn main:app --host 0.0.0.0 --port 8080 --reload`
- 后端测试：
  - `cd backend && .venv/bin/python -m pytest -q`
- 前端初始化与运行：
  - `cd frontend && npm install`
  - `npm run dev`：启动本地开发服务器
  - `npm run build`：执行类型检查并构建生产包
  - `npm run preview`：预览构建结果

## 代码风格与命名规范
- Python：
  - 遵循 PEP 8
  - 使用 4 个空格缩进
  - 函数与变量使用 `snake_case`
  - Pydantic 模型使用 `PascalCase`
- TypeScript / Vue：
  - 使用 2 个空格缩进
  - 变量与函数使用 `camelCase`
  - 组件文件使用 `PascalCase`，例如 `HomeView.vue`
- API 客户端模块统一放在 `frontend/src/api/`
- 路由页面统一放在 `frontend/src/views/`
- 规格目录名称必须使用 `kebab-case`，例如 `image-upload-llm-analysis`

## 测试要求
- 后端测试框架为 `pytest`
- 前端测试框架为 `vitest`
- 新增测试请放在 `backend/tests/` 下，并命名为 `test_<feature>.py`
- 前端单元测试建议与被测模块同目录放置，命名为 `*.test.ts`
- 每个 API 变更都应覆盖：
  - 成功路径
  - 关键错误路径
  - 状态码与响应体断言
- 单元测试优先采用表格驱动测试风格
- 提交 PR 前必须执行 `pytest -q`

## 提交与 PR 规范
- 提交信息遵循仓库现有的 Conventional Commits 风格，例如：
  - `feat:`
  - `fix:`
  - `docs:`
  - `chore:`
- 每次提交应聚焦单一逻辑变更，避免混入无关内容
- 提交 PR 时必须：
  - 关联对应规格文档：`specs/features/<feature-name>/spec.md`、`tasks.md`、`test-plan.md`
  - 按 PR 模板提供测试证据，例如日志或截图
  - 对非简单变更说明风险等级与回滚方案

## 自定义指令
- 当用户说“帮我提交并推送代码”时，按以下顺序执行：
  - 先检查 `git status --short`、当前分支和远端状态
  - 确认本次变更范围与已完成工作一致，不遗漏新增文件或误提交无关内容
  - 使用符合 Conventional Commits 的提交信息执行 `git add -A`、`git commit`
  - 默认推送到当前分支对应的远端上游分支
  - 完成后返回提交信息、提交哈希和推送结果
- 若工作区存在明显无关或冲突性修改，需要先向用户说明风险，再决定是否继续提交

## 安全与配置
- 不要提交任何密钥或敏感信息
- 统一通过环境变量配置，例如 `OPENAI_API_KEY`、`IMAGE_ANALYZER_MODE`
- 本地图片分析模式默认使用 `mock`
- 仅在已正确配置有效凭据时，才切换到 `openai` 模式
