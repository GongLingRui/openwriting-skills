---
name: risk-control-weekly
description: "风控/稽核周报写作（风险矩阵、异常趋势、整改跟踪、下周计划）。支持从表格/纪要/工单导出生成周报与附件。"
---

# Risk Control Weekly（风控/稽核周报）

你负责生成“可落地”的风控/稽核周报：既要覆盖风险全景，也要能落到责任人、整改动作与截止日期。涉及表格、工单导出、证据材料汇总时，交给 OpenCode 执行。

## 触发条件

- 用户要写“风控周报/稽核周报/合规周报/风险复盘”
- 需要从 Excel/CSV/Word/PDF 汇总异常、生成风险矩阵、整改追踪表

## 约定

- bridge：`http://opencode-bridge:8000`
- 鉴权：`Authorization: Bearer $OPENCODE_BRIDGE_TOKEN`
- `{user}`：私聊 `open_id`；群共享用 `chat_id`
- 输出必须写入 `/workspace/output/`：
  - `output/weekly_report.md`（必选）
  - `output/risk_matrix.csv`（可选）
  - `output/actions.csv`（可选：整改追踪清单）

## 阶段一：问清楚四件事

- 周期：起止日期（本周）
- 覆盖范围：业务线/系统/区域/团队
- 风险口径：风险等级定义（影响×可能性），以及“重大/高/中/低”的阈值
- 输出：只要 Markdown 还是需要 Word（如需要则追加 `output/weekly_report.docx`）

## 阶段二：上传材料

让用户上传：

- 异常/告警清单（Excel/CSV）
- 稽核发现（Word/PDF）
- 整改跟踪表（Excel）
- 工单导出（CSV/Excel）

逐个上传：

```bash
curl -sS -F "file=@/path/to/file" "http://opencode-bridge:8000/file/{user}" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

## 阶段三：委托 OpenCode（指令模板）

指令必须包含：

- 本周摘要：3–8 条（风险变化、关键事件、影响范围）
- 风险矩阵：按“类别/风险项/证据/等级/建议/负责人/截止日期”
- 异常趋势：按周/天的变化与解释（如果输入数据支持）
- 整改跟踪：未关闭项列表 + 进度 + 阻塞点
- 下周计划：稽核重点与改进动作

输出文件：

- `output/weekly_report.md`
- `output/notes.md`（口径/假设/证据索引）
- 可选 `output/risk_matrix.csv`、`output/actions.csv`

提交：

```bash
curl -sS -X POST "http://opencode-bridge:8000/task/{user}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN" \
  -d '{"message":"<周报结构化指令，引用 input/...>"}'
```

## 阶段四：回传

- 先发“本周要点 + 风险 Top5 + 需要决策/资源支持事项”
- 再按 `files` 下载并发回 `weekly_report.md`/`docx`/表格附件
