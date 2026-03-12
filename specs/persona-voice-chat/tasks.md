# 任务清单（`tasks.md`）

## 使用说明

- 本文件基于 `spec.md` 和 `plan.md` 生成
- 任务必须能直接执行，避免“完善一下”“处理相关逻辑”这类空泛描述
- 所有任务都要写真实文件路径
- 默认遵循 `Red -> Green -> Refactor`
- 任务按用户故事分组，保证每个故事可独立交付、独立验证

## 任务格式

`- [ ] Txxx [阶段] [故事] 任务描述（文件路径）`

示例：

`- [ ] T001 [Red] [US1] 为人物创建成功路径补充后端 API 测试（backend/tests/test_persona_api.py）`

字段说明：

- `Txxx`：任务编号，按执行顺序递增
- `[阶段]`：`Red` / `Green` / `Refactor`
- `[故事]`：`Setup` / `Foundation` / `US1` / `US2` / `US3`

## 1. 前置说明

- **功能名称**：人物声音采集与语音聊天
- **规格目录**：`specs/persona-voice-chat/`
- **依赖文件**：
  - `spec.md`
  - `plan.md`
- **是否包含后端改动**：是
- **是否包含前端改动**：是

## 2. Setup

只放最小必要的准备工作；没有就写 `N/A`，不要凑数。

- [ ] T001 [Red] [Setup] 新建人物与聊天相关测试文件骨架（`backend/tests/test_persona_api.py`、`backend/tests/test_persona_service.py`、`backend/tests/test_chat_api.py`、`backend/tests/test_chat_service.py`、`frontend/src/views/persona/PersonaLibraryView.test.ts`、`frontend/src/views/persona/PersonaChatView.test.ts`、`frontend/src/features/persona/validation.test.ts`）
- [ ] T002 [Red] [Setup] 准备人物、本地样本文件和聊天数据的测试夹具策略说明并写入测试辅助代码（`backend/tests/test_persona_service.py`、`backend/tests/test_chat_service.py`）

## 3. Foundation

只放会阻塞多个用户故事的基础任务。若没有共享阻塞项，可写 `N/A`。

- [ ] T003 [Red] [Foundation] 为人物命名规则、样本就绪规则和错误码映射编写表格驱动失败测试（`backend/tests/test_persona_service.py`、`frontend/src/features/persona/validation.test.ts`）
- [ ] T004 [Red] [Foundation] 为统一错误响应、未配置模型供应商和文件写入失败场景补充失败测试（`backend/tests/test_persona_api.py`、`backend/tests/test_chat_api.py`）
- [ ] T005 [Green] [Foundation] 新增人物、样本、聊天相关基础 schema 与错误码常量（`backend/app/schemas.py`）
- [ ] T006 [Green] [Foundation] 新增人物与聊天基础服务目录及模型网关边界（`backend/app/services/persona/__init__.py`、`backend/app/services/persona/models.py`、`backend/app/services/chat/__init__.py`、`backend/app/services/chat/models.py`、`backend/app/services/chat/model_gateway.py`）
- [ ] T007 [Green] [Foundation] 扩展后端配置以支持人物存储根目录和模型供应商环境变量（`backend/app/config.py`）
- [ ] T008 [Refactor] [Foundation] 收敛人物模块和聊天模块共用的错误处理与时间戳/标识生成逻辑（`backend/app/errors.py`、`backend/app/services/request_ids.py`）

## 4. User Story 1 - 创建并准备可聊天人物（P1）

**目标**：完成首页入口、人物管理页、人物创建/重命名/删除、样本上传与试听、就绪状态展示。

**独立验证方式**：用户可以创建合法人物、上传或录制合法样本、查看样本统计和就绪状态、试听最新样本、删除样本或人物；未满足条件的人物保持“未就绪”。

### Red

