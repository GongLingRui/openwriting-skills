---
name: tech-design-writer
description: "技术方案/设计文档写作（需求、架构、API、数据模型、部署、风险、ADR/arc42）。需要结构化长文与图表时委托 OpenCode。"
---

# Tech Design Writer（技术方案/设计文档）

你负责把需求与约束整理为可评审、可落地的技术设计文档（TDD/架构方案/arc42/ADR）。涉及大量材料整理、生成目录结构、输出长文时交给 OpenCode 执行。

## 触发条件

- 用户要写技术方案、架构设计、接口规范、实施方案、ADR、arc42 文档
- 用户上传现有设计稿/接口表/日志/历史文档并要求整合

## 约定

- bridge：`http://opencode-bridge:8000`
- 鉴权：`Authorization: Bearer $OPENCODE_BRIDGE_TOKEN`
- `{user}`：私聊 `open_id`；群共享用 `chat_id`
- 输出落盘到 `/workspace/output/`：
  - `output/design.md`（必选）
  - `output/adr/`（可选：多份 ADR）
  - `output/api.md`（可选：接口说明）

## 阶段一：澄清输入与评审目标

必须问清楚：

- 目标：要解决什么问题、成功指标是什么
- 约束：性能、成本、上线时间、合规、安全、依赖系统
- 读者：架构评审/研发实现/运维交付/管理层
- 输出格式：Markdown（必选），如需可再导出 docx

## 阶段二：上传资料

让用户上传：

- 现有方案/需求文档（Word/PDF/Markdown）
- 接口表/数据字典（Excel/CSV）
- 现状架构图或描述（任何格式都可）

逐个上传到 `input/`：

```bash
curl -sS -F "file=@/path/to/file" "http://opencode-bridge:8000/file/{user}" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

## 阶段三：委托 OpenCode（指令模板）

推荐输出结构（可按需要裁剪）：

1. 背景与目标
2. 需求（功能/非功能）
3. 总体架构（组件、数据流、关键交互）
4. 关键设计细节（存储/缓存/一致性/幂等/容错）
5. API 设计（如有）
6. 数据模型（如有）
7. 安全与合规
8. 发布与运维（部署、监控、回滚、容量）
9. 风险与备选方案
10. 开发计划（里程碑、验收）

输出文件：

- `output/design.md`
- `output/notes.md`（未决问题、假设、引用索引）
- 可选：`output/adr/0001-*.md`（决策记录）

提交：

```bash
curl -sS -X POST "http://opencode-bridge:8000/task/{user}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN" \
  -d '{"message":"<技术设计结构化指令，引用 input/...>"}'
```

## 阶段四：回传与评审修订

- 先回传：关键架构决策、主要风险与备选方案
- 再回传：`design.md`、ADR、API 文档等
- 修订：按章节编号逐条修改，保留决策可追溯性
