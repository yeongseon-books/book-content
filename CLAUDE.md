# Claude Code Project Context

This is `yeongseon-books/book-content`, a private content repository for technical book series (blog-first, book-later model).

## Key References

- **Rules for all agents**: [AGENTS.md](./AGENTS.md) — read this first (Prime Directive, post structure, quality gates)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md) — repo layout, pipelines, asset flow
- **Content model**: [CONTENT_MODEL.md](./CONTENT_MODEL.md) — front matter, status lifecycle, series.yaml
- **Style**: [STYLE_GUIDE.md](./STYLE_GUIDE.md) + `.sisyphus/skills/humanize-korean/quick-rules.md`
- **Blog writing**: [BLOG_WRITING_GUIDE.md](./BLOG_WRITING_GUIDE.md)
- **eBook writing**: [EBOOK_WRITING_GUIDE.md](./EBOOK_WRITING_GUIDE.md)
- **Asset policy**: [ASSET_POLICY.md](./ASSET_POLICY.md)

## Quick Start

```bash
make check          # validate content, generated outputs, and links
make docs-build     # build MkDocs site (strict mode)
pytest tests/       # run unit tests
```

## Repository Layout

```
content/<series>/{ko,en}/   # canonical source (Markdown)
content/<series>/medium/    # generated Medium HTML (do not edit)
assets/<series>/<NN>/       # image assets
scripts/                    # check_*, lint_*, build_*, export_*, sync_*
.sisyphus/medium/           # Medium pipeline tools
.sisyphus/style/            # Korean style checker
tests/                      # unit tests
```

## Conventions

- Canonical source lives in `content/<series>/{ko,en}/`.
- `series.yaml` is the single source of truth for the series catalog.
- Run `make check` before every commit.
- Golden references (e.g. `content/azure-app-service-101/ko/01-what-is-app-service.md`) must never be modified.
- Application code language is Python. Shell/YAML/JSON/Dockerfile are for config and CLI steps only.
- No emoji in content or code output.