- [ ] T009 [Red] [US1] 为人物创建、列表、重命名、删除成功与失败路径编写后端 API 测试（`backend/tests/test_persona_api.py`）
- [ ] T010 [Red] [US1] 为人物命名校验、大小写重复校验和删除不存在人物场景补充服务测试（`backend/tests/test_persona_service.py`）
- [ ] T011 [Red] [US1] 为样本批量上传原子性、格式/时长校验、样本上限和就绪状态计算编写后端测试（`backend/tests/test_persona_api.py`、`backend/tests/test_persona_service.py`）
- [ ] T012 [Red] [US1] 为人物管理页初始渲染、创建人物、展示就绪状态和错误文案编写前端测试（`frontend/src/views/persona/PersonaLibraryView.test.ts`）
- [ ] T013 [Red] [US1] 为人物名和样本上传前端校验编写表格驱动测试（`frontend/src/features/persona/validation.test.ts`）

### Green

- [ ] T014 [Green] [US1] 实现人物领域模型、本地 JSON 元数据读写和人物 CRUD 服务（`backend/app/services/persona/models.py`、`backend/app/services/persona/service.py`、`backend/app/services/persona/storage.py`）
- [ ] T015 [Green] [US1] 实现样本校验、转存为 `wav`、样本统计与就绪状态计算（`backend/app/services/persona/sample_service.py`、`backend/app/services/persona/audio.py`）
- [ ] T016 [Green] [US1] 在后端新增人物与样本相关 API 路由和响应模型（`backend/app/routes.py`、`backend/app/schemas.py`）
- [ ] T017 [Green] [US1] 新增人物管理 API 客户端与前端校验逻辑（`frontend/src/api/personas.ts`、`frontend/src/features/persona/validation.ts`）
- [ ] T018 [Green] [US1] 新增人物管理页并接入人物创建、列表、样本上传、试听、删除交互（`frontend/src/views/persona/PersonaLibraryView.vue`）
- [ ] T019 [Green] [US1] 更新首页和路由，增加人物管理页与聊天页入口（`frontend/src/views/HomeView.vue`、`frontend/src/router/index.ts`）

### Refactor

- [ ] T020 [Refactor] [US1] 清理人物与样本服务中的重复校验逻辑并保持测试通过（`backend/app/services/persona/service.py`、`backend/app/services/persona/sample_service.py`）
- [ ] T021 [Refactor] [US1] 收敛人物管理页的错误提示、空态和上传状态展示（`frontend/src/views/persona/PersonaLibraryView.vue`）

## 5. User Story 2 - 调整人物设定并维护人物状态（P2）

**目标**：支持编辑人物设定、保存后生效、重置人物状态并清空设定/聊天记录/共享上下文。

**独立验证方式**：用户能更新人物设定并看到持久化结果，执行“重置人物状态”后该人物恢复为无设定、无聊天记录、无共享上下文的状态。

### Red

- [ ] T022 [Red] [US2] 为人物设定更新和重置人物状态的后端 API 行为编写失败测试（`backend/tests/test_persona_api.py`、`backend/tests/test_chat_api.py`）
- [ ] T023 [Red] [US2] 为重置后清空设定、聊天记录和上下文的服务行为编写测试（`backend/tests/test_persona_service.py`、`backend/tests/test_chat_service.py`）
- [ ] T024 [Red] [US2] 为人物设定表单保存和“重置人物状态”确认流程编写前端测试（`frontend/src/views/persona/PersonaLibraryView.test.ts`）

### Green

- [ ] T025 [Green] [US2] 扩展人物服务以支持设定字段读写、重命名同步更新和状态重置（`backend/app/services/persona/service.py`、`backend/app/services/persona/storage.py`）
- [ ] T026 [Green] [US2] 扩展聊天服务以支持按人物清空聊天记录和共享上下文（`backend/app/services/chat/service.py`、`backend/app/services/chat/storage.py`）
- [ ] T027 [Green] [US2] 新增人物设定更新与重置 API（`backend/app/routes.py`、`backend/app/schemas.py`）
- [ ] T028 [Green] [US2] 在人物管理 API 客户端中加入设定保存与状态重置调用（`frontend/src/api/personas.ts`）
- [ ] T029 [Green] [US2] 在人物管理页实现设定编辑面板、保存交互和状态重置操作（`frontend/src/views/persona/PersonaLibraryView.vue`）

