## 1. Data Pipeline Refactor

- [x] 1.1 Extract a unified aggregation step that merges batter/SP/RP outputs into one `depth-charts.json` schema.
- [x] 1.2 Define and emit `meta` fields (`schemaVersion`, `season`, `generatedAt`, `buildId`, `buildStatus`).
- [x] 1.3 Add a quality-report generator that computes per-team and global warnings.
- [x] 1.4 Ensure fallback matching order is enforced (exact -> playerid -> normalized) and unresolved rows are recorded as warnings.

## 2. Validation and Publish Gates

- [x] 2.1 Implement structural gate checks (30 teams; Batter/SP/RP presence; section order Batter -> SP -> RP).
- [x] 2.2 Implement threshold-based warning gates and critical failure handling.
- [x] 2.3 Add atomic publish flow to promote only passing artifacts to `public/data/latest`.
- [x] 2.4 Preserve previous snapshot for rollback and document rollback command/process.

## 3. Frontend Foundation

- [x] 3.1 Initialize frontend app structure and data-loading layer for static JSON snapshots.
- [x] 3.2 Implement `/teams` with division grouping, status badges, and warning counts.
- [x] 3.3 Implement `/team/:abbr` with fixed section order tables (Batter, SP, RP).
- [x] 3.4 Add shared status bar showing season, generated timestamp, and build status.

## 4. UX and Data Transparency

- [x] 4.1 Add missing-value rendering (`--`) and row-level warning styling.
- [x] 4.2 Add warning summary/detail panels at team level.
- [x] 4.3 Ensure player links open Fangraphs source pages in new tabs.
- [x] 4.4 Implement filter/search URL state persistence on `/teams`.

## 5. Verification and Cutover

- [x] 5.1 Add regression checks for known critical rows (NYY SU7, TOR SU7, LAD Batter 5, ATH Batter 8).
- [x] 5.2 Validate QA gate checklist and record results for go/no-go decision.
- [x] 5.3 Remove Notion from standard delivery workflow documentation and operational runbook.
- [x] 5.4 Perform cutover to web UI as primary consumer surface and monitor first post-cutover run.
