---
name: 飞书办公套件
description: "飞书能力执行层，与内置飞书渠道互补协作。内置渠道提供上下文（sender_open_id、chat_id），本技能负责执行所有飞书操作。触发场景：凡涉及日历/会议室、消息通知、审批、多维表格、通讯录、考勤的请求，均应调用本技能——并优先复用内置渠道已提供的 open_id/chat_id，无需再向用户询问。"
version: 1.0.1
icon: 🏢
metadata:
  clawdbot:
    emoji: 🏢
    requires:
      bins:
        - uv
      env:
        - FEISHU_APP_ID
        - FEISHU_APP_SECRET
    primaryEnv: FEISHU_APP_ID
    install:
      - id: brew
        kind: brew
        formula: uv
        bins:
          - uv
        label: Install uv via Homebrew
---

# 🏢 飞书办公套件

*Feishu/Lark Office Toolkit — 让 Agent 成为你的飞书办公助手*

基于飞书开放平台 API 的全面集成工具包，覆盖日常办公六大核心场景。通过本技能包，你可以帮用户预约会议室、发送消息、发起审批、操作多维表格、查询通讯录和管理考勤。

## 🤝 与内置飞书渠道的协作关系

两者不是"二选一"，而是**分工协作**：

| 角色 | 负责什么 | 提供/使用的数据 |
|------|----------|----------------|
| 内置飞书渠道 | **上下文提供者** — 接收消息、感知对话环境 | 提供：`sender_open_id`、`chat_id`、消息内容 |
| feishu-toolkit | **能力执行者** — 执行所有飞书操作 | 使用：上述 ID 去调用飞书 API |

### 协作模式：用内置上下文驱动本技能

内置渠道在每条消息里已经知道了发消息人的身份和当前群组。本技能应主动复用这些信息，**不要再向用户询问 ID**。

| 用户说 | 内置渠道提供 | 本技能如何用 |
|--------|-------------|-------------|
| "帮我查今天的考勤" | `sender_open_id` | 直接以该 open_id 查考勤，无需再问 |
| "查我的日程" | `sender_open_id` | 直接查该用户日历 |
| "把结果发到这个群" | `chat_id` | 用该 chat_id 发消息，无需再问群名 |
| "帮我发起请假申请" | `sender_open_id` | 以该用户身份提交审批 |
| "给张三发消息" | — | 先用通讯录查张三的 open_id，再发送 |
| "预约明天的会议室" | `sender_open_id` | 以该用户为组织者创建日程 |

### 何时单独使用本技能

操作对象明确是**第三方**时（给其他用户发消息、查其他部门的成员、操作指定多维表格），直接调用本技能，无需内置渠道提供额外信息。

## 📦 功能模块

### 1. 日历与会议室 (Calendar)
创建/更新/删除/查看日程，预约会议室，查询忙闲状态。
*   **核心能力**: 创建/更新/删除/查看日程、会议室预约、日程管理、忙闲查询
*   **详情**: [查看文档](references/calendar.md)

### 2. 消息 (Messaging)
向个人或群聊发送文本、富文本和卡片消息。
*   **核心能力**: 发送消息、回复消息、卡片交互
*   **详情**: [查看文档](references/messaging.md)

### 3. 审批 (Approval)
查看审批定义、列出可用审批类型、发起审批、查询审批状态、审批人操作（同意/拒绝/转交）、撤回审批申请。
*   **核心能力**: 查看审批定义、列出审批类型、创建审批、查询状态、审批人同意/拒绝/转交、撤回审批
*   **详情**: [查看文档](references/approval.md)

### 4. 多维表格 (Bitable)
创建多维表格、读写记录，实现结构化数据管理。
*   **核心能力**: 创建多维表格、列出多维表格、查看表结构、查询记录、新增记录、更新记录
*   **详情**: [查看文档](references/bitable.md)

### 5. 通讯录 (Contacts)
查询企业组织架构中的用户和部门信息。
*   **核心能力**: 用户查询、部门查询、组织架构浏览
*   **详情**: [查看文档](references/contacts.md)

### 6. 考勤 (Attendance)
查询员工打卡结果、补卡记录和考勤组信息。
*   **核心能力**: 打卡查询、补卡记录、考勤组管理
*   **详情**: [查看文档](references/attendance.md)


## ⚙️ 配置说明

### 前置条件

