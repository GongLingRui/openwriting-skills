#!/usr/bin/env python3
import sys, os; sys.path.insert(0, "/home/node/clawd/.pylib/lib/python3.11/site-packages")
"""
send_feishu.py — 将报告发送到飞书

支持三种发送方式：
1. 富文本消息 (post) — 默认，支持标题+格式化内容
2. 卡片消息 (interactive) — 精美卡片格式，支持 Markdown
3. 文本消息 (text) — 纯文本

用法:
  python3 send_feishu.py --input report.md --chat-id oc_xxx
  python3 send_feishu.py --input report.md --chat-id oc_xxx --format card
  python3 send_feishu.py --input report.md --user-id ou_xxx
"""

import argparse
import json
import os
import re
import sys

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests", file=sys.stderr)
    sys.exit(1)

FEISHU_TOOLKIT_URL = os.environ.get("FEISHU_TOOLKIT_URL", "http://127.0.0.1:8002")
# 飞书富文本消息最大 30KB
MAX_POST_SIZE = 28000


def send_message(receive_id, receive_id_type, msg_type, content):
    """调用 feishu-toolkit 发送消息"""
    url = f"{FEISHU_TOOLKIT_URL}/messaging/send"
    payload = {
        "receive_id": receive_id,
        "receive_id_type": receive_id_type,
        "msg_type": msg_type,
        "content": json.dumps(content, ensure_ascii=False),
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ======================================================================
# Markdown → 飞书富文本转换
# ======================================================================

def md_to_feishu_post(markdown_text, title=None):
    """
    将 Markdown 文本转换为飞书富文本消息格式。
    飞书 post 格式: {zh_cn: {title, content: [[{tag, text}, ...], ...]}}
    """
    lines = markdown_text.strip().split("\n")
    content_lines = []
    detected_title = title

    for line in lines:
        line = line.rstrip()

        # 提取标题
        if line.startswith("# ") and not detected_title:
            detected_title = line[2:].strip()
            continue

        # 二级标题 → 加粗
        if line.startswith("## "):
            text = line[3:].strip()
            content_lines.append([{"tag": "text", "text": f"\n{'─' * 20}\n"},
                                  {"tag": "text", "text": f"【{text}】\n"}])
            continue

        # 三级标题
        if line.startswith("### "):
            text = line[4:].strip()
            content_lines.append([{"tag": "text", "text": f"\n▸ {text}\n"}])
            continue

        # 表格行 → 纯文本保留
        if line.startswith("|"):
            # 跳过分割线
            if re.match(r'\|[\s\-|]+\|', line):
                continue
            content_lines.append([{"tag": "text", "text": line + "\n"}])
            continue

        # 列表项
        if line.startswith("- ") or line.startswith("* "):
            content_lines.append([{"tag": "text", "text": f"  • {line[2:].strip()}\n"}])
            continue
        if re.match(r'^\d+\.\s', line):
            content_lines.append([{"tag": "text", "text": f"  {line.strip()}\n"}])
            continue

        # 引用
        if line.startswith("> "):
            content_lines.append([{"tag": "text", "text": f"  │ {line[2:].strip()}\n"}])
            continue

        # 分割线
        if line.strip() == "---":
            content_lines.append([{"tag": "text", "text": f"{'─' * 30}\n"}])
            continue

        # 空行
        if not line.strip():
            content_lines.append([{"tag": "text", "text": "\n"}])
            continue

        # 普通文本
        content_lines.append([{"tag": "text", "text": line + "\n"}])

    return {
        "zh_cn": {
            "title": detected_title or "工作报告",
            "content": content_lines
        }
    }


def md_to_feishu_card(markdown_text, title=None):
    """
    将 Markdown 转换为飞书卡片消息格式。
    卡片支持原生 Markdown 渲染。
    """
    # 提取标题
    if not title:
        match = re.match(r'^#\s+(.+)', markdown_text.strip())
        if match:
            title = match.group(1)
            markdown_text = markdown_text[match.end():].strip()

    # 飞书卡片 Markdown 限制：去除 HTML 标签
    clean_md = re.sub(r'<[^>]+>', '', markdown_text)

    # 分块（飞书卡片单个 markdown 元素有大小限制）
    chunks = split_markdown(clean_md, max_size=3000)

    elements = []
    for chunk in chunks:
        elements.append({"tag": "markdown", "content": chunk})

    return {
        "header": {
            "title": {"tag": "plain_text", "content": title or "工作报告"},
            "template": "blue"
        },
        "elements": elements
    }


def split_markdown(text, max_size=3000):
    """将长文本分块，按段落边界切分"""
    if len(text) <= max_size:
        return [text]

    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_size:
            if current:
                chunks.append(current)
            current = line
        else:
            current += "\n" + line if current else line
    if current:
        chunks.append(current)
    return chunks


# ======================================================================
# 分段发送（处理超长报告）
# ======================================================================

def send_report(markdown_text, receive_id, receive_id_type, fmt="post", title=None):
    """
    发送报告到飞书。
    如果报告过长，自动分段发送。
    """
    results = []

    if fmt == "card":
        card_content = md_to_feishu_card(markdown_text, title)
        result = send_message(receive_id, receive_id_type, "interactive", card_content)
        results.append(result)
    elif fmt == "text":
        # 纯文本，去除 Markdown 标记
        clean = re.sub(r'[#*`]', '', markdown_text)
        if len(clean) > 4000:
            # 分段
            for i in range(0, len(clean), 4000):
                chunk = clean[i:i+4000]
                result = send_message(receive_id, receive_id_type, "text", {"text": chunk})
                results.append(result)
        else:
            result = send_message(receive_id, receive_id_type, "text", {"text": clean})
            results.append(result)
    else:
        # 默认富文本 post
        post_content = md_to_feishu_post(markdown_text, title)
        # 检查大小
        content_str = json.dumps(post_content, ensure_ascii=False)
        if len(content_str) > MAX_POST_SIZE:
            # 分段发送
            lines = markdown_text.split("\n")
            mid = len(lines) // 2
            part1 = "\n".join(lines[:mid])
            part2 = "\n".join(lines[mid:])
            post1 = md_to_feishu_post(part1, title=f"{title or '报告'}（上）")
            post2 = md_to_feishu_post(part2, title=f"{title or '报告'}（下）")
            results.append(send_message(receive_id, receive_id_type, "post", post1))
            results.append(send_message(receive_id, receive_id_type, "post", post2))
        else:
            result = send_message(receive_id, receive_id_type, "post", post_content)
            results.append(result)

    return results


# ======================================================================
# Main
# ======================================================================

def main():
    parser = argparse.ArgumentParser(description="将报告发送到飞书")
    parser.add_argument("--input", required=True, help="报告 Markdown 文件路径")
    parser.add_argument("--chat-id", help="群聊 ID")
    parser.add_argument("--user-id", help="用户 open_id")
    parser.add_argument("--format", choices=["post", "card", "text"], default="post",
                        help="消息格式: post(富文本), card(卡片), text(纯文本)")
    parser.add_argument("--title", help="报告标题（可选）")
    args = parser.parse_args()

    if not args.chat_id and not args.user_id:
        print("❌ 请指定 --chat-id 或 --user-id", file=sys.stderr)
        sys.exit(1)

    # 读取报告
    with open(args.input, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    # 确定接收者
    if args.chat_id:
        receive_id = args.chat_id
        receive_id_type = "chat_id"
    else:
        receive_id = args.user_id
        receive_id_type = "open_id"

    # 发送
    print(f"📤 正在发送到飞书...", file=sys.stderr)
    results = send_report(markdown_text, receive_id, receive_id_type,
                          fmt=args.format, title=args.title)

    for i, r in enumerate(results):
        msg_id = r.get("message_id", "unknown")
        print(f"  ✅ 消息 {i+1} 已发送 (message_id: {msg_id})", file=sys.stderr)

    print(f"\n✅ 发送完成，共 {len(results)} 条消息", file=sys.stderr)


if __name__ == "__main__":
    main()
