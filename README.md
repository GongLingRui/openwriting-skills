# OpenWriting Skills

本仓库汇集了 OpenCode/Claude Code 自动化工作流所需的各类写作 Skill，覆盖企业办公、商业文档、技术方案等场景。

## 目录

- [飞书办公套件](#飞书办公套件)
- [项目跟踪报告](#项目跟踪报告)
- [商业写作](#商业写作)
- [技术文档](#技术文档)
- [合规与审计](#合规与审计)
- [飞书文件发送](#飞书文件发送)

---

## 飞书办公套件

### feishu-toolkit

飞书能力执行层，与内置飞书渠道互补协作。

| 属性 | 值 |
|------|-----|
| **名称** | 飞书办公套件 |
| **标识** | `feishu-toolkit` |
| **版本** | 1.0.1 |

**核心功能**：日历与会议室、消息通知、审批流程、多维表格、通讯录查询、考勤管理。

**使用场景**：
- 预约会议室
- 发送群通知
- 发起审批流程
- 操作飞书多维表格
- 查询员工信息
- 查看考勤记录

**配置要求**：
- `FEISHU_APP_ID`（必填）
- `FEISHU_APP_SECRET`（必填）

> 详细文档：[feishu-toolkit/SKILL.md](feishu-toolkit/SKILL.md)

---

## 项目跟踪报告

### project-tracker-feishu

飞书版工作任务跟踪报告生成器，从飞书多维表格读取数据，自动生成6类管理报告。

| 属性 | 值 |
|------|-----|
| **名称** | 飞书工作跟踪报告 |
| **标识** | `project-tracker-feishu` |
| **版本** | 1.0.0 |

**6类报告**：

| 报告类型 | 适用场景 |
|---------|---------|
| 周进度简报 | 每周例会 |
| 月度管理报告 | 月度总结 |
| 项目节点报告 | 节点检查 |
| 团队绩效分析 | 绩效评估 |
| 风险预警专报 | 风险提示 |
| 季度汇报材料 | 领导汇报 |

**使用流程**：
1. 读取飞书多维表格数据
2. 生成报告并发送到飞书群
3. 或导出为 DOCX 公文格式

**配置要求**：
- `MINIMAX_API_KEY`（必填）
- `FEISHU_APP_ID`（必填）
- `FEISHU_APP_SECRET`（必填）

> 详细文档：[project-tracker-feishu/SKILL.md](project-tracker-feishu/SKILL.md)

---

## 商业写作

### bid-proposal-writer

**投标/方案书写作**，从 RFP/招标文件生成完整投标响应与方案书。

| 属性 | 值 |
|------|-----|
| **名称** | 投标方案写作 |
| **标识** | `bid-proposal-writer` |

**适用场景**：
- 投标书、项目方案书
- 需求响应文档
- 实施与交付计划

**输出文件**：
- `output/proposal.md`（必选）
- `output/proposal.docx`（常见）
- `output/compliance_matrix.csv`（可选：需求响应矩阵）

---

### competitive-intel-writer

**竞品分析/竞争情报报告**，包含竞品画像、SWOT、差距分析、策略建议。

| 属性 | 值 |
|------|-----|
| **名称** | 竞品分析写作 |
| **标识** | `competitive-intel-writer` |

**适用场景**：
- 竞品对标分析
- 差距分析
- 策略路线图

**输出文件**：
- `output/report.md`（必选）
- `output/scorecard.csv`（可选：量化评分表）

---

### customer-case-study-writer

**客户案例/成功故事文案**，按 Challenge-Solution-Results 结构输出。

| 属性 | 值 |
|------|-----|
| **名称** | 客户案例写作 |
| **标识** | `customer-case-study-writer` |

**适用场景**：
- 客户成功案例
- 行业应用案例
- 销售与市场背书材料

**输出结构**：
- Challenge：挑战与现状
- Solution：方案与落地
- Results：关键结果（量化）

---

### landing-page-writer

**落地页/官网功能页文案**，使用 AIDA 结构（Attention-Interest-Desire-Action）。

| 属性 | 值 |
|------|-----|
| **名称** | 落地页文案 |
| **标识** | `landing-page-writer` |

**适用场景**：
- 产品/功能推广页
- 转化页
- 官网功能页

---

### product-one-pager-writer

**产品单页/功能清单文案**，使用 FAB 结构（Features-Advantages-Benefits）。

| 属性 | 值 |
|------|-----|
| **名称** | 产品单页写作 |
| **标识** | `product-one-pager-writer` |

**适用场景**：
- 产品单页
- 销售单页
- 对外产品介绍

---

### press-release-writer

**新闻稿/公告文案**，使用 5W1H 结构（Who/What/When/Where/Why/How）。

| 属性 | 值 |
|------|-----|
| **名称** | 新闻稿写作 |
| **标识** | `press-release-writer` |

**适用场景**：
- 公司公告
- 产品发布
- 合作发布
- 融资消息

---

### sales-email-writer

**销售邮件/私信文案**，使用 PAS 结构（Problem-Agitation-Solution）。

| 属性 | 值 |
|------|-----|
| **名称** | 销售邮件写作 |
| **标识** | `sales-email-writer` |

**适用场景**：
- 冷启动邮件
- 跟进邮件
- 私信触达

---

### market-research-writer

**市场调研/行业研究报告**，包含 TAM/SAM/SOM、PESTLE、波特五力、SWOT 等分析框架。

| 属性 | 值 |
|------|-----|
| **名称** | 市场调研写作 |
| **标识** | `market-research-writer` |

**适用场景**：
- 行业调研报告
- 市场趋势分析
- 竞争格局分析
- 市场规模测算

**输出文件**：
- `output/report.md`（必选）
- `output/notes.md`（假设与引用）
- `output/charts/`（如需图表）

---

## 技术文档

### tech-design-writer

**技术方案/设计文档**，可输出 TDD/架构方案/arc42/ADR 等格式。

| 属性 | 值 |
|------|-----|
| **名称** | 技术设计写作 |
| **标识** | `tech-design-writer` |

**适用场景**：
- 技术方案
- 架构设计
- 接口规范
- 实施方案
- ADR（架构决策记录）

**输出文件**：
- `output/design.md`（必选）
- `output/adr/`（可选：决策记录）
- `output/api.md`（可选：接口说明）

---

## 合规与审计

### internal-audit-report

**内审报告写作**，从稽核底稿、访谈纪要生成正式内审报告。

| 属性 | 值 |
|------|-----|
| **名称** | 内审报告写作 |
| **标识** | `internal-audit-report` |

**适用场景**：
- 内审报告生成
- 稽核发现汇总
- 整改建议追踪

**输出文件**：
- `output/audit_report.md`（必选）
- `output/audit_report.docx`（常见）
- `output/findings.csv`（可选：发现清单）

---

### risk-control-weekly

**风控/稽核周报**，支持风险矩阵、异常趋势、整改跟踪。

| 属性 | 值 |
|------|-----|
| **名称** | 风控周报写作 |
| **标识** | `risk-control-weekly` |

**适用场景**：
- 风控周报
- 稽核周报
- 合规周报
- 风险复盘

**输出文件**：
- `output/weekly_report.md`（必选）
- `output/risk_matrix.csv`（可选）
- `output/actions.csv`（可选：整改追踪）

---

## 飞书文件发送

### feishu-im-file-send

飞书附件发送固定流程，用于将 docx/pdf/xlsx 作为飞书聊天附件发送。

| 属性 | 值 |
|------|-----|
| **名称** | 飞书文件发送 |
| **标识** | `feishu-im-file-send` |

**强制规则**：
- 必须使用 `feishu_media` 的 `upload_and_send_file` 动作
- 禁止使用 `message` 的 `filePath`
- 参数名必须是 `file_path`（下划线）

---

## 目录结构

```
openwriting-skills/
├── feishu-toolkit/                # 飞书办公套件
│   ├── SKILL.md
│   ├── server/                    # API 服务
│   └── references/                # 各模块 API 文档
│
├── project-tracker-feishu/         # 飞书工作跟踪报告
│   ├── SKILL.md
│   ├── scripts/                    # 脚本
│   └── references/                 # 参考文档
│
├── bid-proposal-writer/            # 投标方案
├── competitive-intel-writer/       # 竞品分析
├── customer-case-study-writer/     # 客户案例
├── landing-page-writer/             # 落地页
├── product-one-pager-writer/       # 产品单页
├── press-release-writer/           # 新闻稿
├── sales-email-writer/             # 销售邮件
├── market-research-writer/         # 市场调研
├── tech-design-writer/             # 技术设计
├── internal-audit-report/          # 内审报告
├── risk-control-weekly/            # 风控周报
└── feishu-im-file-send/            # 飞书文件发送
```

---

## 通用约定

部分 Skill 涉及与 OpenCode Bridge 交互，通用约定如下：

| 项目 | 约定 |
|------|------|
| **Bridge 地址** | `http://opencode-bridge:8000` |
| **鉴权方式** | `Authorization: Bearer $OPENCODE_BRIDGE_TOKEN` |
| **用户标识** | 私聊用 `open_id`，群共享用 `chat_id` |
| **输入目录** | `input/` |
| **输出目录** | `output/` |

---

## 配置与使用

各 Skill 的具体配置要求见其对应的 SKILL.md 文件。

如需在 OpenCode 环境中使用，确保：
1. 已在对应环境中配置所需的环境变量
2. 某些 Skill 需要先启动相关服务（如 feishu-toolkit）
3. 涉及文件上传时使用 Bridge API