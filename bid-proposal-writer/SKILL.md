---
name: bid-proposal-writer
description: "投标/方案书写作（需求响应、技术方案、实施计划、交付与验收、报价说明、风险与承诺）。需要从 RFP/附件生成完整文档时委托 OpenCode。"
---

# Bid Proposal Writer（投标/方案书）

你负责基于 RFP/招标文件与附件材料，生成结构清晰、可交付的投标响应与方案书。涉及大量附件解析、目录与一致性校验、长文输出时通过 OpenCode 执行。

## 触发条件

- 用户要写投标书、项目方案书、需求响应、实施与交付计划
- 用户上传 RFP（PDF/Word）与多份附件（表格、资质、案例等）

## 约定

- bridge：`http://opencode-bridge:8000`
- 鉴权：`Authorization: Bearer $OPENCODE_BRIDGE_TOKEN`
- `{user}`：私聊 `open_id`；群共享用 `chat_id`
- 输出必须落盘：
  - `output/proposal.md`（必选）
  - `output/proposal.docx`（常见需要）
  - `output/compliance_matrix.csv`（可选：逐条需求响应矩阵）

## 阶段一：澄清投标要素

必须问清楚：

- 客户/项目名称、截止时间、交付物要求（格式/模板/页数）
- 响应范围：技术 + 实施 + 运维 + 安全 + 资质 + 报价（哪些要写）
- 是否需要严格对齐 RFP 章节与条款编号

## 阶段二：上传 RFP 与附件

让用户上传全部材料到 `input/`：

```bash
curl -sS -F "file=@/path/to/file" "http://opencode-bridge:8000/file/{user}" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

## 阶段三：委托 OpenCode（指令模板）

指令必须包含：

- RFP 主文件路径：`input/...`
- 附件清单（案例/资质/价格表/产品白皮书等）：`input/...`
- 输出结构（建议）：
  1. 项目理解与总体方案
  2. 需求响应（逐条）
  3. 技术架构与方案细节
  4. 实施计划（里程碑、资源、风险）
  5. 交付与验收
  6. 运维与支持
  7. 安全与合规
  8. 资质与案例
  9. 报价说明（如需要）
- 合规矩阵：
  - `output/compliance_matrix.csv`：字段（条款编号、条款原文摘要、响应、证据/引用、备注）

输出文件：

- `output/proposal.md`
- `output/notes.md`（引用与证据索引：哪些内容来自哪些 input）
- 可选：`output/proposal.docx`、`output/compliance_matrix.csv`

提交：

```bash
curl -sS -X POST "http://opencode-bridge:8000/task/{user}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN" \
  -d '{"message":"<投标方案结构化指令，引用 input/...>"}'
```

## 阶段四：回传与一致性校验

- 先回传：总体方案亮点、关键承诺、风险与对策
- 再回传：`proposal.md`/`docx`/合规矩阵
- 若用户要求严格编号一致性：再次委托 OpenCode 进行“条款编号对齐检查 + 修订”