1. 在 [飞书开发者后台](https://open.feishu.cn/app) 创建自建应用
2. 为应用开启**机器人能力**
3. 根据需要的模块申请对应 API 权限（见下方权限列表）
4. 配置 **通讯录权限范围** — 在权限管理中将范围设为「全部成员」或指定部门
5. 发布应用版本并通过管理员审核

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `FEISHU_APP_ID` | ✅ | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 App Secret |
| `FEISHU_APPROVAL_CODES` | 否 | 常用审批类型映射（JSON），如 `'{"请假":"CODE1","出差":"CODE2"}'` |

### 各模块所需权限
| 模块 | 权限标识 | 说明 |
|------|----------|------|
| 日历 | `calendar:calendar` | 读写日历及日程信息 |
| 日历 | `vc:room:readonly` | 查询/搜索会议室 |
| 消息 | `im:message:send_as_bot` | 以应用身份发消息 |
| 审批 | `approval:approval` | 读写审批信息 |
| 审批 | `approval:approval.list:readonly` | 查询审批实例列表 |
| 审批 | `approval:task` | 审批人操作（同意/拒绝/转交、查询任务） |
| 多维表格 | `bitable:app` | 读写多维表格 |
| 多维表格 | `drive:drive` | 访问云空间（创建/列出多维表格时需要） |
| 通讯录 | `contact:contact.base:readonly` | 读取通讯录基本信息 |
| 通讯录 | `contact:department.base:readonly` | 获取部门信息（搜索部门/用户时需要） |
| 通讯录 | `contact:user.base:readonly` | 获取用户姓名、头像等基础信息 |
| 通讯录/考勤 | `contact:user.employee_id:readonly` | 获取用户 ID（考勤模块 open_id 转 employee_id 时必需） |
| 考勤 | `attendance:task:readonly` | 导出打卡数据 |

## 🚀 快速开始

**调用任何飞书功能前，必须先确保 API 服务正在运行。请执行以下命令：**

> ⚠️ **严禁** 执行 `pkill`、`kill`、`killall` 等任何终止 feishu-toolkit 进程的命令。服务一旦启动应持续运行，仅在未运行时才启动，不要重启。

> ⚠️ **严禁直接调用飞书开放平台 API**（`open.feishu.cn/open-apis/...`）。**严禁**自行获取 `tenant_access_token`。所有飞书操作必须通过 `http://127.0.0.1:8002` 的 feishu-toolkit 服务完成。若 feishu-toolkit 暂不支持某功能，应告知用户，而非绕过服务直接调用飞书原始 API。

> ⚠️ **Shell 脚本必须使用 `bash` 执行**（容器内 `/bin/sh` 是 `dash`，不支持 bash 语法，会报 `Bad substitution` 错误）。执行任何多行脚本时，请使用 `bash << 'EOF' ... EOF` 或 `bash -c "..."`，不要用 `sh`。

```bash
# 检查服务是否已在运行
if curl -s http://127.0.0.1:8002/ping > /dev/null 2>&1; then
  echo "feishu-toolkit 服务已运行"
else
  # 从 openclaw.json 读取飞书凭证（服务进程必须持有凭证才能鉴权）
  # 注意：容器内无 jq，使用 node 解析 JSON
  _fk_app_id=$(node -e "try{var c=require('fs').readFileSync('/home/node/.openclaw/openclaw.json','utf8');var d=JSON.parse(c);process.stdout.write((d.skills&&d.skills.entries&&d.skills.entries['feishu-toolkit']&&d.skills.entries['feishu-toolkit'].env&&d.skills.entries['feishu-toolkit'].env.FEISHU_APP_ID)||'')}catch(e){}" 2>/dev/null || true)
  _fk_app_secret=$(node -e "try{var c=require('fs').readFileSync('/home/node/.openclaw/openclaw.json','utf8');var d=JSON.parse(c);process.stdout.write((d.skills&&d.skills.entries&&d.skills.entries['feishu-toolkit']&&d.skills.entries['feishu-toolkit'].env&&d.skills.entries['feishu-toolkit'].env.FEISHU_APP_SECRET)||'')}catch(e){}" 2>/dev/null || true)
  if [ -z "$_fk_app_id" ] || [ -z "$_fk_app_secret" ]; then
    echo "feishu-toolkit 凭证未配置，请运行 manage.sh feishu <username> <appId> <secret>"
    exit 1
  fi
  # 启动服务（服务目录固定在容器内 /home/node/clawd/skills/feishu-toolkit/server）
  cd /home/node/clawd/skills/feishu-toolkit/server
  nohup env \
    FEISHU_APP_ID="$_fk_app_id" \
    FEISHU_APP_SECRET="$_fk_app_secret" \
    UV_CACHE_DIR=/home/node/clawd/skills/feishu-toolkit/.uv-cache \
    UV_LINK_MODE=copy \
    uv run uvicorn feishu_toolkit.main:app --host 127.0.0.1 --port 8002 \
    > /tmp/feishu-toolkit.log 2>&1 &
  echo "服务启动中（首次约需 30-60 秒安装依赖）..."
  for i in $(seq 1 12); do
    sleep 5
    if curl -s http://127.0.0.1:8002/ping > /dev/null 2>&1; then
      echo "feishu-toolkit 服务就绪，可以开始调用 API"
      break
    fi
    echo "  等待中... $((i*5))s"
  done
  curl -s http://127.0.0.1:8002/ping > /dev/null 2>&1 || {
    echo "服务启动失败，查看日志："; tail -30 /tmp/feishu-toolkit.log
  }
fi
```

> 服务以后台进程运行，容器重启后需重新执行上述命令。

**示例 API 调用**：

```bash
# 创建多维表格
curl -X POST http://127.0.0.1:8002/bitable/apps \
  -H 'Content-Type: application/json' \
  -d '{"name":"项目跟踪"}'

# 发送消息
curl -X POST http://127.0.0.1:8002/messaging/messages \
  -H 'Content-Type: application/json' \
  -d '{"receive_id":"ou_xxx","msg_type":"text","content":"{\"text\":\"Hello\"}"}'
```

## 使用场景

- 🏢 **会议室预约**: "帮我预约明天下午2点到3点的8楼大会议室"
- 💬 **消息通知**: "给产品组群发一条关于版本发布的通知"
- ✅ **审批流程**: "帮我发起一个出差审批"
- 📊 **数据管理**: "在项目跟踪表中新增一条任务记录"
- 👥 **人员查询**: "查一下市场部有哪些成员"
- ⏰ **考勤管理**: "查看我这周的打卡记录"

## 🔗 相关资源

*   [飞书开放平台](https://open.feishu.cn/)
*   [飞书开发者文档](https://open.feishu.cn/document/)
*   [API 调试台](https://open.feishu.cn/api-explorer)
