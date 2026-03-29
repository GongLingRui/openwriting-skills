#!/usr/bin/env python3
import sys, os; sys.path.insert(0, "/home/node/clawd/.pylib/lib/python3.11/site-packages")
"""
batch_generate_feishu.py — 飞书版批量报告生成

从飞书多维表格读取数据 → MiniMax 生成6类报告 → 发送到飞书群聊（默认）或导出DOCX（可选）

用法:
  # 发送到飞书群聊
  python3 batch_generate_feishu.py --app-token <TOKEN> --chat-id <CHAT_ID>

  # 导出为 DOCX
  python3 batch_generate_feishu.py --app-token <TOKEN> --docx --output-dir ~/Desktop

环境变量:
  MINIMAX_API_KEY       MiniMax API 密钥
  MINIMAX_BASE_URL      MiniMax API 地址 (默认 https://api.minimaxi.com/v1)
  FEISHU_TOOLKIT_URL    feishu-toolkit 服务地址 (默认 http://127.0.0.1:8002)
"""

import json
import os
import re
import subprocess
import sys
import time

try:
    import requests
except ImportError:
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY",
    "sk-cp-HnHVB6YD5O58F7s0STe-rQKbp0MiQJOwu5jnnjUTWSuqGJiI10RY0hg8i2n9M3SUeS2GGyc42lGAppW7LywvutEjwySiG49h_ftN5FcH5twUMq48FN53iu0")
MINIMAX_BASE_URL = os.environ.get("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1")
MODEL = "MiniMax-M2.5-highspeed"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
PARSE_BITABLE = os.path.join(SCRIPT_DIR, "parse_bitable.py")
SEND_FEISHU = os.path.join(SCRIPT_DIR, "send_feishu.py")
GENERATE_DOCX = os.path.join(SCRIPT_DIR, "generate_docx.py")


def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def build_system_prompt():
    skill_md = read_file(os.path.join(SKILL_DIR, "SKILL.md"))
    if skill_md.startswith("---"):
        parts = skill_md.split("---", 2)
        if len(parts) >= 3:
            skill_md = parts[2].strip()
    analysis_rules = read_file(os.path.join(SKILL_DIR, "references", "analysis-rules.md"))
    report_templates = read_file(os.path.join(SKILL_DIR, "references", "report-templates.md"))
    return f"""你是一个 AI 助手，具备以下 Skill：

{skill_md}

以下是分析规则参考：

{analysis_rules}

以下是报告模板参考：

{report_templates}

当前日期：{time.strftime('%Y年%m月%d日')}

注意：
- 用户提供的数据来自飞书多维表格，已包含里程碑节点计划
- 严禁使用任何人称代词（我、我们、我部、本部门等）
- 一律使用"公司""财务资产部"等第三人称表述
"""


def parse_bitable_data(app_token, weeks=2, tasklist=True):
    cmd = [sys.executable, PARSE_BITABLE,
           "--app-token", app_token,
           "--weeks", str(weeks),
           "--format", "summary"]
    if tasklist:
        cmd.append("--tasklist")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 解析失败: {result.stderr}", file=sys.stderr)
        return None
    return result.stdout


