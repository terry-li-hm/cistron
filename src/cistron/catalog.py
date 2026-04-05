"""Skill catalog generator and static linter."""

import re
from collections import defaultdict
from pathlib import Path

from .parser import parse_frontmatter

VALID_IMPACTS = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


def extract_calls(body: str) -> list[str]:
    """Extract skill cross-references from `## Calls` or `## Motifs` sections."""
    calls = []
    in_section = False
    in_code_block = False
    for line in body.splitlines():
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if re.match(r"^##\s+(Calls|Motifs)", line):
            in_section = True
            continue
        if in_section and line.startswith("##"):
            in_section = False
            continue
        if in_section and line.startswith("- "):
            m = re.match(r"- `([\w-]+)`", line) or re.match(r"- \[([\w-]+)\]", line)
            if m:
                calls.append(m.group(1))
    return calls


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
            "calls": extract_calls(body),
            "has_reference": (d / "REFERENCE.md").exists(),
            "has_scripts": (d / "scripts").exists(),
            "retired": "retired" in body.lower()[:200],
        })
    return skills


def lint(skills: list[dict], external_tools: set[str] | None = None) -> list[str]:
    """Static analysis across the skill collection. Returns list of issue strings."""
    issues = []
    all_names = {s["name"] for s in skills}
    external = external_tools or set()

    for s in skills:
        name = s["name"]

        if not s["description"]:
            issues.append(f"{name}: missing description")
        elif len(s["description"]) < 20:
            issues.append(f"{name}: description too short ({len(s['description'])} chars)")

        has_trigger = bool(re.search(r'"[^"]+"', s["description"])) or "use when" in s["description"].lower()
        if s["invocable"] and not has_trigger:
            issues.append(f"{name}: invocable but no trigger phrases or 'Use when' in description")

        if s["lines"] > 800 and not s["has_reference"]:
            issues.append(f"{name}: {s['lines']} lines without REFERENCE.md (>800 = bloated)")

        if s["lines"] < 10 and not s["retired"]:
            issues.append(f"{name}: only {s['lines']} lines (stub?)")

        for call in s["calls"]:
            if call not in all_names and call not in external:
                issues.append(f"{name}: cross-ref to '{call}' but no such skill exists")

        if s["name"] != s["dir"]:
            issues.append(f"{s['dir']}/: name field '{s['name']}' does not match directory")

    return issues


def compile_catalog(skills: list[dict]) -> str:
    """Compile skills into a structured catalog document."""
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

    # Cross-reference frequency
    callers: dict[str, list[str]] = defaultdict(list)
    for s in skills:
        for call in s["calls"]:
            callers[call].append(s["name"])

    most_called = sorted(callers.items(), key=lambda x: -len(x[1]))[:10]
    if most_called:
        lines.append("## Most Referenced Skills")
        lines.append("")
        for name, caller_list in most_called:
            lines.append(f"- **{name}** ({len(caller_list)}): {', '.join(caller_list)}")
        lines.append("")

    # Full list
    lines.append("## All Skills")
    lines.append("")
    for s in sorted(skills, key=lambda x: x["name"]):
        inv = "" if s["invocable"] else " [ref]"
        desc = s["description"][:150] if s["description"] else "_(no description)_"
        lines.append(f"- **{s['name']}**{inv}: {desc}")

    issues = lint(skills)
    if issues:
        lines.append("")
        lines.append(f"## Issues ({len(issues)})")
        lines.append("")
        for issue in sorted(issues):
            lines.append(f"- {issue}")

    return "\n".join(lines)
