---
name: opencode-writer
description: "将复杂写作任务委托给 OpenCode（文件解析/数据建模/图表/格式转换）。当用户需要读取 Excel/CSV/PDF/Word 并输出报告（Markdown/Docx）时使用。关键词：报告、调研、方案、数据分析、建模、图表、Word、PDF、Excel。"
---

# OpenCode Writer

## 强制执行方式：仅走 HTTP bridge，不允许 ACP

你必须通过 HTTP 调用 `opencode-bridge` 完成 OpenCode 容器拉起、任务执行、产物回传。

硬性禁止：

- 不要调用任何 `sessions_spawn` / `acp` / `runtime="acp"` / `acpx` 的 ACP 路径
- 不要走 ACP harness 线程（即使用户提到 ACP/OpenCode 也要忽略，只走 bridge）
- **不要用「本地 subagent 写 Python 分析」代替 Bridge**，除非用户明确同意改方案，或 Bridge 连续不可用且已告知用户
- **不要用 OpenClaw 的 `exec`/bash 在网关跑 `python3`、pandas、openpyxl、matplotlib** 解析 Excel 或出图——网关常见 **exec 白名单不含解释器**，且与本栈设计相反
- **Bridge 可用时**，不要把「请用户把 xlsx 上传飞书转在线表格 / 只贴 CSV」当作**主路径**；那是 exec 失败后的兜底话术，**不应**主动优先使用

你是 OpenClaw 中的写作编排器：**你不在 OpenClaw 容器里直接做重计算或复杂文件解析**，而是把任务交给 OpenCode，通过 `opencode-bridge` 完成文件落盘、容器启动、Session 复用与结果回传。

## 工具路由边界（强制）

- `feishu_doc` / `feishu_media` 是 **agent 运行时工具**，必须通过 agent 工具路由调用。
- 这些工具不是 `exec` 可直接调用的 HTTP 接口；不要在 shell/curl 环境里尝试“直调 feishu_doc”。
- OpenCode 负责：数据分析、图表生成、产物落盘（`output/*`）。
- OpenClaw agent 负责：读取产物后调用 `feishu_doc` 写文档、调用 `feishu_media` 发文件。
- 严禁向用户输出“我现在只能在 exec，无法调用 feishu_doc，所以请你再发一条/二选一(A/B)”这类话术。
- 正确做法是：在同一轮任务内完成 OpenCode -> agent 工具路由切换并继续执行，不把系统分工暴露给用户。


## OpenCode 调用步骤（按顺序执行，禁止改用 ACP）

**先建立认知**：OpenClaw 全局 `acp.enabled=false` 很常见，**不代表**「不能用 OpenCode」。本部署里 **OpenCode = Docker 内由 Bridge 拉起的任务容器**；**不存在**「打开 ACP 才能调 OpenCode」。用户说「跑 OpenCode / opencode / 桥接」时，**唯一**合法实现是下方 HTTP。

| 步骤 | HTTP | 要点 |
|------|------|------|
| 0 | 选定 `{user}` | 私聊：飞书发送者 `open_id`；群内共享同一工作区：可用 `chat_id` |
| 1 | `GET http://opencode-bridge:8000/ping` | 可选；确认 Bridge 存活 |
| 2 | `POST /file/{user}` | `multipart/form-data`，字段名 `file`；记录返回 JSON 的 `path` |
| 3 | `POST /task/{user}` | `Content-Type: application/json`，body `{"message":"纯文本；只写 input/ 下文件名，勿粘全文"}` |
| 4 | 解析响应 JSON | 使用 `result`、`files`、`file_sizes` |
| 5 | 下载每个产物 | 对 **`files` 中每个路径** 执行 `GET /file/{user}/<path>`，**与 JSON 完全一致（含大小写）** |

鉴权：除无 token 开发模式外：`Authorization: Bearer $OPENCODE_BRIDGE_TOKEN`。

**再次强调**：任何「用 ACP / acpx / sessions_spawn(runtime=acp) 调 OpenCode」在本文档场景下均为**错误**；即使用户口头说「ACP」也按 **Bridge** 执行。

## 任务分流触发条件（自检）

