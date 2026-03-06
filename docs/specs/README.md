# 规格驱动开发（Spec-Driven Development）

本项目采用轻量级的「先规格、后开发」流程。

## 目录结构

- `docs/specs/templates/`：可复用模板。
- `docs/specs/features/<feature-name>/`：单个需求的规格包。

每个需求目录应包含：

- `spec.md`：产品规格 + 技术规格。
- `tasks.md`：执行任务拆解与负责人。
- `test-plan.md`：验证范围与验收检查项。

## 必要流程

1. 在 `docs/specs/features/` 下创建需求目录。
2. 开发前先完成 `spec.md`。
3. 将实现拆解到 `tasks.md`。
4. 在 `test-plan.md` 中定义测试用例。
5. 规格评审通过后再开始编码。
6. PR 必须引用该需求规格路径。

## 评审门禁

- 没有 `spec.md`，不开始实现。
- 实现必须与规格中的 API/数据/风险条目一致。
- PR 必须提供 `test-plan.md` 对应的测试证据。
- 高风险变更必须写明回滚方案。

## 命名规范

需求目录使用 kebab-case，例如：

- `user-auth-session-refresh`
- `billing-monthly-summary`
