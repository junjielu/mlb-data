## Why

The current publication flow can detect missing rows and structural issues, but it cannot distinguish valid Fangraphs-side missing data from script-side lookup failures. That makes the gate too weak for release safety and also leaks internal quality semantics into a frontend that is supposed to be consumer-facing.

## What Changes

- Replace result-count-based publish gating with attribution-based gating for missing metrics.
- Classify missing rows into `source_missing`, `lookup_failed`, or `unknown` instead of relying only on aggregate warning counts.
- Require manual operator review before publishing builds that contain high-risk `unknown` rows in key lineup, rotation, or bullpen slots.
- Keep user-facing frontend pages focused on approved depth chart results and remove internal warning/status diagnostics from the production UI contract.
- Strengthen the meaning of `public/data/latest/` so it represents the most recent approved snapshot, not merely the most recent successful build artifact.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `depth-charts-data-pipeline`: change quality evaluation and publish gating to use missing-data attribution, risk-based review, and operator approval for high-risk unknown cases.
- `depth-charts-web-ui`: change the frontend contract so production pages show approved depth chart data and freshness metadata without exposing internal warning diagnostics.

## Impact

- Affected code: `scripts/fangraphs_batter_sync.py`, `scripts/fangraphs_sp_sync.py`, `scripts/fangraphs_rp_sync.py`, `scripts/depth_charts_pipeline.py`, `scripts/regression_checks.py`, `scripts/qa_go_no_go.py`, `public/app.js`, and related runbook/docs.
- Affected data artifacts: candidate snapshots, `quality-report.json`, publish decision outputs, and any operator review metadata used before promoting to `public/data/latest/`.
- Affected systems: Fangraphs ingestion, snapshot publication, QA/review workflow, and the public static frontend contract.
