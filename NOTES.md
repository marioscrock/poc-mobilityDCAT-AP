# Notes - pending fixes/changes

Date: 2026-09-16

## 1) Serialization direction change on main

- On `main`, TTL files should be the canonical source format.
- Corresponding JSON-LD and RDF/XML serializations should be generated from TTL.
- Update build logic accordingly (including examples where applicable).
- Update workflow/README wording that currently implies RDF/XML source -> TTL conversion.
- Keep script and documentation updates aligned in one change set for this transition.
- Review `copy-assets.py` for TTL-first behavior so copied inputs and generated outputs remain consistent.

## 2) Removed folders

- `validationFiles/` is no longer part of the repository structure.
- `enterpriseArchitectFiles/` is no longer part of the repository structure.
- Remove/adjust all references to these folders in docs and build scripts.
- Ensure build/publish steps do not expect these folders to exist.
- Verify no stale references remain in README, DEVELOPMENT guide, and script comments.

## 3) Draft naming convention

- Add explicit documentation for draft naming conventions.
- Clarify the exact format for draft tags and examples (e.g. major/minor/patch and draft suffix pattern).
- Ensure README and workflow comments use the same convention wording.
- Add one canonical naming rule in README with one concrete example and mirror the same wording in workflow comments.

## 4) CI validation policy

- Evaluate stricter release quality gates: keep validation checks non-blocking for drafts, but consider failing release builds on HTML validation or broken local references.

## 5) New release procedure documentation

- Add a dedicated README section describing how to create a new release end-to-end.
- Include the expected sequence, for example:
	- Create a `release/X.Y.Z` branch from `main`.
	- Push the branch so `build-release.yml` publishes `releases/X.Y.Z/`.
	- Run `promote-latest.yml` with `X.Y.Z` when that release should become latest.
	- Confirm `LATEST_RELEASE` was updated on `main` and `releases/latest/` was refreshed on `gh-pages`.
- Add a short checklist of preconditions (clean branch state, version naming convention, and required permissions to push/trigger workflows).
- Document a release-specific metadata update step (values vary at each release).
- For now, keep this as documentation only (no automation change yet).

### Release-specific changes table (to be applied per release)

| Item | Configure in `src/config.js` | Release value pattern |
|------|------------------------------|-----------------------|
| Canonical URL | `canonicalURI` | `https://w3id.org/mobilitydcat-ap/releases/X.Y.Z` |
| Document identifier (`id`) | Derived from `canonicalURI` in ReSpec JSON-LD output | `https://w3id.org/mobilitydcat-ap/releases/X.Y.Z` |
| Document type and recommendation labeling | `specStatus` (and related ReSpec status behavior) | `ED` |
| Publication date (`datePublished`, `publishDate`, `publishISODate`) | `publishDate` | `YYYY-MM-DD` and `YYYY-MM-DDT00:00:00.000Z` |
| Generated subtitle and visible publication label | `specStatus` + `publishDate` | `Recommendation DD Month YYYY` |
| Release URL metadata links | `latestVersion`, `thisVersionURI`, `prevVersionURI`, `latestVersionURI`, `prevRecURI`, `edDraftURI` | Values aligned with current `X.Y.Z` release |
| Publisher/copyright metadata | `copyrightHolder`, `copyrightURL` (plus relevant organization metadata fields) | Name/URL values for the release publisher |
| Document status and document version metadata | `otherLinks` entries (`Document status`, `Document version`) | Status and version values for this release |
| Reviewers metadata | `otherLinks` entry (`Reviewed by`) | `NAPCORE SWG 4.4`, `European NAP operators`, `Editors of DCAT-AP/SEMIC Team` |
| Approvers metadata | `otherLinks` entry (`Approved by`) | `NAPCORE SWG 4.4` |

Notes for this table:
- Values above are release-specific and should be reviewed for every `X.Y.Z`.
- For configurable fields, document only the `src/config.js` update path.
- Non-config checks remain part of release verification, e.g. confirming `releases/index.html` and `releases/X.Y.Z/index.html` are identical.

### Draft vs release config.js checklist (to document)

- Add a dedicated checklist showing which `src/config.js` values must be set when creating:
	- a new draft publication;
	- a new release publication.
- Include at least these keys in the draft vs release comparison:
	- `specStatus`
	- `publishDate`
	- `canonicalURI`
	- `latestVersion`
	- `thisVersionURI`
	- `prevVersionURI`
	- `latestVersionURI`
	- `prevRecURI`
	- `edDraftURI`
	- `otherLinks` (`Document status`, `Document version`, optional `Reviewed by`, `Approved by`)
	- `copyrightHolder` / `copyrightURL`

### HTML-only text items to verify with Peter

- Some wording may still need direct HTML-level adjustment after build (depending on ReSpec templates and policy wording).
- Add a review checkpoint with Peter to confirm exactly which statements, if any, must be edited in exported HTML instead of being controlled in `src/config.js`.
- Record the outcome as a stable rule for future releases/drafts.

## 6) Presentation of refactoring objectives

- Create a short presentation that explains the objectives of this repository refactoring.
- Cover these core goals explicitly:
	- Improve project structure and maintainability.
	- Facilitate local development and onboarding.
	- Automate publishing operations and release flow.

## 7) ReSpec CI timeout issue and tested fix (document only)

- Problem observed in CI during `uv run python src/scripts/build-spec.py`:
	- `FATAL TimeoutError: Navigation timeout ... exceeded` (example seen with 620 ms).
	- In local testing, failure could also occur later while waiting for ReSpec runtime readiness.
- Likely causes:
	- Timeout handling too aggressive for CI/network conditions.
	- Dependence on loading ReSpec remotely can make startup less stable.
- Fix tested successfully in a separate branch:
	- Use explicit ReSpec timeout in seconds via `--timeout`.
	- Use `--use-local` so the local installed ReSpec build is used instead of remote script loading.
	- Keep `--localhost` for correct `data-include` resolution.
	- Add command fallback to `npx respec` when `respec` is not directly on PATH.
- Main branch decision:
	- Do not apply this change now on `main`.
	- Keep this as a documented fix candidate to apply when needed.

## 8) Dev mode SHACL validation for examples (future work)

- Add a development-mode validation step to check example files against SHACL shapes.
- Scope for future implementation (not now):
	- Validate examples in `src/examples/` against shapes in `src/shaclShapes/`.
	- Integrate as an optional dev command (for local quality checks).
	- Optionally wire it into CI later, after local workflow is stable.

## 9) Agent instructions interoperability

- Evaluate removing `CLAUDE.md` in favor of a more generic `agent.md`-style guidance file for broader tool interoperability.
- Define a neutral structure that can be consumed by different coding agents, not tied to a single vendor/tool.
- Ensure any migration keeps the same essential project context (repository structure, build flow, workflow conventions, and release process).
- Add a transition note in documentation so contributors know which instruction file is canonical.

## 10) Reorganize DEVELOPMENT.md by task

- Rework `DEVELOPMENT.md` so it is organized by user tasks/workflows instead of tool-only sections.
- Add task-oriented sections, for example:
	- Update or publish a draft.
	- Create and publish a new release.
	- Promote a release to latest.
	- Run local validation and troubleshooting.
- For each task, include prerequisites, exact commands, expected outputs, and verification checks.
- Add quick links between `DEVELOPMENT.md`, `README.md`, and workflow names to reduce onboarding friction.
