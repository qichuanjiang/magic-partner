# 测试计划：sample-user-greeting

## 1. 测试范围

- 范围内：`/api/greeting` 行为与响应结构。
- 范围外：鉴权、持久化及其他接口。

## 2. 用例矩阵

- 用例 1：`GET /api/greeting?name=Tom` 返回 `Hello, Tom!`
- 用例 2：`GET /api/greeting` 返回默认 `Hello, World!`
- 用例 3：响应中包含数值类型 `timestamp`
- 用例 4：前端调用后正确展示问候语
- 用例 5：`/api/health` 仍返回 `{ "status": "ok" }`

## 3. 测试数据

- 无需额外夹具。

## 4. 执行命令

- 后端手工验证：
  - `curl "http://localhost:8080/api/greeting?name=Tom"`
  - `curl "http://localhost:8080/api/greeting"`
- 前端验证：
  - `cd frontend && npm run dev`

## 5. 验收标准

- 用例矩阵全部通过。
- 响应结构保持稳定。
- 健康检查接口无回归。

## 6. 证据

- Curl 输出结果
- 页面展示截图
