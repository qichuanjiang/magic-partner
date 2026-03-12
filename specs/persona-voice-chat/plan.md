# 实施计划（`plan.md`）

## 基本信息

- **功能名称**：人物声音采集与语音聊天
- **规格文件**：`specs/persona-voice-chat/spec.md`
- **计划文件**：`specs/persona-voice-chat/plan.md`
- **创建日期**：2026-03-12
- **负责人**：Codex

## 1. 方案摘要

本次实现覆盖 `US1` 到 `US3` 的完整原型链路，但交付顺序严格按 `P1 -> P2 -> P3` 推进。后端沿用现有 FastAPI 路由 + 服务层模式，在 `backend/app/services/` 下新增人物、样本、聊天和模型编排相关服务，并继续使用本地文件系统与 JSON 元数据存储。前端沿用现有 Vue 3 + vue-router + axios 结构，在现有 `views` 与 `api` 目录中补充人物管理页、聊天页和相关 API 客户端。测试上遵循 Red-Green-Refactor，优先补后端 API/服务失败测试与前端关键交互测试。声音克隆、ASR 和 LLM 的具体供应商尚未锁定，因此计划保留统一模型接入边界，把供应商选择列为实现风险而不是隐式决定。

## 2. 规格映射

把规格中的用户故事和需求映射到本次实现范围，避免“计划偷偷扩容”。

### 2.1 本次实现的用户故事

| 用户故事 | 是否本次实现 | 说明 |
| --- | --- | --- |
| US1 | 是 | 完成人物创建、命名校验、样本上传/录音、样本试听、就绪状态 |
| US2 | 是 | 完成人物设定编辑与“重置人物状态” |
| US3 | 是 | 完成文字/语音聊天、10 轮上下文、语音回复与音色失败提示 |

### 2.2 需求映射

| 需求编号 | 实现方式摘要 | 涉及文件/模块 |
| --- | --- | --- |
| FR-001 ~ FR-002 | 新增首页入口、人物管理页、聊天页和对应 API | `frontend/src/router/index.ts` `frontend/src/views/*` `backend/app/routes.py` |
| FR-003 ~ FR-020 | 在后端新增 `persona`、`voice_sample`、`persona_state` 服务与本地存储结构 | `backend/app/services/persona_*` |
| FR-021 ~ FR-037 | 新增聊天编排、ASR/LLM/voice clone 适配与聊天记录存储 | `backend/app/services/chat_*` `backend/app/services/model_*` |
| FR-038 ~ FR-040 | 删除人物及级联清理 | `backend/app/services/persona_service.py` |

## 3. 技术上下文

只填写与当前功能直接相关的内容。

| 项目 | 内容 |
| --- | --- |
| 后端语言/版本 | Python 3.x |
| 前端语言/版本 | TypeScript 5.x |
| 后端框架 | FastAPI 0.116.x |
| 前端框架 | Vue 3 + Vite 5 |
| 测试框架 | `pytest` / `vitest` |
| 存储 | 本地文件系统 + JSON 元数据 |
| 外部依赖 | ASR、LLM、声音克隆/TTS 提供方，当前未定 |
| 运行约束 | 本地原型优先，不引入数据库、对象存储、消息队列和复杂鉴权 |

## 4. 宪法对齐检查

本节是计划阶段的准入门槛。

### 4.1 简单性原则

- 是否存在可以删掉的抽象层：是。计划只保留必要的服务边界，不引入 repository、事件总线或额外状态管理层
- 是否完全基于现有目录结构实现：是。沿用 `backend/app/routes.py`、`backend/app/services/`、`frontend/src/api/`、`frontend/src/views/`
- 是否新增了不必要的第三方依赖：否。仅在模型供应商 SDK 或音频处理能力成为实现刚需时再最小化引入

### 4.2 测试先行铁律

- 先写的失败测试清单：人物命名校验、样本批量上传原子性、就绪规则、人物状态重置、未就绪人物禁止聊天、语音识别失败、声音克隆失败提示、人物删除级联清理
- 哪些测试是集成测试，哪些是单元测试：后端 API 行为用集成测试；命名/样本/聊天窗口等规则用服务单元测试；前端页面流程和错误展示用视图测试
- 哪些地方采用表格驱动测试：命名规则、样本格式/时长校验、错误码映射、就绪状态判定

