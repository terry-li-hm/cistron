"""cistron command-line interface — compile, catalog, extract-tests."""

import json
import sys
from pathlib import Path

from .catalog import compile_catalog, load_skills
from .compile import compile_flat, extract_test_cases, load_rules, parse_sections_file


def print_help():
    print("""cistron -- knowledge-as-code compiler for agent skills

Usage:
    cistron compile <rules-dir> [-o OUTPUT] [--critical] [--sections FILE]
        Compile rule files into a flat document.
        --critical         Include only CRITICAL and HIGH impact rules
        --sections FILE    Path to _sections.md taxonomy file
        -o, --output FILE  Output file (default: stdout)

    cistron extract-tests <rules-dir> [-o OUTPUT]
        Extract Incorrect/Correct code examples as eval JSON.

    cistron catalog <skills-dir> [-o OUTPUT]
        Generate overview document for a skill collection.

For linting, use agnix (https://github.com/agent-sh/agnix).
For skill generation, use SkillForge (https://pypi.org/project/skillforge/).
""")


def _get_output(args: list[str]) -> Path | None:
    if "-o" in args:
        return Path(args[args.index("-o") + 1])
    if "--output" in args:
        return Path(args[args.index("--output") + 1])
    return None


def _get_flag(args: list[str], flag: str) -> str | None:
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            return args[idx + 1]
    return None


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print_help()
        return 0

    cmd = args[0]
    if cmd not in ("compile", "catalog", "extract-tests"):
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print_help()
        return 1

    if len(args) < 2:
        print(f"cistron {cmd}: missing directory argument", file=sys.stderr)
        return 1

    target_dir = Path(args[1])
    if not target_dir.exists():
        print(f"Directory not found: {target_dir}", file=sys.stderr)
        return 1

    out_file = _get_output(args)

    if cmd == "compile":
        sections_path = _get_flag(args, "--sections")
        sections = parse_sections_file(Path(sections_path)) if sections_path else {}
        if not sections:
            parent_sections = target_dir.parent / "_sections.md"
            if parent_sections.exists():
                sections = parse_sections_file(parent_sections)

        rules = load_rules(target_dir)
        if not rules:
            print(f"No rule files found in {target_dir}", file=sys.stderr)
            return 1

        impact_filter = {"CRITICAL", "HIGH"} if "--critical" in args else None
        output = compile_flat(rules, sections, impact_filter=impact_filter)

        if out_file:
            out_file.write_text(output + "\n", encoding="utf-8")
            n = sum(1 for r in rules if not impact_filter or r["impact"] in impact_filter)
            print(f"Compiled {n} rules to {out_file}", file=sys.stderr)
        else:
            print(output)
        return 0

    if cmd == "extract-tests":
        rules = load_rules(target_dir)
        cases = extract_test_cases(rules)
        output = json.dumps(cases, indent=2)
        if out_file:
            out_file.write_text(output + "\n", encoding="utf-8")
            bad = sum(1 for c in cases if c["type"] == "bad")
            good = sum(1 for c in cases if c["type"] == "good")
            print(f"Extracted {len(cases)} test cases to {out_file}", file=sys.stderr)
            print(f"  bad: {bad}, good: {good}", file=sys.stderr)
        else:
            print(output)
        return 0

    if cmd == "catalog":
        skills = load_skills(target_dir)
        if not skills:
            print(f"No SKILL.md files found in {target_dir}", file=sys.stderr)
            return 1
        output = compile_catalog(skills)
        if out_file:
            out_file.write_text(output + "\n", encoding="utf-8")
            print(f"Cataloged {len(skills)} skills to {out_file}", file=sys.stderr)
        else:
            print(output)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
