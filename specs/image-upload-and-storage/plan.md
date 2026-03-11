---
title: 图片上传并保存技术方案
feature: image-upload-and-storage
status: draft
owners:
  - Codex
created: 2026-03-11
updated: 2026-03-11
spec: specs/image-upload-and-storage/spec.md
---

# 图片上传并保存技术方案

## 1. 技术上下文总结

### 1.1 固定技术选型

- 后端语言与框架：Python + FastAPI
- 前端语言与框架：Vue 3 + Vite + TypeScript
- 代码管理：GitHub
- Markdown 输出处理：不引入第三方 Markdown 处理库，保持原生字符串和标准渲染能力
- 数据存储：首版不引入数据库，所有页面数据通过后端 API 实时读取
- 文件存储：首版使用本地文件系统，保存到 `frontend/public/image/<slug>/`

### 1.2 当前仓库现实

- 后端已具备 FastAPI 应用入口、统一错误处理器、图片分析相关路由与测试。
- 前端已具备 Vue Router、Axios HTTP 客户端和一个现有图片分析页面。
- 本功能应在现有项目内增量实现，不新建独立子项目，不引入数据库，不引入新的状态管理库。

### 1.3 目标产物

本次实现将交付以下能力：

- 图片上传页面
- 简称文件夹列表页面
- 文件夹详情页面
- 上传、列表、删除相关后端 API
- 本地文件系统存储实现
- 面向未来 OSS 替换的存储服务边界

## 2. 合宪性审查

以下审查基于 [constitution.md](/Users/admin/myself/magic-partner/constitution.md) 当前内容逐条执行。

### 2.1 第一条：简单性原则

#### 1.1 YAGNI

- 符合。
- 方案仅实现 `spec.md` 中已确认的能力：上传、覆盖确认、列表、预览、删除。
- 明确不做：搜索、登录、数据库元信息管理、OSS 集成、复杂权限系统。

#### 1.2 框架优先

- 符合。
- 后端仅使用 FastAPI 原生路由、`UploadFile`、Pydantic、异常处理机制，不新增文件上传框架。
- 前端仅使用 Vue 3、Vue Router、Axios 和现有 Vite 能力，不新增 UI 框架或复杂状态方案。

#### 1.3 反过度工程

- 符合，但有一处必要抽象。
- 不引入 repository、DDD 分层或消息队列。
- 仅抽取一个最小“存储服务边界”，目的是隔离本地文件系统与未来 OSS，实现复杂度可控且直接服务于规格中的“存储可替换”要求。

### 2.2 第二条：测试先行铁律

#### 2.1 TDD 循环

- 符合。
- 实施顺序必须为：
  1. 先写后端失败测试
  2. 实现本地存储服务与 API
  3. 再写前端失败测试
  4. 实现上传页、列表页和删除交互
  5. 最后整理与重构

#### 2.2 表格驱动

- 符合。
- 后端校验类测试将采用表格驱动覆盖简称非法、格式非法、大小超限、数量超限、删除目标不存在、冲突确认等分支。
- 前端校验函数与错误映射也采用表格驱动。

#### 2.3 拒绝无意义 Mock

- 符合。
- 后端优先使用真实 FastAPI `TestClient` 和真实临时目录执行集成测试。
- 前端优先测试真实组件行为与 API 客户端交互，不用脱离上下文的假数据拼装业务状态。

### 2.3 第三条：明确性原则

#### 3.1 错误处理

- 符合。
- 后端将为所有失败路径返回稳定错误结构与错误码。
- 前端所有异步请求使用 `try/catch` 处理，区分可恢复错误与系统错误。
- 覆盖确认采用显式 API 响应状态，不通过模糊文案或隐式 200 结果表达。

#### 3.2 无隐式全局状态

- 符合。
- 首版不引入全局上传状态。
- 页面状态保留在各自视图组件内部，通过路由参数驱动当前文件夹视图。
- 若后续状态复杂度增加，再评估 Pinia；本期不需要。

### 2.4 包内聚检查

