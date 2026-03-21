## Why

The current depth chart pipeline does not enforce a single identity-first matching strategy across batter, SP, and RP ingestion. As a result, some rows still fall back through inconsistent name-based paths and can attach season stats to the wrong player when names are ambiguous.

The release boundary is also too loose. Candidate, QA, review, and warning-oriented data are still published under `public/data/latest/`, which makes internal workflow state part of the public contract even when the frontend does not render it.

## What Changes

- Standardize batter, SP, and RP ingestion around source roster identity from Fangraphs depth chart rows, using the row's player identity as the primary key for stats resolution.
- Forbid silent cross-player fallback when the source roster identity and resolved stats identity disagree; ambiguous rows must remain unresolved or be sent through review instead of publishing mismatched stats.
- Move QA, review, candidate, and other operator-only artifacts out of the public release surface so `public/data/latest/` only contains consumer-facing release data.
- Shrink the public depth chart snapshot contract so it excludes warning diagnostics, review state, and other release-workflow metadata that are not meant for frontend consumption.
- Preserve operator auditability through internal artifacts and release-gating outputs without exposing those fields in the public site payloads.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `depth-charts-data-pipeline`: change ingestion and publication requirements so roster-row identity is the authoritative basis for player matching, ambiguous mismatches are gated instead of silently accepted, and internal QA/review artifacts are separated from public release artifacts.
- `depth-charts-web-ui`: change the public data contract so production pages consume consumer-facing release snapshots only and no longer depend on or expose operator workflow metadata from published files.

## Impact

- Affected code: `scripts/fangraphs_batter_sync.py`, `scripts/fangraphs_sp_sync.py`, `scripts/fangraphs_rp_sync.py`, `scripts/depth_charts_pipeline.py`, `scripts/regression_checks.py`, `scripts/qa_go_no_go.py`, and frontend data-loading code in `public/app.js`.
- Affected artifacts: candidate/review/QA outputs, release snapshot shape, and the filesystem layout for public vs internal build outputs.
- Affected systems: Fangraphs ingestion, release gating, operator review workflow, rollback/recovery flow, and the public static site data contract.
