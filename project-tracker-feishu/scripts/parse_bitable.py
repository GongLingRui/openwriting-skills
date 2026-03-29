#!/usr/bin/env python3
import sys, os; sys.path.insert(0, "/home/node/clawd/.pylib/lib/python3.11/site-packages")
"""
parse_bitable.py — 从飞书多维表格读取工作任务跟踪数据

替代 parse_tracker.py 的飞书适配版本。
通过 feishu-toolkit HTTP API 读取 Bitable 数据，
输出与 parse_tracker.py 相同格式的 summary 文本。

用法:
  python3 parse_bitable.py --app-token <APP_TOKEN> [--weeks 2] [--team 英大长安] [--tasklist]
  python3 parse_bitable.py --app-token <APP_TOKEN> --format json

环境变量:
  FEISHU_TOOLKIT_URL  feishu-toolkit 服务地址 (默认 http://127.0.0.1:8002)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests", file=sys.stderr)
    sys.exit(1)

FEISHU_TOOLKIT_URL = os.environ.get("FEISHU_TOOLKIT_URL", "http://127.0.0.1:8002")


# ======================================================================
# Bitable API 封装
# ======================================================================

def api_get(endpoint, params=None):
    url = f"{FEISHU_TOOLKIT_URL}{endpoint}"
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_post(endpoint, data):
    url = f"{FEISHU_TOOLKIT_URL}{endpoint}"
    resp = requests.post(url, json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def list_tables(app_token):
    """列出多维表格中的所有数据表"""
    return api_get("/bitable/tables", {"app_token": app_token})


def list_fields(app_token, table_id):
    """获取数据表的字段定义"""
    return api_get("/bitable/fields", {"app_token": app_token, "table_id": table_id})


def search_records(app_token, table_id, field_names=None, page_size=500):
    """查询所有记录"""
    data = {
        "app_token": app_token,
        "table_id": table_id,
        "page_size": page_size,
    }
    if field_names:
        data["field_names"] = field_names
    return api_post("/bitable/records/search", data)


# ======================================================================
# 数据表自动发现
# ======================================================================

# 工作跟踪表的字段关键词
TRACKER_FIELD_KEYWORDS = ["板块", "任务分类", "具体任务", "负责团队", "重要程度"]
# 任务清单表的字段关键词
TASKLIST_FIELD_KEYWORDS = ["模块", "工作任务", "里程碑", "频率"]


def detect_tables(app_token):
    """
    自动识别工作跟踪表和任务清单表。
    返回 (tracker_table_id, tasklist_table_id)
    """
    tables_resp = list_tables(app_token)
    tables = tables_resp.get("tables", [])

    tracker_tid = None
    tasklist_tid = None

    for t in tables:
        tid = t["table_id"]
        tname = t.get("name", "")

        # 先按名称猜测
        if "跟踪" in tname or "进度" in tname:
            tracker_tid = tid
            continue
        if "清单" in tname or "任务清单" in tname:
            tasklist_tid = tid
            continue

        # 按字段匹配
        fields_resp = list_fields(app_token, tid)
        field_names = [f["field_name"] for f in fields_resp.get("fields", [])]
        field_text = " ".join(field_names)

        tracker_hits = sum(1 for kw in TRACKER_FIELD_KEYWORDS if kw in field_text)
        tasklist_hits = sum(1 for kw in TASKLIST_FIELD_KEYWORDS if kw in field_text)

        if tracker_hits >= 3 and not tracker_tid:
            tracker_tid = tid
        elif tasklist_hits >= 2 and not tasklist_tid:
            tasklist_tid = tid

    return tracker_tid, tasklist_tid


# ======================================================================
# 字段动态映射
# ======================================================================

def build_field_map(fields):
    """
    根据字段名称动态映射到逻辑角色。
    返回 {role: field_name} 字典。
    """
    fmap = {}
    progress_fields = []  # 周进展相关字段

    for f in fields:
        name = f["field_name"]
        fname_lower = name.lower()

        if "板块" in name:
            fmap["domain"] = name
        elif "任务分类" in name or "分类" in name:
            fmap["category"] = name
        elif "具体任务" in name or "任务名" in name:
            fmap["task"] = name
        elif "重要程度" in name or "重要" in name:
            fmap["priority"] = name
        elif "牵头" in name or "配合" in name or "角色" in name:
            fmap["role"] = name
        elif "负责团队" in name or "团队" in name:
            fmap["team"] = name
        elif "序号" in name:
            fmap["seq"] = name
        elif "进展" in name or "计划" in name or "问题" in name:
            progress_fields.append(name)

    fmap["progress_fields"] = progress_fields
    return fmap


def build_tasklist_field_map(fields):
    """任务清单表的字段映射"""
    fmap = {}
    for f in fields:
        name = f["field_name"]
        if "模块" in name:
            fmap["module"] = name
        elif "频率" in name or "频次" in name:
            fmap["frequency"] = name
        elif "工作任务" in name or "任务" in name:
            fmap["task"] = name
        elif "里程碑" in name or "节点" in name:
            fmap["milestone"] = name
    return fmap


# ======================================================================
# 数据解析
# ======================================================================

def extract_cell_text(value):
    """从 Bitable 字段值中提取纯文本"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        # 富文本字段: [{text: "xxx", type: "text"}, ...]
        # 人员字段: [{id: "ou_xxx", name: "张三"}, ...]
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.append(item.get("text", item.get("name", str(item))))
            else:
                parts.append(str(item))
        return " ".join(parts).strip()
    if isinstance(value, dict):
        return value.get("text", value.get("name", str(value)))
    return str(value)


