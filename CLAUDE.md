# Personal Academic Website — Claude Code Guide

## Project Overview

Paul Vernus's personal academic website, built with Quarto.
Hosted at https://pvernus.github.io, deployed automatically
via GitHub Actions on every push to `main`.

---

## Key Files

| File | Purpose |
|------|---------|
| `index.qmd` | About/profile page (Jolla template, homepage) |
| `cv.qmd` | Curriculum vitae page |
| `_quarto.yml` | Site config — navbar, theme, search |
| `styles.css` | Custom CSS overrides (minimal by default) |
| `profile.jpg` | Profile photo |
| `.github/workflows/publish.yml` | CI/CD — builds and deploys to GitHub Pages |

## Directories to Leave Alone

- `_site/` — generated output, never edit manually, not committed
- `.quarto/` — Quarto cache, not committed
- `.claude/` — Claude Code config; agents/rules are for research workflows

---

## Common Commands

```bash
quarto preview      # Live preview with hot reload (use during editing)
quarto render       # Full build to _site/ (verify before committing)
quarto check        # Validate Quarto install and project structure
```

Deployment is automatic — push to `main` and GitHub Actions handles the rest.

---

## Conventions

### Content
- Page content lives in `.qmd` files at the repo root
- Front matter is minimal — only override what `_quarto.yml` already sets globally
- Do not add `format: html` to individual pages unless overriding site defaults
- `toc` is set globally in `_quarto.yml`; add `toc: false` in front matter to suppress per-page

### Styles
- Keep `styles.css` minimal — prefer Quarto theme defaults
- No inline styles in `.qmd` files

### Navigation
- Add new pages by creating a `.qmd` file, then adding it to `website.navbar` in `_quarto.yml`
- Do not create subdirectories for top-level nav pages

### Images
- Place images at the repo root alongside `.qmd` files
- Reference with relative paths: `image: profile.jpg`

### Git
- Commit source files only (`*.qmd`, `_quarto.yml`, `styles.css`, images)
- `_site/` is gitignored — never stage or commit it
- Commit message format: imperative mood, e.g. `Add research section to CV`

---

## Deployment

Push to `main` → GitHub Actions renders with Quarto → publishes to `gh-pages` branch →
GitHub Pages serves at https://pvernus.github.io.

**One-time manual setup** (after first workflow run creates the `gh-pages` branch):
GitHub repo → Settings → Pages → Source: branch `gh-pages`, folder `/ (root)`.

---

## What This File Does NOT Cover

Research paper workflows (LaTeX, R, agent orchestration, quality gates) are
governed by `.claude/rules/` and `.claude/agents/`. Those rules apply when
working on research manuscripts. This file covers the website only.
