
---
name: opencode-writer
description: 编码/文件解析重任务编排。默认通过 sessions_send 委托 coder Agent，重任务升级 sessions_spawn，并统一由 coder 通过 opencode-bridge 执行。
---

# OpenCode Writer（A2A + Bridge）

## 执行总则

- 默认链路：`sessions_send -> coder -> opencode-bridge -> OpenCode`
- 重任务链路：`sessions_spawn(agentId="coder") -> opencode-bridge -> OpenCode`
- 禁止将 `sessions_spawn` 误用为 ACP 执行路径；`runtime="acp"` / `acpx` 不作为本技能主路径

## 何时升级到 sessions_spawn

满足任一条件即升级：

1. 预计执行时间 > 10 分钟
2. 需要并行多个批次（长文、多个产物并行生成）
3. 同会话有多个独立重任务同时推进

## coder 侧 Bridge 标准流程

1. `POST /file/{user}` 上传输入文件
2. `POST /task/{user}` 提交结构化 message
3. 读取返回 `files` / `file_sizes`
4. 仅按返回路径执行 `GET /file/{user}/...` 下载产物

## 约束

- 不在网关直接跑 `python3` / pandas / openpyxl / matplotlib 代替 Bridge
- 不猜测产物文件名，不在 `files` 白名单外下载
- 失败时先重试 Bridge，再决定是否回退方案
