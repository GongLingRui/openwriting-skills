---
name: project-tracker-feishu
description: 飞书版工作任务跟踪报告生成器。从飞书多维表格读取数据，自动生成6类管理报告，默认输出到飞书消息，可选导出为DOCX公文。适用于定期汇报、绩效分析、风险预警等场景。
version: 1.0.0
icon: 📊
metadata:
  clawdbot:
    emoji: 📊
    requires:
      bins:
        - python3
      env:
        - MINIMAX_API_KEY
        - FEISHU_APP_ID
        - FEISHU_APP_SECRET
      pip:
        - requests
        - python-docx
    primaryEnv: MINIMAX_API_KEY
---

# 📊 Project Tracker — 飞书版

*从飞书多维表格自动生成6类管理报告，发送到飞书群聊或导出为DOCX*

## 功能概述

本 Skill 是 project-tracker 的飞书适配版本。与 Excel 版的区别：
- **数据源**：从飞书多维表格（Bitable）实时读取，无需上传文件
- **默认输出**：发送到飞书群聊（富文本/卡片消息），也可导出 DOCX
- **依赖**：需配合 `feishu-toolkit` Skill 使用

### 6类报告

| 报告类型 | 适用场景 | 数据范围 |
|---------|---------|---------|
| 周进度简报 | 每周例会 | 最近2周 |
| 月度管理报告 | 月度总结 | 最近4周 |
| 项目节点报告 | 节点检查 | 最近4周 |
| 团队绩效分析 | 绩效评估 | 最近4周 |
| 风险预警专报 | 风险提示 | 最近4周 |
| 季度汇报材料 | 领导汇报 | 最近6周 |

## 使用步骤

### Step 0: 前置准备

1. 确保 `feishu-toolkit` 已部署并运行（默认 `http://127.0.0.1:8002`）
2. 在飞书中创建多维表格，包含两个数据表：

**表1：工作任务跟踪表**
字段包含：板块、任务分类、具体任务、重要程度、牵头/配合、负责团队、序号、各周进展（上周进展/本周计划/存在问题）

**表2：工作任务清单**
字段包含：模块、频率、工作任务、里程碑节点计划

3. 将飞书应用添加为多维表格协作者（文档右上角 → 更多 → 添加文档应用）
4. 获取多维表格 `app_token`（从多维表格 URL 提取：`https://xxx.feishu.cn/base/{app_token}`）

### Step 1: 读取飞书数据

```bash
# 读取数据并输出摘要
python3 scripts/parse_bitable.py --app-token <APP_TOKEN>

# 含任务清单（里程碑数据）
python3 scripts/parse_bitable.py --app-token <APP_TOKEN> --tasklist

# 按团队过滤
python3 scripts/parse_bitable.py --app-token <APP_TOKEN> --team 英大长安

# JSON 格式输出
python3 scripts/parse_bitable.py --app-token <APP_TOKEN> --format json
```

数据表会自动检测——脚本根据字段名关键词（板块、任务分类、具体任务等）识别工作跟踪表和任务清单表。也可手动指定 `--tracker-table` 和 `--tasklist-table`。

### Step 2: 生成报告并发送到飞书

```bash
# 全部6类报告 → 发送到飞书群聊
python3 scripts/batch_generate_feishu.py --app-token <APP_TOKEN> --chat-id <CHAT_ID>

# 全部6类 → 发送到个人
python3 scripts/batch_generate_feishu.py --app-token <APP_TOKEN> --user-id <USER_OPEN_ID>

# 使用卡片格式（更精美）
python3 scripts/batch_generate_feishu.py --app-token <APP_TOKEN> --chat-id <CHAT_ID> --feishu-format card

# 仅生成指定报告
python3 scripts/batch_generate_feishu.py --app-token <APP_TOKEN> --chat-id <CHAT_ID> --reports weekly risk
```

### Step 2-alt: 导出为 DOCX

```bash
# 全部6类 → 导出到桌面
python3 scripts/batch_generate_feishu.py --app-token <APP_TOKEN> --docx --output-dir ~/Desktop
```

### Step 3: 单独发送已有报告到飞书

```bash
# 将已有的 Markdown 报告发送到飞书
python3 scripts/send_feishu.py --input report.md --chat-id <CHAT_ID>
python3 scripts/send_feishu.py --input report.md --chat-id <CHAT_ID> --format card
```

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `MINIMAX_API_KEY` | ✅ | MiniMax API 密钥 |
| `FEISHU_APP_ID` | ✅ | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 App Secret |
| `FEISHU_TOOLKIT_URL` | 否 | feishu-toolkit 地址（默认 http://127.0.0.1:8002） |
| `MINIMAX_BASE_URL` | 否 | MiniMax API 地址（默认 https://api.minimaxi.com/v1） |

## 文件结构

```
project-tracker-feishu/
├── SKILL.md                              # 本文件
├── scripts/
│   ├── parse_bitable.py                  # 飞书多维表格数据解析
│   ├── send_feishu.py                    # 飞书消息发送
│   ├── batch_generate_feishu.py          # 批量报告生成（主入口）
│   ├── generate_docx.py                  # DOCX 生成（复用）
│   └── test_e2e.py                       # （原版遗留，飞书版不使用）
├── references/
│   ├── analysis-rules.md                 # 分析规则
│   └── report-templates.md              # 报告模板
```

## 与原版 project-tracker 的区别

| 对比项 | project-tracker | project-tracker-feishu |
|--------|----------------|----------------------|
| 数据源 | Excel 文件 (.xlsx) | 飞书多维表格 (Bitable) |
| 数据读取 | openpyxl 本地解析 | HTTP API 远程调用 |
| 默认输出 | 终端 + DOCX | 飞书消息（富文本/卡片） |
| DOCX支持 | ✅（默认） | ✅（可选 --docx） |
| 依赖 | openpyxl, python-docx | requests, python-docx, feishu-toolkit |
| 部署要求 | 仅需 Python | 需 feishu-toolkit 服务运行 |

## 报告输出规范

所有报告遵循以下规范：
- **央企公文体**：四字词组、对仗结构、分层递进
- **禁止第一人称**：不使用"我""我们""我部"，一律第三人称
- **数据驱动**：所有数据必须来自实际填报，不得编造
- **禁止 emoji/感叹号**：保持正式公文风格
- **动态团队分析**：自动识别数据中的所有团队，逐一分析
- **里程碑引用**：涉及节点风险时必须引用具体时间节点