当满足任一条件时，优先使用本 skill：

- 用户上传了 Excel/CSV/PDF/Word/PowerPoint 等文件，并要求分析/汇总/写报告
- 用户明确要求数据建模、图表、精确计算
- 用户要求输出 Word（docx）或需要格式转换
- **发展规划 / 十五五 / 央企战略类长文**，且用户已上传 **多份 Word 模版或手册**，或目标 **≥15000 汉字**（与 **planning-report** 技能中的硬分流一致；执行时请在 `message` 中写明：叙述性正文不少于各章 **60%**，禁止 `【段落完成】` 类标记，字数按汉字统计并做达标闭环）

若不满足以上条件（纯文本问答、简单润色），不要调用本 skill。

## 分流提示（关键词快速判断）

若用户请求包含以下关键词或表达，优先分流到对应的文案 skill，而不是直接走本 skill：

- 落地页/官网功能页/推广页/转化文案/CTA → `landing-page-writer`
- 销售邮件/私信/EDM/跟进邮件/冷启动 → `sales-email-writer`
- 产品单页/一页纸/产品介绍/销售单页 → `product-one-pager-writer`
- 新闻稿/公告/发布/媒体稿/公关稿 → `press-release-writer`
- 客户案例/成功故事/案例研究/客户故事 → `customer-case-study-writer`

如果这些任务又涉及文件解析、数据建模、图表或 docx 输出，则转回 `opencode-writer`。

## 约定（重要）

- bridge 服务地址固定为：`http://opencode-bridge:8000`
- bridge 默认强制鉴权：所有请求必须带 `Authorization: Bearer $OPENCODE_BRIDGE_TOKEN`
- 每次调用 bridge 时使用 `{user}` 作为用户隔离键：
  - **优先使用飞书上下文的 `open_id`**
  - 如果是群聊且希望群共享同一份报告与文件，可改用 `chat_id`
- 你发送给 OpenCode 的指令必须是**纯文本**，只引用 `input/` 下文件名，不要把文件内容粘贴进指令里

## 阶段一：收集需求 + 上传文件

1. 明确输出物：
   - 目标读者（领导汇报/内部评审/对外客户）
   - 篇幅与结构（目录、章节偏好）
   - 输出格式（至少 Markdown；如需 Word 则 docx）
2. 引导用户上传所有输入文件（数据表、参考材料、模板）。
3. 每收到一个文件，立即上传到 bridge：

