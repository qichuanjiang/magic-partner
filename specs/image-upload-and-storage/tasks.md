---
title: 图片上传并保存任务拆解
feature: image-upload-and-storage
status: draft
owners:
  - Codex
created: 2026-03-12
updated: 2026-03-12
spec: specs/image-upload-and-storage/spec.md
plan: specs/image-upload-and-storage/plan.md
---

# 图片上传并保存任务拆解

## 任务拆解原则

- 所有任务遵循 `constitution.md` 的 Test-First Imperative，先测试、后实现。
- 每个任务只允许聚焦一个主文件的创建或修改。
- 依赖关系以任务编号表示，执行时应满足依赖后再开始当前任务。
- 若某个测试任务依赖尚不存在的接口或类型，允许先写出失败测试或占位导入，后续由实现任务补齐。

## 执行顺序总览

1. 先完成后端测试任务 `T01-T02`
2. 再完成后端实现任务 `T03-T10`
3. 再完成前端测试任务 `T11-T13`
4. 最后完成前端实现任务 `T14-T20`

## 后端测试任务

### T01

- 主文件：`backend/tests/test_image_storage_service.py`
- 类型：测试
- 依赖：无
- 目标：新增存储服务级失败测试，覆盖简称校验、文件数量限制、格式限制、大小限制、批次内同名自动重命名、目录内冲突需确认、删除单图、删除最后一张后自动删目录、删除整个文件夹、写入失败回滚。
- 完成标准：测试使用 `pytest` 和真实临时目录；校验类场景采用表格驱动；当前应因实现缺失而失败。

### T02

- 主文件：`backend/tests/test_image_library_api.py`
- 类型：测试
- 依赖：T01
- 目标：新增 API 失败测试，覆盖 `POST /api/images`、`GET /api/image-folders`、`GET /api/image-folders/{folder_slug}`、`DELETE /api/image-folders/{folder_slug}/images/{file_name}`、`DELETE /api/image-folders/{folder_slug}` 的成功路径与关键错误路径。
- 完成标准：断言状态码、响应体结构、错误码；包含 `409 OVERWRITE_CONFIRMATION_REQUIRED` 场景；当前应因接口未实现而失败。

## 后端实现任务

### T03

- 主文件：`backend/app/services/image_storage/models.py`
- 类型：实现
- 依赖：T01
- 目标：定义图片存储领域模型，例如 `StoredImage`、`FolderSummary`、`UploadCandidate`、`UploadPlan`、`UploadConflict`、`DeleteImageResult`。
- 完成标准：模型字段足以支撑服务层、路由层和测试中的数据表达；不依赖 FastAPI。

### T04

- 主文件：`backend/app/services/image_storage/validators.py`
- 类型：实现
- 依赖：T01, T03
- 目标：实现简称、文件数量、文件类型、文件大小的显式校验函数，并返回稳定错误。
- 完成标准：覆盖 `IMAGE_FOLDER_REQUIRED`、`IMAGE_FOLDER_INVALID`、`IMAGE_BATCH_LIMIT_EXCEEDED`、`UNSUPPORTED_IMAGE_TYPE`、`INVALID_IMAGE_SIZE` 等错误语义。

### T05

- 主文件：`backend/app/services/image_storage/naming.py`
- 类型：实现
- 依赖：T01, T03
- 目标：实现批次内同名文件自动重命名规则，产出 `a.png`、`a(1).png`、`a(2).png` 形式的最终文件名。
- 完成标准：保持扩展名不变；重名规则稳定可预测；不处理目录内现有文件覆盖逻辑。

### T06

- 主文件：`backend/app/services/image_storage/local_storage.py`
- 类型：实现
- 依赖：T01, T03, T04, T05
- 目标：实现本地文件系统读写删能力，包括目录创建、文件枚举、封面图选择、图片列表排序、删除单图、删除文件夹、空目录清理、写入回滚辅助。
- 完成标准：根目录受控在 `frontend/public/image`；防止路径穿越；不依赖 FastAPI 请求对象。

### T07

- 主文件：`backend/app/services/image_storage/service.py`
- 类型：实现
- 依赖：T01, T03, T04, T05, T06
- 目标：实现图片管理服务编排逻辑，包括上传预检查、目录内冲突检测、确认覆盖后的提交、列表查询、删除结果汇总。
- 完成标准：整批失败不落盘；覆盖前返回冲突信息；写入失败时可回滚；服务输出可直接供 API 层映射。

### T08

- 主文件：`backend/app/config.py`
- 类型：实现
- 依赖：T06
- 目标：补充图片管理相关配置常量，例如存储根目录、允许的图片类型、单文件大小上限、单批次文件数上限。
- 完成标准：配置可被图片管理服务与现有图片分析逻辑复用；不引入数据库或环境变量复杂配置。

### T09

- 主文件：`backend/app/schemas.py`
- 类型：实现
- 依赖：T02, T03, T07
- 目标：新增图片上传、文件夹列表、文件夹详情、删除结果、冲突响应相关的 Pydantic 响应模型。
- 完成标准：响应模型能表达成功结果与错误结果；字段命名与 `plan.md` 接口设计保持一致。

