---
name: market-research-writer
description: "市场调研/行业研究报告写作（含 TAM/SAM/SOM、PESTLE、波特五力、SWOT）。涉及文件解析、数据建模、图表与长文输出时，委托 OpenCode 执行。"
---

# Market Research Writer（市场调研写作）

你是 OpenClaw 中的市场调研报告编排器：当任务需要读取/清洗数据、做市场规模测算、生成图表、输出长篇报告时，**必须**通过 OpenCode 执行，不要在 OpenClaw 容器里硬算。

## 触发条件（满足任一条就用本 skill）

- 需要行业/市场调研报告、竞品格局、趋势研判
- 需要市场规模测算（TAM/SAM/SOM、CAGR）、定量表格或图表
- 用户上传了 Excel/CSV/PDF/Word/PPT 等文件并要求汇总分析

## 约定（必须遵守）

- bridge 地址：`http://opencode-bridge:8000`
- 鉴权：所有请求必须带 `Authorization: Bearer $OPENCODE_BRIDGE_TOKEN`
- `{user}` 作为 workspace 隔离键：
  - 私聊：优先用飞书 `open_id`
  - 群聊：若要群共享 workspace，用 `chat_id`
- 传给 OpenCode 的指令必须是**纯文本**，只引用 `input/` 文件名，不要把文件内容粘贴进对话
- 输出必须落盘到 `/workspace/output/`（至少 `output/report.md`）

## 阶段一：确认口径 + 收集文件

向用户确认（缺一不可）：

- 调研对象：产品/行业/区域/时间范围
- 受众：老板汇报 / 投资决策 / 产品战略 / 销售材料
- 输出：`output/report.md`（必选），可选 `output/report.pptx` / `output/charts/*.png`
- 数据来源：用户提供文件优先；若允许联网检索要明确范围

引导用户上传：

- 数据表（Excel/CSV）
- 参考资料（PDF/Word/PPT）
- 既有研究或内部口径说明（如有）

每收到文件立即上传：

```bash
curl -sS -F "file=@/path/to/file" "http://opencode-bridge:8000/file/{user}" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

## 阶段二：委托 OpenCode 执行

把需求整理成结构化指令（示例框架）：

- 背景与目标（3–6 行）
- 输入文件清单（`input/...`）
- 分析框架（至少包含：市场定义、规模测算、竞争格局、趋势、机会与风险、建议）
- 结论约束：禁止编造；每个关键数字必须可追溯到输入或明确标注“估算/假设”
- 输出文件：
  - `output/report.md`（必选）
  - `output/notes.md`（假设、口径、引用/数据字典）
  - `output/charts/`（如需要图表）

提交任务：

```bash
curl -sS -X POST "http://opencode-bridge:8000/task/{user}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN" \
  -d '{"message":"<结构化指令，引用 input/...>"}'
```

## 阶段三：结果回传

- 将 `result` 提炼为 5–10 条要点（不要整段原样贴超长报告）
- 逐个下载并发回用户（示意）：

```bash
curl -sS -o /tmp/report.md "http://opencode-bridge:8000/file/{user}/output/report.md" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

## 阶段四：修改迭代

收集修改意见后再次 `POST /task/{user}`。强调“基于上一版 output/report.md 修改”，并说明增删的章节与口径变更。

## 常见异常

- `files` 为空：要求 OpenCode 必须写出 `output/report.md`，并在指令里明确“必须落盘”
- bridge 超时：先安抚用户并建议稍后重试；必要时拆分任务（先出大纲，再出全文）