- 符合用户特别强调的“包内聚”要求。
- 后端路由只负责 HTTP 协议适配，不负责文件系统细节。
- 存储相关逻辑集中到 `backend/app/services/image_storage/`。
- 前端上传、列表、删除的领域类型、校验和请求适配集中到 `frontend/src/features/image-library/` 与 `frontend/src/api/`。
- 视图层仅编排交互，不承载文件名冲突判断、路径拼接等领域逻辑。

## 3. 实现总览

### 3.1 核心设计决策

1. 以后端为唯一图片管理入口。
2. 本地文件系统实现只作为一个 `storage backend`，而不是暴露给前端的事实标准。
3. API 设计以“文件夹列表”和“文件夹内图片列表”为中心，而不是裸文件路径。
4. 上传接口分为两个行为阶段：
   - 预检查阶段：发现目录内冲突文件时返回“需要确认覆盖”
   - 确认提交阶段：前端带确认标记再次提交，后端执行覆盖写入
5. 同批上传内的重名在服务端自动重命名，不要求前端参与。

### 3.2 路由视图设计

- `/`：保留现有首页
- `/images`：简称文件夹列表页
- `/images/:slug`：某个简称目录的图片列表页
- 上传入口可放在 `/images` 页内，不单独拆新路由

## 4. 项目结构细化

### 4.1 后端结构

建议在现有结构上增加如下文件：

```text
backend/
  app/
    config.py
    errors.py
    main.py
    routes.py
    schemas.py
    services/
      image_storage/
        __init__.py
        models.py
        service.py
        local_storage.py
        validators.py
        naming.py
  tests/
    test_image_library_api.py
    test_image_storage_service.py
    fixtures/
      image_uploads/
```

#### 后端职责划分

- `routes.py`
  - 定义图片管理相关 HTTP 接口
  - 解析 `multipart/form-data`、路径参数、查询参数
  - 将异常转换为统一 API 错误响应
- `schemas.py`
  - 定义请求响应的 Pydantic 模型
  - 仅表达 API 边界，不放文件系统逻辑
- `services/image_storage/models.py`
  - 定义领域层数据结构，如 `FolderSummary`、`StoredImage`、`UploadPlan`
- `services/image_storage/validators.py`
  - 校验简称、文件数量、格式、大小
- `services/image_storage/naming.py`
  - 处理批次内自动重命名规则
- `services/image_storage/local_storage.py`
  - 实现与本地文件系统交互的读写删逻辑
- `services/image_storage/service.py`
  - 编排上传、冲突检测、列表、删除、回滚

#### 依赖方向

- `routes.py` -> `schemas.py`, `services/image_storage/service.py`
- `service.py` -> `models.py`, `validators.py`, `naming.py`, `local_storage.py`
- `local_storage.py` 不依赖 FastAPI
- `validators.py` 和 `naming.py` 不依赖 HTTP 层

### 4.2 前端结构

建议在现有结构上增加如下文件：

```text
frontend/
  src/
    api/
      imageLibrary.ts
    features/
      image-library/
        types.ts
        validation.ts
        validation.test.ts
        upload-state.ts
    views/
      image-library/
        ImageLibraryView.vue
        ImageFolderView.vue
    router/
      index.ts
```

#### 前端职责划分

- `src/api/imageLibrary.ts`
  - 封装图片管理相关 API 请求
  - 统一处理请求参数拼装和响应类型
- `src/features/image-library/types.ts`
  - 定义文件夹列表项、图片列表项、错误码、上传响应类型
- `src/features/image-library/validation.ts`
  - 前端基础校验：简称、文件数、文件格式、文件大小
  - 仅做用户体验层预校验，最终规则以后端为准
- `src/features/image-library/upload-state.ts`
  - 放置当前功能私有的状态转换辅助函数
  - 不引入全局 store，只为组件内逻辑去重
- `ImageLibraryView.vue`
  - 承载上传表单、文件夹列表、删除文件夹入口
- `ImageFolderView.vue`
  - 展示某个简称目录下的图片缩略图列表与删除单张操作

#### 依赖方向

- View -> `src/api/imageLibrary.ts`
- View -> `features/image-library/types.ts`, `validation.ts`
- `src/api/imageLibrary.ts` -> `src/api/http.ts`
- 不允许 View 直接拼接本地磁盘路径

## 5. 存储设计

### 5.1 存储根目录