### T10

- 主文件：`backend/app/routes.py`
- 类型：实现
- 依赖：T02, T07, T08, T09
- 目标：接入图片管理 API 路由，完成请求解析、服务调用、状态码映射和统一错误响应。
- 完成标准：T02 通过；上传接口支持 `multipart/form-data` 多文件、`overwrite` 标记和 `folder_slug`；列表和删除接口可用。

## 前端测试任务

### T11

- 主文件：`frontend/src/features/image-library/validation.test.ts`
- 类型：测试
- 依赖：T10
- 目标：新增前端表格驱动校验测试，覆盖简称为空、纯空格、非法字符、文件数量超限、文件格式非法、文件大小超限等分支。
- 完成标准：测试描述清晰；当前应因校验实现缺失而失败。

### T12

- 主文件：`frontend/src/views/image-library/ImageLibraryView.test.ts`
- 类型：测试
- 依赖：T10
- 目标：新增图片库首页视图测试，覆盖上传表单渲染、文件夹列表加载、`409` 覆盖确认流程、上传成功后跳转、删除文件夹确认与刷新。
- 完成标准：测试围绕用户行为和页面结果，而不是组件内部实现；当前应因视图未实现而失败。

### T13

- 主文件：`frontend/src/views/image-library/ImageFolderView.test.ts`
- 类型：测试
- 依赖：T10
- 目标：新增文件夹详情页测试，覆盖图片缩略图列表渲染、按更新时间排序展示、删除单图确认、删除最后一张后返回列表页。
- 完成标准：测试围绕路由参数和页面行为；当前应因视图未实现而失败。

## 前端实现任务

### T14

- 主文件：`frontend/src/features/image-library/types.ts`
- 类型：实现
- 依赖：T11, T12, T13
- 目标：定义前端图片库领域类型，包括文件夹项、图片项、上传成功响应、冲突响应、删除响应、错误码联合类型。
- 完成标准：类型命名清晰，能支撑 API 客户端和视图组件；不包含业务逻辑。

### T15

- 主文件：`frontend/src/features/image-library/validation.ts`
- 类型：实现
- 依赖：T11, T14
- 目标：实现前端预校验函数与错误码到用户文案的映射。
- 完成标准：T11 通过；仅承担用户体验层预检查，不替代后端校验。

### T16

- 主文件：`frontend/src/api/imageLibrary.ts`
- 类型：实现
- 依赖：T10, T12, T13, T14
- 目标：实现图片管理 API 客户端，包括上传、获取文件夹列表、获取文件夹详情、删除单图、删除文件夹。
- 完成标准：统一使用 `frontend/src/api/http.ts`；能解析 `409 OVERWRITE_CONFIRMATION_REQUIRED`；请求参数拼装正确。

### T17

- 主文件：`frontend/src/features/image-library/upload-state.ts`
- 类型：实现
- 依赖：T12, T14, T15, T16
- 目标：实现图片上传交互所需的私有状态辅助函数，例如待上传文件归一化、冲突确认后的二次提交参数复用、成功后的页面状态清理。
- 完成标准：仅封装当前 feature 私有状态转换；不引入全局 store。

### T18

- 主文件：`frontend/src/views/image-library/ImageLibraryView.vue`
- 类型：实现
- 依赖：T12, T14, T15, T16, T17
- 目标：实现图片库首页，包含简称输入、多图选择、上传按钮、约束提示、文件夹列表、删除文件夹操作、覆盖确认交互。
- 完成标准：T12 通过；上传成功后跳转到对应 `/images/:slug`；空状态、错误状态和加载状态显式处理。

### T19

- 主文件：`frontend/src/views/image-library/ImageFolderView.vue`
- 类型：实现
- 依赖：T13, T14, T16
- 目标：实现文件夹详情页，展示缩略图、文件名、更新时间，并支持删除单图和删除后跳转处理。
- 完成标准：T13 通过；页面不直接拼接磁盘路径，只消费 API 返回的 `preview_url`。

### T20

- 主文件：`frontend/src/router/index.ts`
- 类型：实现
- 依赖：T18, T19
- 目标：注册 `/images` 和 `/images/:slug` 路由，并保持现有首页路由可用。
- 完成标准：新页面可通过路由访问；路由命名与组件导入清晰；不引入无关路由。

## 收尾检查

- 完成 `T01-T20` 后，后端应执行 `cd backend && .venv/bin/python -m pytest -q`
- 完成 `T01-T20` 后，前端应执行 `cd frontend && npm run build`
- 若新增了前端视图测试，还应执行 `cd frontend && npm run test -- --run`

## 任务依赖图摘要

- 后端主链路：`T01 -> T03 -> T04/T05 -> T06 -> T07 -> T08/T09 -> T10`
- API 测试链路：`T01 -> T02 -> T09 -> T10`
- 前端校验链路：`T10 -> T11 -> T14 -> T15`
- 前端首页链路：`T10 -> T12 -> T14 -> T16 -> T17 -> T18`
- 前端详情链路：`T10 -> T13 -> T14 -> T16 -> T19`
- 路由接入链路：`T18 + T19 -> T20`
