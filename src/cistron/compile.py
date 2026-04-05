"""Rule compiler — takes individual rule files with impact frontmatter
and compiles them into flat documents. The polymerase pattern."""

import re
from pathlib import Path

from .parser import parse_frontmatter

VALID_IMPACTS = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
IMPACT_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def parse_rule(path: Path) -> dict:
    """Parse a single rule file. Returns dict with frontmatter fields plus body."""
    fm = parse_frontmatter(path)
    body = fm.get("_body", "").strip()

    # Strip leading ## heading from body for compact output
    clean_body = re.sub(r"^## .+\n+", "", body, count=1).strip()
    # Strip leading **bold title.** if present (migration artifact)
    clean_body = re.sub(r"^\*\*[^*]+\*\*\s*", "", clean_body).strip()

    # Infer section from filename prefix if no section field
    stem = path.stem
    prefix = stem.split("-")[0] if "-" in stem else "misc"

    return {
        "path": path,
        "name": stem,
        "title": fm.get("title", stem),
        "impact": fm.get("impact", "MEDIUM"),
        "impact_description": fm.get("impactDescription", ""),
        "tags": [t.strip() for t in fm.get("tags", "").split(",") if t.strip()],
        "section": fm.get("section", prefix),
        "body": clean_body,
    }


def parse_sections_file(path: Path) -> dict[str, dict]:
    """Parse a _sections.md taxonomy file.

    Format:
        ## 1. Section Title (prefix)
        **Impact:** CRITICAL
        **Description:** Description text.
    """
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    sections = {}
    for block in re.split(r"(?=^## \d+\. )", text, flags=re.MULTILINE):
        m = re.match(r"^## (\d+)\.\s+(.+?)\s+\((\w+)\)\s*$", block, re.MULTILINE)
        if not m:
            continue
        number = int(m.group(1))
        title = m.group(2).strip()
        prefix = m.group(3).strip()
        impact_m = re.search(r"\*\*Impact:\*\*\s+(\w+)", block)
        impact = impact_m.group(1) if impact_m else "MEDIUM"
        desc_m = re.search(r"\*\*Description:\*\*\s+(.+?)(?=\n\n|$)", block, re.DOTALL)
        desc = desc_m.group(1).strip() if desc_m else ""
        sections[prefix] = {
            "number": number,
            "title": title,
            "impact": impact,
            "description": desc,
        }
    return sections


def load_rules(rules_dir: Path) -> list[dict]:
    """Load all rule files from a directory (excluding files starting with _)."""
    if not rules_dir.exists():
        return []
    rules = []
    for f in sorted(rules_dir.glob("*.md")):
        if f.name.startswith("_"):
            continue
        rules.append(parse_rule(f))
    return rules


def compile_flat(
    rules: list[dict],
    sections: dict | None = None,
    impact_filter: set[str] | None = None,
    header: str = "",
) -> str:
    """Compile rules into a flat document grouped by section.

    Args:
        rules: List of parsed rule dicts from load_rules().
        sections: Taxonomy from parse_sections_file(), used for ordering and titles.
        impact_filter: Optional set like {"CRITICAL", "HIGH"} to filter rules.
        header: Optional document header text prepended to output.
    """
    if impact_filter:
        rules = [r for r in rules if r["impact"] in impact_filter]

    grouped: dict[str, list[dict]] = {}
    for rule in rules:
        section = rule["section"]
        grouped.setdefault(section, []).append(rule)

    sections = sections or {}
    sorted_prefixes = sorted(
        grouped.keys(),
        key=lambda p: sections.get(p, {}).get("number", 99),
    )

    lines = []
    if header:
        lines.append(header)
        lines.append("")

    for prefix in sorted_prefixes:
        sec = sections.get(prefix, {"title": prefix.title(), "number": 99})
        lines.append(f"### {sec['title']}")

        section_rules = sorted(
            grouped[prefix],
            key=lambda r: (IMPACT_ORDER.get(r["impact"], 9), r["title"]),
        )

        for rule in section_rules:
            body = rule["body"]
            first_para = []
            for bl in body.splitlines():
                if bl.strip() == "" or bl.startswith("```") or bl.startswith("**Incorrect") or bl.startswith("**Correct"):
                    break
                first_para.append(bl)
            compact = " ".join(first_para).strip()
            lines.append(f"- **{rule['title']}.** {compact}" if compact else f"- **{rule['title']}.**")

        lines.append("")

    return "\n".join(lines)


def extract_test_cases(rules: list[dict]) -> list[dict]:
    """Extract Incorrect/Correct code examples as structured eval cases."""
    cases = []
    for rule in rules:
        # Re-read body to get the full content (clean_body may have stripped examples)
        text = rule["path"].read_text(encoding="utf-8")
        for m in re.finditer(
            r"\*\*(Incorrect|Correct|Don't|Do)\b[^*]*\*\*[:\s]*\n*```(\w+)?\n(.*?)```",
            text,
            re.DOTALL,
        ):
            label = m.group(1)
            lang = m.group(2) or "python"
            code = m.group(3).strip()
            case_type = "bad" if label in ("Incorrect", "Don't") else "good"
            cases.append({
                "rule_title": rule["title"],
                "impact": rule["impact"],
                "type": case_type,
                "language": lang,
                "code": code,
            })
    return cases