### 4.3 明确性原则

- 需要显式处理的错误：命名非法/重复、文件格式非法、时长非法、超限、未就绪聊天、ASR 失败、LLM 失败、声音克隆失败、文件写入失败、删除对象不存在
- 前端失败态与后端错误响应如何对应：后端返回稳定错误码与消息，前端在 `api` 层映射为用户可展示文案并保留可恢复操作
- 是否引入新的共享状态，若引入为何合理：后端会新增按人物维度持久化的聊天记录与上下文，这是业务要求，不属于隐式全局状态

### 4.4 结论

- `PASS`
- 当前计划满足进入任务拆解阶段的条件，但模型供应商选型仍需在实现前确认

## 5. 目录与文件变更

只列出预计会改动的真实路径。

### 5.1 后端

- `backend/app/routes.py`
- `backend/app/schemas.py`
- `backend/app/config.py`
- `backend/app/services/request_ids.py`
- `backend/app/services/persona/`
- `backend/app/services/chat/`
- `backend/tests/test_persona_api.py`
- `backend/tests/test_persona_service.py`
- `backend/tests/test_chat_api.py`
- `backend/tests/test_chat_service.py`

### 5.2 前端

- `frontend/src/router/index.ts`
- `frontend/src/api/personas.ts`
- `frontend/src/api/chat.ts`
- `frontend/src/views/HomeView.vue`
- `frontend/src/views/persona/PersonaLibraryView.vue`
- `frontend/src/views/persona/PersonaLibraryView.test.ts`
- `frontend/src/views/persona/PersonaChatView.vue`
- `frontend/src/views/persona/PersonaChatView.test.ts`
- `frontend/src/features/persona/validation.ts`
- `frontend/src/features/persona/validation.test.ts`

### 5.3 规格与文档

- `specs/persona-voice-chat/spec.md`
- `specs/persona-voice-chat/plan.md`
- `specs/persona-voice-chat/tasks.md`

## 6. 设计决策

本节回答“为什么这样做”。

### 6.1 数据与领域对象

- 新增/修改哪些对象：`Persona`、`VoiceSample`、`ChatMessage`、`PersonaContext`、`PersonaSettings`
- 哪些字段是关键字段：`persona_id`、`name`、样本统计、就绪状态、设定字段、消息时间戳、语音资源引用、错误状态
- 是否有兼容性影响：无历史兼容包袱；但需保持前端只依赖后端稳定业务结构，不能推断本地磁盘路径

### 6.2 后端设计

- API 路由：继续集中在 `backend/app/routes.py`，按 `/api/personas`、`/api/personas/{id}/samples`、`/api/personas/{id}/reset`、`/api/chat` 等路径组织
- 请求校验：使用 Pydantic/FastAPI 原生能力做请求模型与响应模型校验；文件上传额外在服务层做格式、时长和数量校验
- 响应模型：在 `backend/app/schemas.py` 新增人物列表、人物详情、样本、聊天响应和标准错误响应模型
- 错误处理：继续沿用 `APIError` 和统一异常处理器，为关键业务错误分配稳定错误码
- 服务边界：
  - `persona_service` 负责人物 CRUD、命名规则、设定保存、重置和删除
  - `sample_service` 负责音频校验、转存、样本统计和样本删除
  - `chat_service` 负责上下文窗口、聊天记录、消息编排
  - `model_gateway` 负责 ASR、LLM、声音克隆调用，隔离供应商差异

### 6.3 前端设计

- 页面或组件入口：在首页增加“人物管理”“语音聊天”入口；新增人物管理页与聊天页
- 数据流：页面组件调用 `src/api`，不直接接触第三方模型；局部状态保存在视图组件中
- 表单/交互状态：人物创建表单、设定编辑表单、录音/上传状态、聊天输入状态、处理中阶段状态都在页面本地管理
- 加载态、空态、失败态：
  - 人物列表为空时展示空状态
  - 上传/保存/聊天时展示加载态与阶段提示
  - 各失败场景显示明确错误，并保留重试或修复入口

