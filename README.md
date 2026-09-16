# mobilityDCAT-AP - Repository Structure POC

> **This is a proof of concept** demonstrating a proposed repository layout and GitHub Actions publishing workflow for mobilityDCAT-AP. It is not the authoritative specification repository.
>
> The goal is to validate the branch-based versioning strategy (see `PLAN.md`) before applying it to the main repo.

## Source files

All hand-authored source files live in `src/`. Generated artefacts go in `dist/` and must not be edited by hand.

## Structure

```
src/
├── index.html                 # ReSpec specification document (entry point)
├── config.js                  # ReSpec configuration
├── mobilitydcat-ap.rdf        # Ontology - primary source of truth (RDF/XML)
├── tables/                    # HTML property tables included by index.html
├── examples/                  # Worked examples
├── figures/                   # UML diagrams and logo
├── shaclShapes/               # SHACL validation constraints
├── validationFiles/           # Granular SHACL shapes (one per class)
├── js/                        # Custom JavaScript
├── scripts/                   # Build scripts (Python); see DEVELOPMENT.md
├── enterpriseArchitectFiles/  # EA model (.qea)
└── appendices/                # Appendix content (placeholder)
```

## Branching convention

| Ref | Type | Published to |
|-----|------|-------------|
| `main` | Latest draft | `drafts/latest/` |
| `release/1.0.0` | Release branch | `releases/1.0.0/` |
| `draft/1.0.0-draft-0.1` | Draft tag | `drafts/1.0.0-draft-0.1/` |

## GitHub Actions workflows

Workflows live in `.github/workflows/` and publish to the `gh-pages` branch.

The workflow set is split into:
- **Caller workflows** for branch/tag-specific publishing logic.
- **Reusable workflows** for build and publish implementation.

| Workflow | Type | Trigger | Publishes to |
|----------|------|---------|-------------|
| `build-main.yml` | caller | push to `main` (path-filtered), manual | `drafts/latest/` |
| `build-draft.yml` | caller | push of `draft/*` tag, manual | `drafts/<version>/` |
| `build-release.yml` | caller | push to `release/*`, manual | `releases/<version>/` and `releases/latest/` if branch version equals `LATEST_RELEASE` |
| `promote-latest.yml` | standalone | manual only | updates `LATEST_RELEASE` on `main` with the provided version value and copies `releases/<version>/` to `releases/latest/` |
| `reusable-build.yml` | reusable | called by caller workflows | builds `dist/` and uploads artifact (default: `spec-dist`) |
| `reusable-publish-gh-pages.yml` | reusable | called by caller workflows | deploys artifact into a target directory on `gh-pages` |

The build and deploy steps are split into two reusable workflows called by the above:

| Reusable workflow | Purpose |
|-------------------|---------|
| `reusable-build.yml` | Full build pipeline - serialise RDF, copy assets, build ReSpec spec, validate HTML, check references; uploads `dist/` as an artifact |
| `reusable-publish-gh-pages.yml` | Pre-clean target directory on `gh-pages`, then deploy the artifact via plain `git` |

### Trigger and guard details

- `build-main.yml` only triggers automatically when these paths change on `main`:
  - `src/**`
  - `package.json`
  - `pyproject.toml`
- `build-draft.yml` extracts the version by stripping the `draft/` prefix from `GITHUB_REF_NAME` and fails fast if it is not version-like.
- `build-release.yml` extracts the version by stripping the `release/` prefix from `GITHUB_REF_NAME` and fails fast if it is not version-like.

### Build pipeline details (`reusable-build.yml`)

The reusable build runs on Ubuntu with a 10-minute timeout and:

1. Checks out source (`actions/checkout@v6`).
2. Sets up Node.js 24 and Python 3.12.
3. Installs `uv` and dependencies (`npm install`, `uv sync`).
4. Adds `node_modules/.bin` to `PATH`.
5. Runs:
	- `src/scripts/serialise.py`
	- `src/scripts/copy-assets.py`
	- `src/scripts/build-spec.py`
6. Runs non-blocking quality checks (`continue-on-error: true`):
	- `html-validate dist/index.html`
	- `src/scripts/check-refs.py`
7. Uploads `dist/` as artifact `spec-dist` (or custom `artifact_name` input).

### Publish pipeline details (`reusable-publish-gh-pages.yml`)

For a caller-supplied `destination_dir`:

1. Downloads the build artifact.
2. Checks out `gh-pages` into `gh-pages-out`.
3. Deletes and recreates `destination_dir` on `gh-pages`.
4. Copies all generated files from `dist/`.
5. Commits (`chore: publish <destination_dir>`) and pushes; if no diff exists, it logs "Nothing to publish".

### Artifact flow

- `reusable-build.yml` exposes `artifact_name` as a workflow output.
- Caller workflows pass `needs.build.outputs.artifact_name` into `reusable-publish-gh-pages.yml`.
- This keeps artifact naming centralized in one place.

### Build scripts under `src/scripts/`

The Python scripts in `src/scripts/` are the implementation behind local `mise` commands and CI build steps.

| Script | What it does | Used by CI |
|--------|--------------|------------|
| `clean.py` | Deletes and recreates `dist/` to ensure a fresh output directory. | Indirectly via project build command; not called directly in `reusable-build.yml`. |
| `serialise.py` | Parses `src/*.rdf` and `src/examples/*.rdf` with rdflib and writes `.ttl` + `.jsonld` into `dist/` and `dist/examples/`. | Yes |
| `copy-assets.py` | Copies static assets into `dist/`: root `mobilitydcat-ap.rdf`, all files from `src/examples/`, plus `src/figures/` and `src/shaclShapes/` directories (when present). | Yes |
| `build-spec.py` | Runs `respec --localhost -s src/index.html -o dist/index.html` to generate the rendered specification. | Yes |
| `check-refs.py` | Scans `dist/index.html` and reports any broken internal links (`href="#..."` without matching `id`). Exits non-zero when broken refs are found. | Yes (non-blocking) |
| `serve.py` | Starts a local HTTP server at `http://localhost:8080` for live ReSpec preview at `src/index.html`. | No |

Notes:
- In CI, `html-validate` and `check-refs.py` are currently configured as non-blocking (`continue-on-error: true`), so publishing can continue even if they report issues.
- `build-spec.py` uses `--localhost` because ReSpec/Chromium cannot resolve `data-include` dependencies correctly from `file://` URLs.

### Promoting a release to `releases/latest/`

`LATEST_RELEASE` in the repo root (on `main`) holds the version number currently marked as latest (e.g. `1.0.0`). On every push to a `release/*` branch, `build-release.yml` reads this file from `main` - if the version matches the branch, it also deploys to `releases/latest/` automatically.

This means:
- Hotfixes to the current latest release branch update `releases/latest/` automatically, just like they update the versioned directory.
- Hotfixes to older release branches only update their versioned directory - `releases/latest/` is untouched.

To promote a different version to latest:

- Run `promote-latest.yml` from the Actions tab and enter the version number.
- It updates `LATEST_RELEASE` on `main` (so future hotfixes to that branch also update `releases/latest/`).
- It also copies the already-built `releases/X.Y.Z/` to `releases/latest/` on `gh-pages` immediately - no rebuild needed.
- It fails fast if `releases/X.Y.Z/` does not exist on `gh-pages`.
- Promotion is an explicit, deliberate step - no version silently becomes latest without a human decision.

## Building locally

See `DEVELOPMENT.md` for prerequisites, setup, and build instructions.