def parse_tracker_data(app_token, tracker_table_id, team_filter=None, weeks=2):
    """
    读取工作跟踪表数据，返回结构化的任务列表。
    """
    # 获取字段结构
    fields_resp = list_fields(app_token, tracker_table_id)
    fields = fields_resp.get("fields", [])
    fmap = build_field_map(fields)

    # 获取所有记录
    all_field_names = [f["field_name"] for f in fields]
    records_resp = search_records(app_token, tracker_table_id, field_names=all_field_names)
    records = records_resp.get("items", [])

    tasks = []
    for rec in records:
        f = rec.get("fields", {})

        domain = extract_cell_text(f.get(fmap.get("domain", ""), ""))
        category = extract_cell_text(f.get(fmap.get("category", ""), ""))
        task_name = extract_cell_text(f.get(fmap.get("task", ""), ""))
        priority = extract_cell_text(f.get(fmap.get("priority", ""), ""))
        role = extract_cell_text(f.get(fmap.get("role", ""), ""))
        team = extract_cell_text(f.get(fmap.get("team", ""), ""))
        seq = extract_cell_text(f.get(fmap.get("seq", ""), ""))

        if not task_name:
            continue

        # 过滤团队
        if team_filter and team_filter not in team:
            continue

        # 提取进展字段
        progress_data = {}
        for pf in fmap.get("progress_fields", []):
            val = extract_cell_text(f.get(pf, ""))
            if val:
                progress_data[pf] = val

        tasks.append({
            "domain": domain,
            "category": category,
            "task": task_name,
            "priority": priority,
            "role": role,
            "team": team,
            "seq": seq,
            "progress": progress_data,
        })

    return tasks, fmap


def parse_tasklist_data(app_token, tasklist_table_id):
    """
    读取任务清单表数据，返回结构化的任务清单。
    """
    fields_resp = list_fields(app_token, tasklist_table_id)
    fields = fields_resp.get("fields", [])
    fmap = build_tasklist_field_map(fields)

    all_field_names = [f["field_name"] for f in fields]
    records_resp = search_records(app_token, tasklist_table_id, field_names=all_field_names)
    records = records_resp.get("items", [])

    items = []
    for rec in records:
        f = rec.get("fields", {})
        module = extract_cell_text(f.get(fmap.get("module", ""), ""))
        frequency = extract_cell_text(f.get(fmap.get("frequency", ""), ""))
        task = extract_cell_text(f.get(fmap.get("task", ""), ""))
        milestone = extract_cell_text(f.get(fmap.get("milestone", ""), ""))

        if not task:
            continue

        items.append({
            "module": module,
            "frequency": frequency,
            "task": task,
            "milestone": milestone,
        })

    return items


# ======================================================================
# 输出格式化（与 parse_tracker.py 兼容）
# ======================================================================

