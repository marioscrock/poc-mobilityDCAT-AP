# Notes - pending fixes/changes

Date: 2026-09-16

## 1) Serialization direction change on main

- On `main`, TTL files should be the canonical source format both for the ontology and examples.
- Corresponding JSON-LD (.jsonld) and RDF/XML (.rdf) serializations should be generated from TTL.
- Update build logic accordingly (including examples where applicable).
- Update workflow/README wording that currently implies RDF/XML source -> TTL conversion.
- Keep script and documentation updates aligned in one change set for this transition.
- Review `copy-assets.py` for TTL-first behavior so copied inputs and generated outputs remain consistent.

## 2) Reflect new structure drafts/latest from current mobilityDCAT-AP repository

- `validationFiles/` is no longer part of the repository structure.
- `enterpriseArchitectFiles/` is no longer part of the repository structure.
- Remove/adjust all references to these folders in docs and build scripts.
- Ensure build/publish steps do not expect these folders to exist.
- Verify no stale references remain in README, DEVELOPMENT guide, and script comments.
- Change `examples/` with new files `minimum`/`complete` in TTL
- Change `shaclShapes/` with new files
- Other changes?

## 3) Draft naming convention

- Add explicit documentation for draft naming conventions (decide if we want to keep the current one).
- Clarify the exact format for draft tags and examples (e.g. major/minor/patch and draft suffix pattern).
- Ensure README and workflow comments use the same convention wording.
- Add one canonical naming rule in README with one concrete example and mirror the same wording in workflow comments.

## 4) Document repository "by procedures"

- Organise documentation "by procedures", e.g., how to create a new draft, how to edit the current draft, how to create a release, how to publish a release, etc.
- Include the expected sequence, for example to publish a release something like:
	- Create a `release/X.Y.Z` branch from `main`.
	- Push the branch so `build-release.yml` publishes `releases/X.Y.Z/`.
	- Run `promote-latest.yml` with `X.Y.Z` when that release should become latest.
	- Confirm `LATEST_RELEASE` was updated on `main` and `releases/latest/` was refreshed on `gh-pages`.

### 5) Draft vs release config.js checklist (to document)

- Add a dedicated checklist showing which `src/config.js` values must be set when creating:
	- a new draft publication;
	- a new release publication.
- TODO Mario discuss required changes with Peter by reviewing old "procedure"defined by Lina for publication and the new set of metadata for v3.0.0
	- Some wording may still need direct HTML-level adjustment after build (depending on ReSpec templates and policy wording).

## 6) Presentation of refactoring objectives

- Create a short presentation that explains the objectives of this repository refactoring.
- Cover these core goals explicitly:
	- Improve project structure and maintainability
	- Facilitate local development and onboarding
	- Automate publishing operations and release flow

## 7) ReSpec CI timeout issue and tested fix

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

## 8) Agent instructions interoperability

- Evaluate removing `CLAUDE.md` in favor of a more generic `agent.md`-style guidance file for broader tool interoperability.
- Define a neutral structure that can be consumed by different coding agents, not tied to a single vendor/tool.

## 9) [FUTURE WORK] Dev mode SHACL validation for example

- Add a development-mode validation step to check example files against SHACL shapes.
- Scope for future implementation (not now):
	- Validate examples in `src/examples/` against shapes in `src/shaclShapes/`.
	- Integrate as an optional dev command (for local quality checks).
	- Optionally wire it into CI later, after local workflow is stable.
