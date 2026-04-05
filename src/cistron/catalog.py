"""Skill catalog generator — produces an overview document from a collection."""

import re
from collections import defaultdict
from pathlib import Path

from .parser import parse_frontmatter


def extract_references(body: str) -> list[str]:
    """Extract skill cross-references from `## Calls` or `## Motifs` sections."""
    refs = []
    in_section = False
    in_code_block = False
    for line in body.splitlines():
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if re.match(r"^##\s+(Calls|Motifs|References)", line):
            in_section = True
            continue
        if in_section and line.startswith("##"):
            in_section = False
            continue
        if in_section and line.startswith("- "):
            m = re.match(r"- `([\w-]+)`", line) or re.match(r"- \[([\w-]+)\]", line)
            if m:
                refs.append(m.group(1))
    return refs


def load_skills(skills_dir: Path) -> list[dict]:
    """Load all SKILL.md files from a directory of skill subdirectories."""
    skills = []
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        skill_file = d / "SKILL.md"
        if not skill_file.exists():
            continue
        fm = parse_frontmatter(skill_file)
        body = fm.get("_body", "")
        skills.append({
            "name": fm.get("name", d.name),
            "dir": d.name,
            "description": fm.get("description", ""),
            "invocable": fm.get("user_invocable", "true").lower() != "false",
            "lines": fm.get("_lines", 0),
            "references": extract_references(body),
            "has_reference_doc": (d / "REFERENCE.md").exists(),
            "has_scripts": (d / "scripts").exists(),
        })
    return skills


def compile_catalog(skills: list[dict]) -> str:
    """Compile skills into a structured overview document."""
    from datetime import datetime

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = len(skills)
    invocable = sum(1 for s in skills if s["invocable"])

    lines = [
        f"# Skill Catalog -- {now}",
        "",
        f"Total: **{total}** skills ({invocable} invocable, {total - invocable} reference)",
        "",
    ]

    callers: dict[str, list[str]] = defaultdict(list)
    for s in skills:
        for ref in s["references"]:
            callers[ref].append(s["name"])

    most_referenced = sorted(callers.items(), key=lambda x: -len(x[1]))[:10]
    if most_referenced:
        lines.append("## Most Referenced")
        lines.append("")
        for name, caller_list in most_referenced:
            lines.append(f"- **{name}** ({len(caller_list)}): {', '.join(caller_list)}")
        lines.append("")

    lines.append("## All Skills")
    lines.append("")
    for s in sorted(skills, key=lambda x: x["name"]):
        inv = "" if s["invocable"] else " [ref]"
        desc = s["description"][:150] if s["description"] else "_(no description)_"
        lines.append(f"- **{s['name']}**{inv}: {desc}")

    return "\n".join(lines)