def generate_summary(tasks, fmap):
    """生成与 parse_tracker.py 兼容的 summary 文本"""
    lines = []
    lines.append("=" * 60)
    lines.append("稽核风控工作任务跟踪数据")
    lines.append(f"数据来源: 飞书多维表格")
    lines.append(f"任务总数: {len(tasks)} 项")
    lines.append("=" * 60)

    # 按板块分组
    domains = {}
    for t in tasks:
        d = t["domain"] or "其他"
        if d not in domains:
            domains[d] = []
        domains[d].append(t)

    for domain, domain_tasks in domains.items():
        lines.append(f"\n## {domain}")
        lines.append(f"  任务数: {len(domain_tasks)}")

        for t in domain_tasks:
            lines.append(f"\n  ### {t['task']}")
            if t["priority"]:
                lines.append(f"    重要程度: {t['priority']}")
            if t["team"]:
                lines.append(f"    负责团队: {t['team']}")
            if t["role"]:
                lines.append(f"    角色: {t['role']}")

            # 输出进展数据
            for field_name, value in t["progress"].items():
                lines.append(f"    {field_name}: {value}")

    # 统计信息
    lines.append("\n" + "=" * 60)
    lines.append("统计汇总")
    lines.append("=" * 60)

    teams = {}
    for t in tasks:
        team = t["team"] or "未分配"
        if team not in teams:
            teams[team] = {"total": 0, "priority": 0, "has_progress": 0, "has_issue": 0}
        teams[team]["total"] += 1
        if t["priority"] and "重点" in t["priority"]:
            teams[team]["priority"] += 1
        if any("进展" in k for k in t["progress"]):
            teams[team]["has_progress"] += 1
        if any("问题" in k and v for k, v in t["progress"].items()):
            teams[team]["has_issue"] += 1

    lines.append(f"\n| 团队 | 总任务 | 重点任务 | 有进展 | 有问题 |")
    lines.append(f"|------|--------|---------|--------|--------|")
    for team, stats in teams.items():
        lines.append(f"| {team} | {stats['total']} | {stats['priority']} | {stats['has_progress']} | {stats['has_issue']} |")

    return "\n".join(lines)


def generate_tasklist_summary(items):
    """生成任务清单摘要文本"""
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("稽核风控工作任务清单（里程碑计划）")
    lines.append(f"数据来源: 飞书多维表格")
    lines.append(f"任务总数: {len(items)} 项")
    lines.append("=" * 60)

    current_module = None
    for item in items:
        if item["module"] and item["module"] != current_module:
            current_module = item["module"]
            lines.append(f"\n## {current_module}")

        lines.append(f"\n  - 任务: {item['task']}")
        if item["frequency"]:
            lines.append(f"    频率: {item['frequency']}")
        if item["milestone"]:
            lines.append(f"    里程碑计划: {item['milestone']}")

    return "\n".join(lines)


# ======================================================================
# Main
# ======================================================================

def main():
    parser = argparse.ArgumentParser(description="从飞书多维表格读取工作任务跟踪数据")
    parser.add_argument("--app-token", required=True, help="多维表格 App Token")
    parser.add_argument("--tracker-table", help="工作跟踪表 table_id（自动检测则留空）")
    parser.add_argument("--tasklist-table", help="任务清单表 table_id（自动检测则留空）")
    parser.add_argument("--weeks", type=int, default=2, help="读取最近几周的数据")
    parser.add_argument("--team", help="按团队名称过滤")
    parser.add_argument("--format", choices=["summary", "json"], default="summary")
    parser.add_argument("--tasklist", action="store_true", help="同时读取任务清单表")
    args = parser.parse_args()

    # 自动检测数据表
    tracker_tid = args.tracker_table
    tasklist_tid = args.tasklist_table

    if not tracker_tid or (args.tasklist and not tasklist_tid):
        print("🔍 自动检测数据表...", file=sys.stderr)
        detected_tracker, detected_tasklist = detect_tables(args.app_token)
        if not tracker_tid:
            tracker_tid = detected_tracker
        if args.tasklist and not tasklist_tid:
            tasklist_tid = detected_tasklist

    if not tracker_tid:
        print("❌ 未找到工作跟踪表，请指定 --tracker-table", file=sys.stderr)
        sys.exit(1)

    # 解析数据
    tasks, fmap = parse_tracker_data(
        args.app_token, tracker_tid,
        team_filter=args.team, weeks=args.weeks
    )

    if args.format == "json":
        output = {"tasks": tasks, "field_map": fmap}
        if args.tasklist and tasklist_tid:
            output["tasklist"] = parse_tasklist_data(args.app_token, tasklist_tid)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(generate_summary(tasks, fmap))
        if args.tasklist:
            if tasklist_tid:
                items = parse_tasklist_data(args.app_token, tasklist_tid)
                print(generate_tasklist_summary(items))
            else:
                print("\n⚠️ 未找到任务清单表，跳过里程碑数据", file=sys.stderr)


if __name__ == "__main__":
    main()
