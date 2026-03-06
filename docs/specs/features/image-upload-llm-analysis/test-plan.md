# 测试计划：image-upload-llm-analysis

## 1. 测试范围

- 范围内：
  - 前端上传交互与参数校验。
  - `POST /api/images/analyze` 的输入校验、模型调用、响应结构。
  - 错误码与错误提示映射。
  - 受影响基础接口回归（`/api/health`、`/api/greeting`）。
- 范围外：
  - 用户鉴权、权限分级。
  - 批量上传与历史记录。
  - 对象存储持久化与离线异步处理。

## 2. 用例矩阵

- 用例 1（P0）：上传合法 `jpg/png/webp` 图片，返回 200，包含 `summary/tags/confidence`。
- 用例 2（P0）：上传超过 5MB 的图片，返回 `413 + INVALID_IMAGE_SIZE`。
- 用例 3（P0）：上传非图片文件（如 `.txt`），返回 `400 + UNSUPPORTED_IMAGE_TYPE`。
- 用例 4（P0）：缺失 `image` 字段，返回 `422 + INVALID_REQUEST`。
- 用例 5（P1）：模拟模型超时，返回 `504 + MODEL_TIMEOUT`，前端显示“可重试”提示。
- 用例 6（P1）：模拟模型上游异常，返回 `502 + MODEL_UPSTREAM_ERROR`，前端显示“服务暂不可用”。
- 用例 7（P1）：前端上传成功后，页面正确展示摘要、标签及置信度。
- 用例 8（P1）：连续提交 3 次不同图片，请求 ID 不重复且每次结果独立。
- 用例 9（P2）：模型返回字段缺失时，后端字段兜底，前端不崩溃。
- 用例 10（P1）：回归验证 `/api/health` 和 `/api/greeting` 行为未改变。

## 3. 测试数据

- `fixtures/ok-image.jpg`：小于 1MB 的正常商品图。
- `fixtures/ok-image.png`：正常截图样本。
- `fixtures/large-image.jpg`：大于 5MB 的边界文件。
- `fixtures/not-image.txt`：非法类型文件。
- 模型桩数据：
  - 成功响应样本。
  - 超时响应样本。
  - 上游 5xx 响应样本。

## 4. 执行命令

- 启动后端：
  - `cd backend && uvicorn main:app --host 0.0.0.0 --port 8080 --reload`
- 启动前端：
  - `cd frontend && npm run dev`
- 后端手工接口验证：
  - `curl -X POST "http://localhost:8080/api/images/analyze" -F "image=@fixtures/ok-image.jpg"`
  - `curl -X POST "http://localhost:8080/api/images/analyze" -F "image=@fixtures/large-image.jpg"`
  - `curl -X POST "http://localhost:8080/api/images/analyze" -F "image=@fixtures/not-image.txt"`
- 前端构建回归：
  - `cd frontend && npm run build`
- 现有接口回归：
  - `curl "http://localhost:8080/api/health"`
  - `curl "http://localhost:8080/api/greeting?name=Tom"`

## 5. 验收标准

- 所有 P0 用例必须通过。
- P1 用例通过率 100%；如存在已知问题需在 PR 明确风险与补救计划。
- 前端展示与 API 契约字段一致，无字段命名偏差。
- 出错场景可定位（日志含 `request_id`、错误码、耗时）。
- 现有健康检查和问候接口无行为回归。

## 6. 证据

- `curl` 命令输出（成功、失败各至少一条）。
- 前端页面截图：
  - 上传前状态
  - 上传成功状态
  - 上传失败状态（至少一种错误）
- PR 中附：
  - 本测试计划执行结果
  - 风险与回滚验证记录
