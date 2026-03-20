## 1. Capture Attribution Evidence

- [x] 1.1 Extend `scripts/fangraphs_batter_sync.py` to preserve match evidence for each row, including successful match method and unresolved lookup context.
- [x] 1.2 Extend `scripts/fangraphs_sp_sync.py` to preserve match evidence for each row, including successful match method and unresolved lookup context.
- [x] 1.3 Extend `scripts/fangraphs_rp_sync.py` to preserve match evidence for each row, including successful match method and unresolved lookup context.
- [x] 1.4 Verify the season-pinned sync outputs still validate for 2025 while carrying the new attribution evidence.

## 2. Rebuild Publish Gating

- [x] 2.1 Update `scripts/depth_charts_pipeline.py` to classify missing rows as `source_missing`, `lookup_failed`, or `unknown`.
- [x] 2.2 Add slot-based risk tiers for Batter, SP, and RP rows so the pipeline can distinguish high-risk unknowns from lower-risk unknowns.
- [x] 2.3 Replace count-threshold-driven publish decisions with attribution-based blocking and pending-review decisions.
- [x] 2.4 Ensure candidate and latest artifact handling continues to support atomic publish and rollback with the new publish states.

## 3. Add Review And QA Workflow

- [x] 3.1 Update `scripts/regression_checks.py` so known regression rows remain hard publish blockers under the new gate.
- [x] 3.2 Update `scripts/qa_go_no_go.py` to surface blocking failures and list high-risk unknown rows that require operator review.
- [x] 3.3 Define the operator approval path for reviewed candidates, including how approval is recorded before promoting a build to `public/data/latest`.
- [x] 3.4 Validate the workflow against at least one candidate containing review-required unknowns and one candidate containing blocking lookup failures.

## 4. Align Frontend And Documentation

- [x] 4.1 Update `public/app.js` and related frontend assets so production pages remain consumer-facing and do not expose internal warning/status diagnostics.
- [x] 4.2 Preserve freshness metadata in the frontend so users can still understand snapshot recency without seeing operator-only quality states.
- [x] 4.3 Update runbooks and QA documentation to describe attribution-based gating, operator review, publish approval, and rollback expectations.