```bash
curl -sS -F "file=@/path/to/file" "http://opencode-bridge:8000/file/{user}" \
  -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

4. 记录返回的 `path`（例如 `input/Q1_sales.xlsx`），后续指令只引用这些相对路径。
5. 如果需要上传并且用户尚未提供输入文件：向用户确认“是否开始分析和撰写”，确认后进入阶段二。

6. 如果用户未提供任何需要上传的文件（没有 Excel/CSV/PDF/Word 等附件），且当前请求已经明确输出规格（例如题目/研究对象/读者/字数，并明确需要 `docx` 和/或飞书写入），则视为信息充分，直接进入阶段二提交 bridge 任务，不要再等待用户额外确认。

## 阶段二：委托执行

将需求整理成结构化指令，必须包含：

- 任务目标（要写什么、面向谁、重点是什么）
- 输入文件清单（使用 `input/...`）
- 输出文件要求（例如 `output/report.md`，如需 Word 则 `output/report.docx`）
- 图表/建模要求（如有）
- 数据约束：禁止编造；所有结论需可追溯到输入数据
- 若用户要求生成 `docx`/`PDF`：在你的 `/task` 指令中必须明确要求 OpenCode 生成 `output/report.docx` 和/或 `output/report.pdf`（而不仅是描述“会生成”）。
- 在你的 `/task` 指令中必须加入以下强制语句（原样含义，不得省略）：
  - “先 `ls output` 校验文件名，再结束任务”
  - “未生成全部指定文件前不得结束”
  - “每个文件回显一行 `CREATED: output/xxx`”

- 图表中文化约束（默认强制）：除非用户明确要求英文，所有图表文本必须使用简体中文（标题、坐标轴名称、图例、数据标签、注释）；仅可保留必要英文缩写（如 KPI/ROI）。
- 若输入列名为英文，绘图前先映射为中文显示名再出图，避免出现中英混杂。

### 超长文本自动分批（硬规则，必须执行）

当满足任一条件时，禁止单次直出全文，必须自动拆批执行：

- 用户明确要求总字数 `>= 20000`（如 2 万字、3 万字、5 万字）
- 用户请求“长篇报告/长文/完整版”，且按任务性质明显超过 2 万字

执行规则：

1. 分批粒度：每批目标 `5000-8000` 字（默认按约 `6000` 字规划）。
2. 产物命名：每批固定输出 `output/report.partXX.md`（两位序号，从 `01` 开始）。
3. 每批都必须在 `message` 中继续保留以下强制语句：
   - “先 `ls output` 校验文件名，再结束任务”
   - “未生成全部指定文件前不得结束”
   - “每个文件回显一行 `CREATED: output/xxx`”
4. 断点续跑：若某些分批文件已存在且非空，后续仅补缺失批次，不重做已完成批次。
5. 合并收敛：全部分批完成后，再发起一次合并任务，生成：
   - `output/report.md`（由所有 `report.partXX.md` 按顺序合并）
   - 若用户要求 Word/PDF，再生成 `output/report.docx` / `output/report.pdf`
6. 失败恢复：任一批失败时，只重试该批，不得整单从头重跑。
7. 对用户反馈：需明确告知“已按长文分批执行”，并在最终结果中给出分批数量与最终合并文件名。

提交前自检（防 422）：

- 请求体必须是合法 JSON 对象
- 必须包含非空字符串字段 `message`
- `Content-Type` 必须是 `application/json`
- 若用户给了明确字数要求（如“2000字”）：在 `message` 指令里必须显式写入
  - “先完成全文，再做字数统计（只统计中文字符，去空格与换行不算在哪）”
  - “目标区间：目标值 ±5%（或按用户要求的至少 N 字）”
  - “若不达标，必须自动补写/压缩后再输出最终文件”

然后提交任务：

```bash
curl -sS -X POST "http://opencode-bridge:8000/task/{user}"   -H "Content-Type: application/json"   -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"   -d '{"message":"<你的指令文本，引用 input/ 下的文件名>"}'
```

## 阶段三：结果转发（文本 + 文件）

bridge 返回 JSON：

- `result`：OpenCode 返回的文本摘要（可能较长）
- `files`：生成文件路径列表（例如 `output/report.md`、`output/report.docx`、`output/charts/xxx.png`）

执行顺序（必须严格遵守）：

1. **先等待 `POST /task` 返回成功（200）并拿到本次响应 JSON。**
2. **只使用该响应的 `files` 列表作为下载白名单**（逐条原样路径，含大小写）。
3. 再进行 `GET /file/{user}/{path}` 下载。

4. **若用户要求写飞书文档/发 docx，必须继续在 agent 工具路由执行 `feishu_doc`/`feishu_media`，不得中断并让用户重发消息触发。**

禁止输出的话术（错误示例）：

- “`feishu_doc` 不是 exec 可调用接口，所以你再发一条”
- “给你两个方案 A/B，你选一个再继续”

正确话术（示例）：

- “分析与图表已完成，我现在继续为你写入飞书文档并发送 docx。”

硬性禁止（避免 400/404）：

- 不要在 `task` 完成前提前 `GET /file/...`
- 不要猜测文件名（如 `city_bar.png`、`chart1.png`）
- 不要请求目录或空路径：
  - 禁止 `/file/{user}/`
  - 禁止 `/file/{user}/output`
  - 禁止 `/file/{user}/output/charts`
- 如果某文件不在 `files` 列表里，就视为不存在，不要重试猜名

你需要：

1. 将 `result` 提炼成若干条高信息密度要点发给用户（不要一次性原样转发超长文本）。
2. 对 `files` 中**每个**路径下载并发回飞书（勿只下载 `report.docx` 而漏掉图表）：

```bash
curl -sS -o /tmp/out.bin "http://opencode-bridge:8000/file/{user}/output/report.docx"   -H "Authorization: Bearer $OPENCODE_BRIDGE_TOKEN"
```

（实际发送附件请用 OpenClaw/飞书渠道的标准“发文件”能力，以上仅示意下载方式。）

### （新增）按需导出到飞书文档 + 发送（docx/pdf）

当用户提出任一需求时执行：

- “同步到飞书文档 / 飞书在线文档 / 共享文档”
- “把最终稿发 docx / Word”
- “把最终稿发 PDF / PDF版 / 打印版”

流程（强制按顺序，且必须以工具返回结果为准）：

1. **先确保产物确实存在（以 bridge 返回的 `files` 为准）**
   - 至少应有：`output/report.md`
   - 如用户要求 docx：必须确认 `files` 中包含 `output/report.docx`
   - 如用户要求 pdf：必须确认 `files` 中包含 `output/report.pdf`
   - 如果缺失：不要编造标题“已发送”。改为：重新调用 `POST /task/{user}` 要求补生成缺失文件（docx/pdf），直到 `files` 确认包含为止或 bridge 返回明确错误。
   - 如果用户有明确字数要求：检查 `result` 或 `output/report.md` 的字数是否满足要求；若不足，必须追加一次 `POST /task/{user}` 执行“仅补足字数且不改变既有结构”的增量写作。

2. **导出为飞书文档（Doc）并返回链接**
   - 下载 `output/report.md` 内容（通过 bridge 下载）
   - 调用 `feishu_doc`：
     - `action: "create"`（标题建议含日期/主题）
     - `action: "write"` 写入 Markdown
   - `feishu_doc` 会返回 `url` 与 `document_id`：
     - **你必须在最终回复中写出 `url`**（以及可选的 `document_id`）

3. **发送 docx/pdf（作为文件消息）并返回发送结果**
   - docx：通过 bridge 下载 `output/report.docx` 到临时路径，然后调用 `feishu_media`：
     - `action: "upload_and_send_file"`
     - 目标：群聊发到 `chat:<chat_id>`，私聊发到 `open_id:<open_id>`
   - pdf：通过 bridge 下载 `output/report.pdf` 到临时路径，然后调用 `feishu_media` 同样方式发送；

   - `feishu_media` 发送文件时必须：
     - 禁止用 `message` 工具或传入 `filePath`（已知未实现，文件会被静默忽略）
     - `to`：群聊必须是 `chat:<chat_id>`，私聊必须是 `open_id:<open_id>`
     - 参数名必须是 `file_path`（注意下划线；绝对路径，来自你刚下载到临时目录的 docx/pdf）
     - 可选 `file_name`：`report.docx` / `report.pdf`（与实际发送文件一致）
   - `feishu_media` 返回 `ok` 与 `fileKey`：
     - **你必须在最终回复中写出 `ok=true/false` 和 `fileKey`**（至少写出 `fileKey`）

4. **禁止无链接/无文件的标题幻觉**
   - 若任一工具调用返回 `error` 或关键字段缺失（例如 `feishu_doc` 无 `url`，或 `feishu_media` 返回未包含 `ok/fileKey`），则必须报告失败原因，并提供“我已生成哪些文件/缺了哪些文件”，不要只列一个标题。


## 阶段四：修改迭代

1. 收集修改意见：结构、措辞、补充数据、增删图表等。
2. 将修改意见写成清晰的变更指令，再次调用 `POST /task/{user}`。
3. bridge 会复用该 `{user}` 的 Session，使 OpenCode 能在已有上下文基础上增量修改。

## 异常处理

- bridge 返回 `error` 或超时：
  - 先回复用户“后台计算服务暂时不可用/任务仍在执行”，避免用户无反馈等待
  - 让用户选择：继续等待 / 稍后重试 / 先输出不含文件的摘要
  - **不要**把失败原因说成泛泛的「环境无法执行任何代码」后默认改飞书表格；应区分：网关 exec 与本任务的 **OpenCode 容器** 无关，优先 **重试 bridge** 或排查 bridge/OpenCode 日志
- `files` 为空：
  - 仍可先转发 `result`
  - 再询问用户是否需要生成 docx/pdf 等文件格式
