# cistron

> In genetics, a cistron is the unit of functional knowledge in DNA — one gene, one function.

Cistron is a toolkit for treating agent skills as code. It turns scattered SKILL.md files into a codebase you can compile, validate, refactor, and evolve.

## The problem

Agent skills are having a moment. Repositories are clearing 100k stars. Every AI coding agent supports the SKILL.md format. But the tooling around skills is stuck in 2015 — individual markdown files, hand-maintained, hoped-for-the-best.

This is where CSS was before Sass. Where JavaScript was before TypeScript. Where documentation was before build pipelines. The file format works. The tooling doesn't exist yet.

## The toolkit

Cistron provides four tools that work together:

**`cistron compile`** — Takes individual rule files with frontmatter and compiles them into a flat document. Supports filtering by impact level (only critical rules for tight context windows), dual-output (lean index + flat compiled), and test-case extraction from Incorrect/Correct code examples.

**`cistron lint`** — Static analysis across your entire skill collection. Catches dead cross-references, name mismatches, empty descriptions, missing trigger phrases, bloated skills without reference files, and twelve other anti-patterns.

**`cistron catalog`** — Auto-generates a structured catalog of your skills with category detection, cross-reference graphs, size distribution, and issue reporting. The equivalent of API documentation, but for agent instructions.

**`cistron motifs`** — A shared abstraction layer. Patterns that appear across many skills (decision trees, audit workflows, verify gates, escalation chains) are extracted into reusable references. Skills link to motifs instead of duplicating.

## Why this matters

The best skill repos I've evaluated — Vercel's, Anthropic's, wshobson's — all converged on the same architecture independently: atomic units with metadata, a compilation step, validation, and selective expression. They just each built their own version, tied to their specific domain.

Cistron is the general toolkit. It works on any collection of SKILL.md files, regardless of domain. Skill authors stop reinventing the wheel. Skill consumers get predictable structure. Static analysis catches drift before it ships.

## The paradigm

Before this toolkit, skills were prose. You read them top to bottom and hoped they worked. You couldn't filter, validate, or refactor a collection of 188 skills any more systematically than you could refactor 188 Word documents.

After: skills are code. Individual files are source. The compiled document is a build artifact. A linter catches errors before deployment. Shared patterns are imported, not copy-pasted. Quality gates run in CI.

This isn't a new idea. It's an old idea applied to a new domain. Every mature language eventually develops this tooling. Skills are next.

## Status

Early. Published to claim the name and the idea. Full port coming.

## License

MIT