def call_minimax(system_prompt, user_message, max_tokens=8000):
    url = f"{MINIMAX_BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MINIMAX_API_KEY}"
    }
    payload = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3
    }
    response = requests.post(url, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    data = response.json()
    if "choices" in data and len(data["choices"]) > 0:
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        # 去除思考过程
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content, usage
    return None, {}


def send_to_feishu(report_md, title, chat_id=None, user_id=None, fmt="post"):
    """将报告发送到飞书"""
    tmp_file = f"/tmp/feishu_report_{int(time.time())}.md"
    with open(tmp_file, 'w', encoding='utf-8') as f:
        f.write(report_md)

    cmd = [sys.executable, SEND_FEISHU, "--input", tmp_file, "--format", fmt, "--title", title]
    if chat_id:
        cmd.extend(["--chat-id", chat_id])
    elif user_id:
        cmd.extend(["--user-id", user_id])
    else:
        print("⚠️ 未指定接收者，跳过飞书发送", file=sys.stderr)
        return

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 飞书发送失败: {result.stderr}", file=sys.stderr)
    else:
        print(result.stderr, end="")

    os.unlink(tmp_file)


def save_as_docx(report_md, filename, title, date, output_dir):
    """保存为 DOCX"""
    tmp_file = f"/tmp/feishu_report_{int(time.time())}.md"
    with open(tmp_file, 'w', encoding='utf-8') as f:
        f.write(report_md)

    output_path = os.path.join(output_dir, filename)
    cmd = [sys.executable, GENERATE_DOCX,
           "--input", tmp_file,
           "--output", output_path,
           "--title", title,
           "--date", date]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ DOCX 生成失败: {result.stderr}", file=sys.stderr)
    else:
        print(f"  📄 {filename}")

    os.unlink(tmp_file)


# 6类报告配置
REPORT_CONFIGS = [
    {
        "name": "周进度简报",
        "filename": "稽核风控工作周进度简报.docx",
        "title": "稽核风控工作周进度简报",
        "date": time.strftime("%Y年第%W周"),
        "weeks": 2,
        "prompt": """以下是本周的工作任务跟踪数据（来自飞书多维表格），请生成一份「周进度简报」。

{data}

请按照报告模板中的「一、周进度简报」格式输出。"""
    },
    {
        "name": "月度管理报告",
        "filename": f"稽核风控{time.strftime('%Y年%m月')}月度管理报告.docx",
        "title": f"关于{time.strftime('%m')}月份稽核风控工作进展情况的报告",
        "date": time.strftime("%Y年%m月"),
        "weeks": 4,
        "prompt": """以下是最近4周的工作任务跟踪数据，请生成一份「月度管理报告」。

{data}

请按照报告模板中的「二、月度管理报告」格式输出。约2000字。
禁止使用第一人称（我、我们、我部等）。"""
    },
    {
        "name": "项目节点报告",
        "filename": "稽核风控项目节点专题报告.docx",
        "title": "关于当前关键工作节点进展情况的专题报告",
        "date": time.strftime("%Y年%m月"),
        "weeks": 4,
        "prompt": """以下是最近4周的工作任务跟踪数据，请围绕当前最紧迫的关键节点生成一份「项目节点报告」。

{data}

请按照报告模板中的「三、项目节点报告」格式输出。约1500字。
涉及节点风险时，必须引用里程碑计划中的具体时间节点。
禁止使用第一人称。"""
    },
    {
        "name": "团队绩效分析",
        "filename": "稽核风控全团队绩效分析报告.docx",
        "title": "稽核风控工作团队绩效分析",
        "date": f"分析周期：{time.strftime('%Y年%m月')}",
        "weeks": 4,
        "prompt": """以下是全部团队最近4周的工作任务跟踪数据，请生成一份覆盖所有团队的「团队绩效分析」报告。

{data}

请对数据中出现的每一个团队（按"负责团队"字段识别）逐一单独分析，包含：
一、基本情况  二、任务完成质量  三、亮点与不足  四、管理建议
最后加「综合对比」章节。

注意：
- 必须为数据中出现的每一个团队单独分析，不可遗漏或合并
- 量化指标必须基于实际数据计算
- 禁止使用第一人称"""
    },
    {
        "name": "风险预警专报",
        "filename": f"稽核风控风险预警专报_{time.strftime('%Y%m')}.docx",
        "title": "稽核风控工作风险预警专报",
        "date": time.strftime("%Y年%m月%d日"),
        "weeks": 4,
        "prompt": """以下是最近4周的工作任务跟踪数据，请全面扫描所有异常情况，生成一份「风险预警专报」。

{data}

请系统性识别风险，按预警级别从高到低排列，每个风险独立成节。
涉及节点风险时，必须引用里程碑计划中的具体时间节点。
禁止使用第一人称。"""
    },
    {
        "name": "季度汇报材料",
        "filename": f"稽核风控{time.strftime('%Y年')}季度工作情况报告.docx",
        "title": f"关于公司{time.strftime('%Y年')}稽核风控工作情况的报告",
        "date": time.strftime("%Y年%m月"),
        "weeks": 6,
        "prompt": """以下是最近6周的工作任务跟踪数据，请生成一份「季度汇报材料」草稿。

{data}

请按照报告模板中的「六、季度/半年汇报材料」格式输出。约3000字。
严格央企公文汇报体，"一是……二是……三是……"分层递进。
严禁使用任何人称代词（我、我们、我部、本部门等），一律使用"公司""财务资产部"等第三人称表述。"""
    },
]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="飞书版批量报告生成")
    parser.add_argument("--app-token", required=True, help="飞书多维表格 App Token")
    parser.add_argument("--chat-id", help="飞书群聊 ID（默认输出方式）")
    parser.add_argument("--user-id", help="飞书用户 open_id")
    parser.add_argument("--feishu-format", choices=["post", "card"], default="post",
                        help="飞书消息格式")
    parser.add_argument("--docx", action="store_true", help="输出为 DOCX 文件")
    parser.add_argument("--output-dir", default=os.path.expanduser("~/Desktop"),
                        help="DOCX 输出目录")
    parser.add_argument("--reports", nargs="+",
                        choices=["weekly", "monthly", "milestone", "team", "risk", "quarterly"],
                        help="指定生成的报告类型（默认全部）")
    args = parser.parse_args()

    if not args.docx and not args.chat_id and not args.user_id:
        print("❌ 请指定输出方式: --chat-id / --user-id (飞书) 或 --docx (文件)", file=sys.stderr)
        sys.exit(1)

    system_prompt = build_system_prompt()

    # 确定要生成的报告
    report_map = {"weekly": 0, "monthly": 1, "milestone": 2, "team": 3, "risk": 4, "quarterly": 5}
    if args.reports:
        configs = [REPORT_CONFIGS[report_map[r]] for r in args.reports]
    else:
        configs = REPORT_CONFIGS

    print(f"{'='*60}")
    print(f"🔧 飞书版批量报告生成")
    print(f"   模型: {MODEL}")
    print(f"   报告数量: {len(configs)}")
    print(f"   输出: {'DOCX → ' + args.output_dir if args.docx else '飞书消息'}")
    print(f"{'='*60}")

    for i, rconfig in enumerate(configs):
        print(f"\n{'='*60}")
        print(f"📋 [{i+1}/{len(configs)}] {rconfig['name']}")
        print(f"{'='*60}")

        # 解析数据
        data = parse_bitable_data(args.app_token, weeks=rconfig["weeks"])
        if not data:
            print(f"  ❌ 数据解析失败，跳过")
            continue

        # 调用 MiniMax
        user_msg = rconfig["prompt"].format(data=data)
        print(f"  🚀 调用 {MODEL}...")
        content, usage = call_minimax(system_prompt, user_msg)
        if not content:
            print(f"  ❌ API 返回空")
            continue

        tokens_in = usage.get("prompt_tokens", 0)
        tokens_out = usage.get("completion_tokens", 0)
        print(f"  ✅ 生成完成 (输入:{tokens_in}, 输出:{tokens_out})")

        # 输出
        if args.docx:
            save_as_docx(content, rconfig["filename"], rconfig["title"],
                         rconfig["date"], args.output_dir)
        else:
            send_to_feishu(content, rconfig["title"],
                           chat_id=args.chat_id, user_id=args.user_id,
                           fmt=args.feishu_format)

    print(f"\n{'='*60}")
    print(f"✅ 完成！共生成 {len(configs)} 份报告")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