- 存储根目录：`frontend/public/image`
- 每个简称目录：`frontend/public/image/<slug>`
- 这里的 `<slug>` 实际使用用户输入的合法简称，不单独生成随机 ID

### 5.2 本地存储接口抽象

首版不引入正式抽象基类，但在服务层固定一组可替换方法：

- `list_folders()`
- `list_images(folder_slug)`
- `plan_upload(folder_slug, files)`
- `commit_upload(plan, overwrite_confirmed)`
- `delete_image(folder_slug, file_name)`
- `delete_folder(folder_slug)`

这样未来切 OSS 时，只需替换底层实现，不破坏路由层和响应结构。

### 5.3 文件命名规则

- 批次内文件重名：
  - `a.png`
  - `a(1).png`
  - `a(2).png`
- 与目录内现有文件重名：
  - 首次上传请求仅返回冲突清单
  - 前端确认后，再次提交相同文件与 `overwrite=true`

### 5.4 一致性策略

- 上传前先完成全部校验，任何校验失败都不落盘。
- 对于需要写入的文件，先生成执行计划，再逐个写入。
- 若写入过程中发生异常，删除本批已成功写入的新文件，保持批次一致性。
- 覆盖旧文件时，首版采用“先备份旧文件到临时路径，再替换，失败则恢复”的保守策略。

## 6. 接口设计

### 6.1 错误响应统一格式

沿用现有后端错误风格，统一返回：

```json
{
  "request_id": "req_xxx",
  "error": {
    "code": "IMAGE_FOLDER_INVALID",
    "message": "图片简称仅允许中文、英文、数字、中划线和下划线"
  }
}
```

### 6.2 错误码建议

- `IMAGE_FOLDER_REQUIRED`
- `IMAGE_FOLDER_INVALID`
- `IMAGE_BATCH_LIMIT_EXCEEDED`
- `UNSUPPORTED_IMAGE_TYPE`
- `INVALID_IMAGE_SIZE`
- `OVERWRITE_CONFIRMATION_REQUIRED`
- `IMAGE_FOLDER_NOT_FOUND`
- `IMAGE_NOT_FOUND`
- `FILE_STORAGE_WRITE_FAILED`
- `FILE_STORAGE_DELETE_FAILED`
- `INVALID_REQUEST`

### 6.3 上传图片

`POST /api/images`

请求类型：`multipart/form-data`

表单字段：

- `folder_slug`: string
- `overwrite`: boolean，可选，默认 `false`
- `images`: File，多文件

成功响应 `200`：

```json
{
  "request_id": "req_xxx",
  "folder": {
    "slug": "素材A",
    "image_count": 3
  },
  "saved_files": [
    {
      "file_name": "a.png",
      "preview_url": "/image/素材A/a.png",
      "updated_at": 1760000000000
    }
  ],
  "created_at": 1760000000000
}
```

冲突待确认响应 `409`：

```json
{
  "request_id": "req_xxx",
  "error": {
    "code": "OVERWRITE_CONFIRMATION_REQUIRED",
    "message": "存在同名文件，确认后将覆盖"
  },
  "conflicts": [
    "a.png",
    "b.png"
  ]
}
```

设计说明：

- `409` 明确表示资源冲突，前端可据此弹出统一确认框。
- 若用户取消确认，不再发起第二次请求。

### 6.4 获取文件夹列表

`GET /api/image-folders`

成功响应 `200`：

```json
{
  "folders": [
    {
      "slug": "素材A",
      "image_count": 3,
      "cover_url": "/image/素材A/a.png",
      "updated_at": 1760000000000
    }
  ]
}
```

排序规则：按 `updated_at` 倒序。

### 6.5 获取某个文件夹下的图片列表

`GET /api/image-folders/{folder_slug}`

成功响应 `200`：

```json
{
  "folder": {
    "slug": "素材A",
    "image_count": 3,
    "updated_at": 1760000000000
  },
  "images": [
    {
      "file_name": "a.png",
      "preview_url": "/image/素材A/a.png",
      "updated_at": 1760000000000
    }
  ]
}
```

异常：

- 不存在文件夹时返回 `404`

### 6.6 删除单张图片

`DELETE /api/image-folders/{folder_slug}/images/{file_name}`

成功响应 `200`：

