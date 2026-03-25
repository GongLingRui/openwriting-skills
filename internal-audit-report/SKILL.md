---
name: internal-audit-report
description: "内审报告写作（范围/方法/发现/证据/整改建议/管理层回复）。从稽核底稿、访谈纪要、日志导出生成正式报告。"
---

# Internal Audit Report（内审报告）

你负责把内审工作底稿与证据材料整理成正式内审报告。涉及证据汇总、表格对齐、引用索引、长文输出时通过 OpenCode 执行。

## 触发条件

- 用户要生成/改写内审报告
- 用户上传稽核底稿、访谈纪要、系统日志、抽样清单等材料

## 约定

- bridge：`http://opencode-bridge:8000`
- 鉴权：`Authorization: Bearer $OPENCODE_BRIDGE_TOKEN`
- `{user}`：私聊 `open_id`；群共享用 `chat_id`
- 输出落盘：
  - `output/audit_report.md`（必选）
  - `output/audit_report.docx`（常见需要）
  - `output/findings.csv`（可选：发现清单）

## 阶段一：确认报告要素

必须确认：

- 审计对象与范围（系统/流程/组织/期间）
- 审计标准与依据（制度、法规、内控要求）
- 报告读者（管理层/合规/业务负责人）
- 输出格式（md/docx）

## 阶段二：上传证据与底稿

要求用户上传所有证据材料，并逐个写入 `input/`：

```bash
curl -sS -F "file=@/path/to/file" "http://opencode-bridge:8000/file/{user}" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

## 阶段三：委托 OpenCode（指令模板）

指令必须包含：

- 报告结构（建议）：
  1. 执行摘要（结论、重大风险、总体评价）
  2. 范围与方法（抽样、访谈、系统核查等）
  3. 发现与影响（每条发现要有证据、风险、根因、建议）
  4. 整改建议与优先级（含责任人/截止日期）
  5. 管理层回复（如有）
- 发现清单输出：
  - `output/findings.csv`：字段建议（编号、主题、等级、证据来源、影响、建议、负责人、截止日期）
- 证据索引：
  - `output/notes.md`：每条发现对应 `input/...` 的证据路径与页码/段落说明（能定位就定位）

提交：

```bash
curl -sS -X POST "http://opencode-bridge:8000/task/{user}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN" \
  -d '{"message":"<内审报告结构化指令，引用 input/...>"}'
```

## 阶段四：回传与复核

- 先回传：重大发现 Top N + 需要管理层决策项
- 再回传：`audit_report.md`/`docx`/`findings.csv`
- 复核修改：按“发现编号”逐条修改，避免泛泛改动