### Refactor

- [ ] T030 [Refactor] [US2] 收敛人物设定默认值和重置逻辑，避免人物服务与聊天服务重复定义（`backend/app/services/persona/models.py`、`backend/app/services/chat/service.py`）
- [ ] T031 [Refactor] [US2] 整理前端设定表单状态和确认弹窗逻辑并保持 US1、US2 测试通过（`frontend/src/views/persona/PersonaLibraryView.vue`）

## 6. User Story 3 - 与人物进行文字或语音聊天（P3）

**目标**：支持选择已就绪人物，通过文字或语音输入聊天，返回文本与真实音色语音回复，并在音色失败时明确提示。

**独立验证方式**：用户可以选择已就绪人物完成一次文字聊天和一次语音聊天；系统保留最近 10 轮记录与上下文；声音克隆失败时展示提示而不是伪造音频。

### Red

- [ ] T032 [Red] [US3] 为未就绪人物禁止聊天、文字聊天成功、语音识别失败和声音克隆失败提示编写后端 API 测试（`backend/tests/test_chat_api.py`）
- [ ] T033 [Red] [US3] 为 10 轮上下文窗口、10 轮聊天记录保留和消息播放信息写入编写服务测试（`backend/tests/test_chat_service.py`）
- [ ] T034 [Red] [US3] 为聊天页人物选择、文字发送、语音输入阶段提示和声音克隆失败提示编写前端测试（`frontend/src/views/persona/PersonaChatView.test.ts`）

### Green

- [ ] T035 [Green] [US3] 实现聊天记录与上下文本地存储服务（`backend/app/services/chat/storage.py`、`backend/app/services/chat/service.py`）
- [ ] T036 [Green] [US3] 实现模型网关接口，接入 ASR、LLM、声音克隆调用与未配置/失败处理（`backend/app/services/chat/model_gateway.py`）
- [ ] T037 [Green] [US3] 实现聊天 API、处理中阶段状态和稳定错误码返回（`backend/app/routes.py`、`backend/app/schemas.py`）
- [ ] T038 [Green] [US3] 新增聊天 API 客户端（`frontend/src/api/chat.ts`）
- [ ] T039 [Green] [US3] 新增聊天页并实现人物选择、文字输入、语音输入、消息流和阶段状态展示（`frontend/src/views/persona/PersonaChatView.vue`）
- [ ] T040 [Green] [US3] 更新首页入口文案，使首页明确说明当前产品定位为人物声音采集与语音聊天原型（`frontend/src/views/HomeView.vue`）

### Refactor

- [ ] T041 [Refactor] [US3] 收敛聊天错误码、阶段状态和语音播放信息结构，保持后端测试全部通过（`backend/app/services/chat/service.py`、`backend/app/schemas.py`）
- [ ] T042 [Refactor] [US3] 整理聊天页的本地状态、错误展示和阶段提示逻辑，保持前端测试全部通过（`frontend/src/views/persona/PersonaChatView.vue`）

## 7. 收尾与验证

- [ ] T043 [Refactor] [Setup] 运行后端测试（`cd backend && .venv/bin/python -m pytest -q`）
- [ ] T044 [Refactor] [Setup] 运行前端测试（`cd frontend && npm run test`）
- [ ] T045 [Refactor] [Setup] 运行前端构建验证（`cd frontend && npm run build`）
- [ ] T046 [Refactor] [Setup] 根据最终实现回写规格与计划中的差异、补充完成状态（`specs/persona-voice-chat/spec.md`、`specs/persona-voice-chat/plan.md`、`specs/persona-voice-chat/tasks.md`）

## 8. 编写规则检查

生成任务后，逐项检查：

- [ ] 每个用户故事都有自己的 Red/Green/Refactor 任务
- [ ] 没有任何实现任务先于对应失败测试
- [ ] 每条任务都指向真实文件路径
- [ ] 没有超出 `spec.md` 范围的任务
- [ ] 关键错误路径和显式错误处理已进入任务清单
- [ ] 任务顺序支持“先交付 P1，再决定是否继续”
