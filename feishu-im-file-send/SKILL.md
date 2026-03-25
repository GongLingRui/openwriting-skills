---
name: feishu-im-file-send
description: 飞书附件发送固定流程（docx/pdf/xlsx）。当用户要求“把文件作为附件发到飞书聊天”时必须触发本 skill，并严格走 feishu_media，不得改用 message(filePath) 或 feishu_doc.upload_file。
---

# 飞书 IM 文件发送固定流程

## 适用场景

- 用户明确要求把 `docx/pdf/xlsx/ppt` 作为 **飞书聊天附件** 发出。
- 用户提到“飞书里收不到文件”“只写到文档没推送到聊天”。

## 强制规则（必须遵守）

1. **只用** `feishu_media` 发聊天附件，动作固定为 `upload_and_send_file`。
2. **禁止** 使用 `message` 的 `filePath` 给飞书发文件（该路径不是飞书附件主路径）。
3. **禁止** 用 `feishu_doc` 的 `upload_file` 代替聊天发附件（它只会把附件写进文档块）。
4. 参数名必须是 `file_path`（下划线），且必须是运行时可读的绝对路径。
5. 发送后必须在回复里包含发送结果关键字段：`ok`、`fileKey`（至少 `fileKey`）。

## 执行步骤

1. 确认产物文件真实存在（例如 `output/report.docx`）。
2. 下载/拷贝到本地可读绝对路径（例如 `/tmp/report.docx`）。
3. 调用 `feishu_media`：
   - `action`: `"upload_and_send_file"`
   - `to`: 群聊用 `chat:<chat_id>`；私聊用 `open_id:<open_id>`
   - `file_path`: `/tmp/report.docx`
   - `file_name`: `report.docx`（可选但推荐）
4. 检查工具返回；若失败，返回明确错误信息，不得声称“已发送”。

## 标准调用示例

```json
{
  "action": "upload_and_send_file",
  "to": "chat:oc_xxx",
  "file_path": "/tmp/report.docx",
  "file_name": "report.docx"
}
```

## 失败处理

- 如果返回 `schema is invalid`：检查是否误用了 `filePath` 或把参数放错层级，改为 `file_path`。
- 如果返回账号/权限错误：提示具体账号与权限问题，并保留文件路径供重试。
- 如果文件不存在：先回到产物生成步骤补齐文件，再重发附件。