```json
{
  "request_id": "req_xxx",
  "deleted": true,
  "folder_deleted": false
}
```

说明：

- 当删除后目录为空，`folder_deleted` 返回 `true`

### 6.7 删除整个文件夹

`DELETE /api/image-folders/{folder_slug}`

成功响应 `200`：

```json
{
  "request_id": "req_xxx",
  "deleted": true
}
```

## 7. 前端交互方案

### 7.1 上传流程

1. 用户输入简称并选择 1-10 张图片。
2. 前端执行基础校验：
   - 简称非空
   - 简称字符合法
   - 文件数不超过 10
   - 每张文件格式与大小合法
3. 前端调用 `POST /api/images`
4. 若返回 `409 OVERWRITE_CONFIRMATION_REQUIRED`，弹出统一确认框
5. 用户确认后，前端带 `overwrite=true` 再次提交
6. 成功后跳转到 `/images/:slug`

### 7.2 文件夹列表流程

1. 页面进入 `/images` 时请求文件夹列表
2. 渲染卡片列表，展示封面、简称、数量、更新时间
3. 点击文件夹进入 `/images/:slug`
4. 点击“删除文件夹”时先确认，再调用删除接口

### 7.3 文件夹详情流程

1. 页面进入 `/images/:slug` 时请求详情接口
2. 渲染缩略图列表
3. 点击单图删除时先确认，再调用删除接口
4. 删除成功后刷新当前目录列表
5. 若目录因最后一张图被删空，前端返回 `/images`

## 8. 测试策略

### 8.1 后端测试

新增：

- `backend/tests/test_image_storage_service.py`
- `backend/tests/test_image_library_api.py`

覆盖点：

- 合法上传单张成功
- 合法上传多张成功
- 文件夹不存在时自动创建
- 批次内同名自动重命名
- 目录内冲突返回 `409`
- 确认覆盖后成功写入
- 非法简称
- 非法文件格式
- 文件超限
- 超过 10 张
- 批量混入非法文件导致整批失败
- 删除单张成功
- 删除最后一张后目录自动删除
- 删除整个文件夹成功
- 删除不存在资源返回 `404`
- 写入失败时回滚

方法要求：

- 优先使用真实临时目录
- 表格驱动覆盖校验场景
- 每个 API 变更至少断言状态码与响应体

### 8.2 前端测试

新增：

- `frontend/src/features/image-library/validation.test.ts`
- 视图组件行为测试，可按实际组件结构补充

覆盖点：

- 简称校验
- 文件数量校验
- 文件格式与大小校验
- `409` 冲突时的确认流程
- 上传成功后跳转
- 删除成功后列表刷新

## 9. 实施顺序

1. 先写后端存储服务测试
2. 实现后端校验、命名和本地存储服务
3. 写后端 API 测试
4. 实现图片管理接口与响应模型
5. 写前端校验测试
6. 实现前端 API 客户端和校验函数
7. 实现文件夹列表页与详情页
8. 接入上传、覆盖确认、删除确认
9. 运行后端 `pytest -q`
10. 运行前端 `vitest` 与 `build`

## 10. 风险与约束

### 10.1 路径写入风险

- 当前将文件写入 `frontend/public/image`，适合本地与当前阶段部署，但不适合作为长期生产持久化方案。
- 通过存储服务边界控制此风险，后续切 OSS 时不改前端协议。

### 10.2 文件名与路径安全

- 必须防止路径穿越。
- `folder_slug` 和 `file_name` 均不得被直接拼接后信任使用。
- 服务层应始终基于受控根目录和标准化路径执行访问。

### 10.3 中文路径兼容性

- 规格允许中文简称，前后端需要正确处理 URL 编码与文件系统路径。
- 前端路由参数要使用编码后的 URL，后端按解码后的值做合法性校验。

## 11. 方案结论

本方案在不引入数据库、不引入额外基础设施的前提下，满足规格中对上传、分组、预览、删除、覆盖确认和可替换存储的全部要求。它遵循项目宪法中的简单性、测试先行和显式错误处理原则，同时把抽象控制在“存储服务边界”这一最小必要范围内，既支持当前本地落盘，也为未来迁移到 OSS 保留了稳定接口面。
