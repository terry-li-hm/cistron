"""YAML frontmatter parser supporting multiline strings."""

from pathlib import Path


def parse_frontmatter(path: Path) -> dict:
    """Extract YAML frontmatter from a markdown file, including multiline strings.

    Returns dict with all frontmatter fields plus:
        _body: everything after the closing ---
        _lines: line count of the body
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    fm: dict = {}
    current_key: str | None = None
    current_val_lines: list[str] = []
    is_multiline = False

    for line in parts[1].strip().splitlines():
        if not line.startswith(" ") and not line.startswith("\t") and ":" in line:
            if current_key and is_multiline:
                fm[current_key] = " ".join(current_val_lines).strip()
            key, _, val = line.partition(":")
            current_key = key.strip()
            val = val.strip().strip("'\"")
            if val in (">", ">-", "|", "|-"):
                is_multiline = True
                current_val_lines = []
            elif val:
                fm[current_key] = val
                is_multiline = False
            else:
                is_multiline = False
        elif is_multiline and current_key:
            current_val_lines.append(line.strip())

    if current_key and is_multiline:
        fm[current_key] = " ".join(current_val_lines).strip()

    fm["_body"] = parts[2]
    fm["_lines"] = len(parts[2].splitlines())
    return fm