### 6.4 配置设计

- 新增环境变量：`VOICE_CHAT_LLM_PROVIDER`、`VOICE_CHAT_ASR_PROVIDER`、`VOICE_CHAT_CLONE_PROVIDER` 及对应凭据
- 默认值：本地文件存储默认开启；模型供应商默认留空，未配置时相关接口返回明确不可用错误
- 本地开发与生产差异：当前仅规划本地原型；后续若进入生产，需要再定义存储与密钥管理策略

## 7. 测试策略

必须体现 Red-Green-Refactor。

### 7.1 Red：先写失败测试

- 后端失败测试：
  - 非法/重复人物名创建失败
  - 非法音频批量上传整体失败并回滚
  - 样本达到 3 段但总时长不足时仍未就绪
  - 未就绪人物聊天失败
  - 人物状态重置后设定、上下文、聊天记录被清空
  - 声音克隆失败时返回明确错误提示
  - 删除人物后资源被级联删除
- 前端失败测试：
  - 管理页拦截明显非法输入
  - 管理页展示后端错误码映射文案
  - 聊天页禁止选择未就绪人物
  - 聊天页展示“识别中 / 思考中 / 合成中”
  - 聊天页在声音克隆失败时展示提示而不是伪造播放音频

### 7.2 Green：最小实现

- 先满足哪些验收场景：先完成人物创建与样本上传，再完成人物设定与重置，最后完成文字/语音聊天
- 如何保证实现只覆盖规格范围：不引入登录、数据库、多用户隔离、审核、默认 TTS 回退或复杂运维设施

### 7.3 Refactor：整理实现

- 哪些代码会在通过测试后再收敛：人物与样本存储逻辑复用、错误码常量、前端错误提示映射、聊天阶段状态处理
- 哪些重构明确不在本次范围：模型供应商热切换、流式语音播放、异步任务化、数据库迁移

## 8. 实施阶段划分

按依赖顺序拆分，不要按“文件类型”机械列任务。

### 阶段 1：测试准备

- 建立人物与聊天相关的测试文件
- 明确错误码、测试数据和本地存储夹具结构
- 为命名、样本、聊天窗口等规则先写表格驱动失败测试

### 阶段 2：基础实现

- 增加人物、样本、聊天相关 schema 与服务边界
- 增加本地文件与 JSON 元数据结构
- 打通统一错误响应和基础配置

### 阶段 3：按用户故事交付

- 先完成 P1：人物创建、样本上传/试听/删除、就绪规则
- 再完成 P2：人物设定编辑、重命名、重置人物状态
- 最后完成 P3：文字/语音聊天、10 轮上下文、语音回复与失败提示

### 阶段 4：收尾

- 清理重复逻辑
- 更新首页导航和必要文档
- 跑完后端测试、前端测试和前端构建验证

## 9. 风险与回退

| 风险 | 触发条件 | 应对方式 |
| --- | --- | --- |
| 模型供应商未定 | 实现聊天或声音克隆时缺少明确接入对象 | 先实现 `model_gateway` 接口边界，并在开始编码前锁定供应商 |
| 音频处理依赖不足 | 本地环境缺少音频转码/时长检测能力 | 优先选可在 Python 中稳定调用的最小依赖方案，并在计划外不扩展复杂媒体流水线 |
| 本地文件一致性问题 | 批量上传、删除、重置过程中出现部分写入 | 全部写入操作采用显式回滚与测试覆盖 |
| 前端交互过重 | 管理页和聊天页状态过多导致实现混乱 | 保持页面本地状态，避免过早引入全局状态库 |

### 回退策略

- 代码回退方式：按用户故事分批提交，若某阶段失败可回退对应功能提交
- 数据回退方式：本地文件与 JSON 数据按人物隔离存储，开发期间可按人物目录级别清理
- 配置回退方式：模型供应商配置未生效时，接口返回显式不可用错误，不启用隐式降级

## 10. 验证清单

- [ ] 失败测试已先写出并实际失败
- [ ] 所有实现可追溯到 `spec.md`
- [ ] 关键错误路径有显式处理
- [ ] 后端测试通过
- [ ] 前端测试通过
- [ ] 如有构建步骤，构建通过
