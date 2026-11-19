#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod-experience-ingest / ingest_experience.py

把他人的 MOD 开发经验资料（文档/案例/笔记/规则）规范化导入到目标知识库的
experiences/ 目录，更新 README 索引，并输出可复核的验证报告。

设计约束：
- 只用 Python 标准库，UTF-8 显式读写（避免 BOM）。
- 默认 dry-run：只预览和校验，不写任何文件（符合专家"纯咨询不擅自动手"铁律）。
  只有显式传 --commit 才真正落库。
- 目标目录默认自动推导为同级 jjxf-project-engineer/experiences，可用 --target 覆盖。
- 去重：按 (date, title) 与已有条目比对；可选 --force 覆盖。

用法：
  python3 ingest_experience.py <manifest.json> [--target DIR] [--commit] [--force]
  python3 ingest_experience.py --emit-template > manifest.example.json
"""

import argparse
import datetime as _dt
import json
import os
import re
import sys

VALID_LAYERS = {"通用", "项目"}
VALID_CATEGORIES = {
    "版本变化", "新坑", "新工具用法", "作者问题", "口径更新", "性能", "其它",
}
VALID_SEVERITY = {"info", "warn", "error"}
VALID_LINES = {"4.6", "4.7", "通用"}

REQUIRED_ITEM_FIELDS = [
    "date", "title", "source", "layer", "category", "lines", "severity",
]
BODY_SECTIONS = [
    ("phenomenon", "现象 / 触发"),
    ("conclusion", "结论"),
    ("evidence", "依据 / 实测数字"),
    ("fix", "正确处理 / 修法"),
    ("prevention", "防范措施"),
    ("related", "关联"),
]

TEMPLATE = {
    "intake_id": "2026-11-19-community-example",
    "intake_date": "2026-11-19",
    "contributor": "来源作者或社区昵称/链接（脱敏后）",
    "source_type": "doc | case | note | rule",
    "items": [
        {
            "date": "2026-11-19",
            "title": "一句话说清这条经验",
            "source": "来源：谁的反馈/哪个项目阶段/哪次实测；外部资料请脱敏",
            "layer": "通用 | 项目",
            "category": "版本变化 | 新坑 | 新工具用法 | 作者问题 | 口径更新 | 性能 | 其它",
            "lines": ["通用"],
            "severity": "info | warn | error",
            "supersedes": "",
            "phenomenon": "什么情况下遇到；错误请贴日志原文，变量用 {…}",
            "conclusion": "一句话答案，结论先行",
            "evidence": "- 出处：文件/日志/命令输出\n- 关键数字：...",
            "fix": "1. 可直接复制的步骤或命令",
            "prevention": "怎么防止复发",
            "related": "- 相关稳定知识：references/xx.md §章节",
        }
    ],
}


def read_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def slugify(title, maxlen=40):
    s = re.sub(r"[^\w\u4e00-\u9fff\-]+", "-", title.strip(), flags=re.UNICODE)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return (s[:maxlen] or "untitled")


def default_target():
    """同级 jjxf-project-engineer/experiences。"""
    here = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(here)                      # .../skills/mod-experience-ingest
    sibling = os.path.join(os.path.dirname(skill_root), "jjxf-project-engineer", "experiences")
    return os.path.normpath(sibling)


def validate_manifest(manifest):
    """返回 (errors, warnings)。结构性校验，不臆测内容真伪。"""
    errors, warnings = [], []
    if not isinstance(manifest, dict):
        return ["清单根节点必须是 JSON 对象"], warnings
    if not manifest.get("items"):
        errors.append("items 为空：没有可导入的经验条目")
    for key in ("intake_id", "intake_date", "contributor", "source_type"):
        if not manifest.get(key):
            warnings.append("清单缺少元数据 %s（建议填写，便于溯源）" % key)
    seen = set()
    for i, item in enumerate(manifest.get("items", [])):
        tag = "items[%d]" % i
        if not isinstance(item, dict):
            errors.append("%s 必须是对象" % tag)
            continue
        for field in REQUIRED_ITEM_FIELDS:
            if field not in item or (isinstance(item[field], str) and not item[field].strip()):
                errors.append("%s 缺少必填字段 %s" % (tag, field))
        if item.get("layer") not in VALID_LAYERS:
            errors.append("%s.layer 必须是 %s 之一" % (tag, sorted(VALID_LAYERS)))
        cat = item.get("category")
        if cat not in VALID_CATEGORIES:
            errors.append("%s.category '%s' 不在允许集合 %s" % (tag, cat, sorted(VALID_CATEGORIES)))
        if item.get("severity") not in VALID_SEVERITY:
            errors.append("%s.severity 必须是 %s 之一" % (tag, sorted(VALID_SEVERITY)))
        lines = item.get("lines")
        if not isinstance(lines, list) or not lines:
            errors.append("%s.lines 必须是非空数组" % tag)
        else:
            bad = [x for x in lines if x not in VALID_LINES]
            if bad:
                errors.append("%s.lines 含非法值 %s（允许 %s）" % (tag, bad, sorted(VALID_LINES)))
            if item.get("layer") == "通用" and any(x in ("4.6", "4.7") for x in lines):
                warnings.append("%s 是通用层但 lines 写了具体引擎线，请确认是否应填 ['通用']" % tag)
        # 日期格式
        d = item.get("date", "")
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(d)):
            errors.append("%s.date '%s' 应为 YYYY-MM-DD" % (tag, d))
        # 正文六段完整性
        for key, label in BODY_SECTIONS:
            if not str(item.get(key, "")).strip():
                warnings.append("%s 缺少正文段 '%s'（建议补齐，经验条目质量门槛要求）" % (tag, label))
        # 重复
        k = (str(item.get("date", "")), str(item.get("title", "")).strip())
        if k in seen:
            errors.append("%s 与本清单内另一条 (date,title) 重复：%s" % (tag, k))
        seen.add(k)
    return errors, warnings


def q(v):
    """YAML 值安全引用：统一双引号并转义内部双引号/换行。"""
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").strip() + '"'


def render_entry(item, intake):
    lines = json.dumps(item["lines"], ensure_ascii=False)
    fm = [
        "---",
        "date: %s" % q(item["date"]),
        "title: %s" % q(item["title"]),
        "source: %s" % q(item.get("source", intake.get("contributor", ""))),
        "layer: %s" % q(item["layer"]),
        "category: %s" % q(item["category"]),
        "lines: %s" % lines,
        "severity: %s" % q(item["severity"]),
        "supersedes: %s" % q(item.get("supersedes", "")),
        "ingest_by: mod-experience-ingest",
        "intake_id: %s" % q(intake.get("intake_id", "")),
        "---",
        "",
        "# %s" % item["title"].strip(),
        "",
    ]
    for key, label in BODY_SECTIONS:
        fm.append("## %s" % label)
        fm.append(str(item.get(key, "")).strip() or "（待补充）")
        fm.append("")
    return "\n".join(fm).rstrip() + "\n"


def existing_index(target):
    """读取目标 experiences 目录现有条目的 (date,title) 集合与 README 文本。"""
    pairs, files = set(), []
    if os.path.isdir(target):
        for fn in os.listdir(target):
            if fn.endswith(".md") and fn.lower() != "readme.md":
                files.append(fn)
                try:
                    txt = open(os.path.join(target, fn), "r", encoding="utf-8-sig").read()
                    m_t = re.search(r'^title:\s*"?(.*?)"?\s*$', txt, re.M)
                    m_d = re.search(r'^date:\s*"?(.*?)"?\s*$', txt, re.M)
                    if m_t and m_d:
                        pairs.add((m_d.group(1).strip(), m_t.group(1).strip()))
                except OSError:
                    pass
    readme = os.path.join(target, "README.md")
    readme_txt = ""
    if os.path.isfile(readme):
        readme_txt = open(readme, "r", encoding="utf-8-sig").read()
    return pairs, files, readme_txt


def plan(manifest, target):
    """生成落库计划：每条 -> 目标文件名 + 内容 + 是否与已有冲突。"""
    pairs, files, readme_txt = existing_index(target)
    planned, conflicts = [], []
    used_names = set()
    for item in manifest["items"]:
        name = "%s-%s.md" % (item["date"], slugify(item["title"]))
        if name in used_names:
            name = "%s-%s-2.md" % (item["date"], slugify(item["title"]))
        used_names.add(name)
        key = (str(item["date"]), str(item["title"]).strip())
        dup = key in pairs or name in files
        content = render_entry(item, manifest)
        planned.append({"filename": name, "path": os.path.join(target, name),
                        "content": content, "duplicate": dup})
        if dup:
            conflicts.append(name)
    return planned, conflicts, readme_txt


def updated_readme(readme_txt, manifest, planned, target):
    """在 '已有条目' 段追加新条目链接。幂等：已存在链接则跳过。"""
    if not readme_txt:
        readme_txt = "# 增量经验区（experiences/）\n\n## 已有条目\n\n"
    lines = readme_txt.splitlines()
    anchor = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("## 已有条目"):
            anchor = i
            break
    if anchor is None:
        lines += ["", "## 已有条目", ""]
        anchor = len(lines) - 2
    insert_at = anchor + 1
    added = []
    for p, item in zip(planned, manifest["items"]):
        link = "- %s · %s → [文件](./%s)" % (
            item["date"], item["title"].strip(), p["filename"])
        if link in lines:
            continue
        # 插到 "已有条目" 段首（最新在前）
        lines.insert(insert_at, link)
        insert_at += 1
        added.append(link)
    return "\n".join(lines).rstrip() + "\n", added


def main(argv=None):
    ap = argparse.ArgumentParser(description="MOD 经验资料规范化导入器")
    ap.add_argument("manifest", nargs="?", help="规范化清单 JSON 路径")
    ap.add_argument("--target", help="目标 experiences 目录（默认同级 jjxf-project-engineer/experiences）")
    ap.add_argument("--commit", action="store_true", help="真正写入文件；默认仅 dry-run 预览")
    ap.add_argument("--force", action="store_true", help="遇到重复仍覆盖写入")
    ap.add_argument("--report", help="把验证报告写入指定 JSON 文件")
    ap.add_argument("--emit-template", action="store_true", help="输出清单模板到 stdout 并退出")
    args = ap.parse_args(argv)

    if args.emit_template:
        print(json.dumps(TEMPLATE, ensure_ascii=False, indent=2))
        return 0
    if not args.manifest:
        ap.error("需要 manifest 路径（或用 --emit-template 查看模板）")

    try:
        manifest = read_json(args.manifest)
    except (OSError, ValueError) as e:
        print("❌ 读取清单失败：%s" % e, file=sys.stderr)
        return 2

    errors, warnings = validate_manifest(manifest)
    target = os.path.abspath(args.target) if args.target else default_target()
    planned, conflicts, readme_txt = plan(manifest, target) if not errors else ([], [], "")

    report = {
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "manifest": os.path.abspath(args.manifest),
        "target": target,
        "mode": "commit" if args.commit else "dry-run",
        "item_count": len(manifest.get("items", [])),
        "errors": errors,
        "warnings": warnings,
        "planned_files": [p["filename"] for p in planned],
        "conflicts": conflicts,
        "written": [],
    }

    print("=" * 60)
    print("MOD 经验资料导入 · %s" % report["mode"].upper())
    print("=" * 60)
    print("清单：%s" % report["manifest"])
    print("目标：%s" % target)
    print("条目数：%d" % report["item_count"])
    if errors:
        print("\n❌ 校验未通过（%d 项错误）：" % len(errors))
        for e in errors:
            print("   - %s" % e)
    if warnings:
        print("\n⚠ 警告（%d 项）：" % len(warnings))
        for w in warnings:
            print("   - %s" % w)
    if not errors:
        print("\n✅ 结构校验通过")
        print("\n落库计划：")
        for p in planned:
            flag = "  [重复!]" if p["duplicate"] else ""
            print("   - %s%s" % (p["filename"], flag))
        if conflicts and not args.force:
            print("\n⚠ 检测到 %d 个与现有条目重复的条目；未加 --force 将跳过这些。" % len(conflicts))

    if args.commit and not errors:
        os.makedirs(target, exist_ok=True)
        for p, item in zip(planned, manifest["items"]):
            if p["duplicate"] and not args.force:
                continue
            with open(p["path"], "w", encoding="utf-8", newline="\n") as f:
                f.write(p["content"])
            report["written"].append(p["filename"])
        new_readme, added = updated_readme(readme_txt, manifest, planned, target)
        readme_path = os.path.join(target, "README.md")
        with open(readme_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new_readme)
        report["readme_added"] = added
        print("\n✅ 已写入 %d 个条目 + 更新 README 索引" % len(report["written"]))
    elif not args.commit:
        print("\n[dry-run] 未写入任何文件。确认无误后加 --commit 执行落库。")

    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("报告已写入：%s" % args.report)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
