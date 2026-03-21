## 1. Unify Identity-First Matching

- [x] 1.1 Audit `scripts/fangraphs_batter_sync.py`, `scripts/fangraphs_sp_sync.py`, and `scripts/fangraphs_rp_sync.py` into one shared resolution order centered on Fangraphs source roster identity.
- [x] 1.2 Refactor SP ingestion so source player ID and targeted player-ID lookup are attempted before weaker name-based fallback paths.
- [x] 1.3 Refactor RP ingestion so same-name fallback cannot silently accept a different numeric player ID than the source roster row.
- [x] 1.4 Preserve explicit mismatch evidence for unresolved or rejected fallback rows so downstream QA can distinguish source absence from script-side mismatch risk.

## 2. Separate Internal And Public Artifacts

- [x] 2.1 Define an internal artifact directory for candidate builds, quality outputs, review records, and QA reports outside `public/data/latest/`.
- [x] 2.2 Update `scripts/depth_charts_pipeline.py` to write internal candidate artifacts to that internal area while keeping atomic publish and rollback behavior intact.
- [x] 2.3 Add a sanitized release-output step that derives public `depth-charts.json` and related browser-facing files from the reviewed internal candidate.
- [x] 2.4 Remove operator-only fields such as warnings, warning counts, review state, and QA metadata from the published public release contract.

## 3. Rewire QA And Publish Workflow

- [x] 3.1 Update `scripts/regression_checks.py` and `scripts/qa_go_no_go.py` to read the correct internal artifact for gating and review decisions instead of assuming everything lives in `public/data/latest/`.
- [x] 3.2 Ensure source-vs-matched player ID disagreements are treated as blocking or reviewable mismatches rather than successful automatic matches.
- [x] 3.3 Verify review approval and publish commands promote only sanitized public release files after internal QA and approval succeed.
- [x] 3.4 Exercise the workflow against at least one ambiguous-name case and one ordinary success case to confirm the new boundary and matching semantics hold.

## 4. Align Frontend And Documentation

- [x] 4.1 Update frontend data loading so `public/app.js` depends only on the sanitized public release contract.
- [x] 4.2 Verify `/teams` and `/team/:abbr` continue rendering approved depth chart and injury data without QA-only artifact dependencies.
- [x] 4.3 Update OpenSpec-linked runbook or operator documentation to describe the internal artifact boundary, review flow, publish flow, and rollback expectations.
