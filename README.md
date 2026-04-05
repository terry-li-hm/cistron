# cistron

> In genetics, a cistron is the unit of functional knowledge in DNA — one gene, one function.

Cistron is a compiler and shared-abstraction layer for agent skills. It treats knowledge as code: atomic rule files get compiled into skill documents, common patterns get extracted into reusable motifs, and code examples in rules become evaluation test cases.

## What this is not

Cistron does not lint. It does not validate frontmatter or catch broken cross-references. For that, use [agnix](https://github.com/agent-sh/agnix) — 385 rules, auto-fix, LSP server, IDE plugins. It is the comprehensive validation tool and cistron defers to it completely.

Cistron does not generate skills. For wizard-based skill creation with pattern learning and personalized templates, use [SkillForge](https://pypi.org/project/skillforge/).

Cistron sits between these two. It is the compiler layer — the step where atomic knowledge units get turned into the skill documents that agnix validates and SkillForge orchestrates.

## Why this layer is missing

The best skill repositories I evaluated — Vercel's, Anthropic's, wshobson's — all converged on the same architecture independently. Each treated skills with many rules as source files that needed a build step. But each built their own version, tied to their specific domain. Vercel's compiler only works on their React best-practices skill. Anthropic's eval framework only works on their skill-creator. None of them generalized.

The ecosystem has linters. It has generators. It has runtime orchestrators. It does not have a general compiler. Cistron is that.

## The three tools

**`cistron compile`** takes a directory of individual rule files — each with impact frontmatter and optional Incorrect/Correct code examples — and produces a flat document. Supports filtering by impact level for tight context windows, dual output (lean index plus flat reference), and template-based layouts. This is the polymerase pattern applied to any rule collection.

**`cistron motifs`** manages the shared abstraction layer. Patterns that appear across many skills — decision trees, audit workflows, verify gates, escalation chains — are extracted into reusable references that skills link to instead of duplicating. Cistron ships with five built-in motifs and supports custom motif directories.

**`cistron extract-tests`** reads rule files and pulls out the Incorrect/Correct code examples as structured JSON. Feed this to an evaluation harness to measure whether a model actually follows the guidance. Turns coaching rules from vibes into measured compliance.

## The paradigm

Before compilation, knowledge lives in one big hand-maintained file. You hope it stays consistent. You cannot filter it, refactor it, or test it systematically. This is where CSS was before Sass, where JavaScript was before TypeScript, where documentation was before build pipelines.

After compilation, individual rules are source files. The compiled document is a build artifact. Filtering is a command-line flag. Test cases are extracted automatically. Shared patterns are imported, not copy-pasted. The same rule file can produce different outputs for different consumers — a lean index for smart agents with progressive disclosure, a flat document for backends without it.

This is an old idea applied to a new domain. Every mature language eventually grows this tooling. Agent knowledge is the next.

## Status

Early. Published to claim the namespace and the idea. Tested against a real 188-skill collection. Not yet on PyPI.

## License

MIT
