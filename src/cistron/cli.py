"""cistron command-line interface."""

import sys
from pathlib import Path

from .catalog import compile_catalog, lint, load_skills


def print_help():
    print("""cistron -- treat agent skills as code

Usage:
    cistron catalog <skills-dir> [-o OUTPUT]   Generate catalog document
    cistron lint <skills-dir>                  Static analysis (exits 1 on issues)
    cistron stats <skills-dir>                 Summary statistics

Options:
    -o, --output FILE   Output file (default: stdout)

Each skills-dir should contain subdirectories with SKILL.md files.
""")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print_help()
        return 0

    cmd = args[0]
    if cmd not in ("catalog", "lint", "stats"):
        print(f"Unknown command: {cmd}", file=sys.stderr)
        print_help()
        return 1

    if len(args) < 2:
        print(f"cistron {cmd}: missing skills directory", file=sys.stderr)
        return 1

    skills_dir = Path(args[1])
    if not skills_dir.exists():
        print(f"Directory not found: {skills_dir}", file=sys.stderr)
        return 1

    skills = load_skills(skills_dir)

    if cmd == "lint":
        issues = lint(skills)
        if issues:
            print(f"{len(issues)} issues found:", file=sys.stderr)
            for i in issues:
                print(f"  {i}", file=sys.stderr)
            return 1
        print(f"All {len(skills)} skills valid.", file=sys.stderr)
        return 0

    if cmd == "stats":
        issues = lint(skills)
        invocable = sum(1 for s in skills if s["invocable"])
        print(f"Total: {len(skills)} ({invocable} invocable, {len(skills) - invocable} reference)")
        print(f"Issues: {len(issues)}")
        return 0

    if cmd == "catalog":
        output = compile_catalog(skills)
        out_file = None
        if "-o" in args:
            out_file = Path(args[args.index("-o") + 1])
        elif "--output" in args:
            out_file = Path(args[args.index("--output") + 1])

        if out_file:
            out_file.write_text(output + "\n", encoding="utf-8")
            print(f"Wrote {len(skills)} skills to {out_file}", file=sys.stderr)
        else:
            print(output)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
