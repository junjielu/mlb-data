## Context

The repository already has a two-stage publication shape: Fangraphs sync scripts produce season-pinned JSON inputs, and `scripts/depth_charts_pipeline.py` merges them into candidate artifacts before optionally promoting a build to `public/data/latest/`. The current gate is still result-oriented. It checks structural minimums and aggregate missing-value thresholds, but it does not preserve enough evidence to explain whether an empty row is a valid Fangraphs-side absence or a script-side lookup failure.

That limitation creates two problems:

- The publish gate is too permissive for a consumer-facing site because some script errors can still pass if they do not exceed global thresholds.
- The frontend contract drifted toward exposing internal warning semantics even though the site is intended to show approved results to end users, not QA diagnostics.

Constraints:

- The season remains pinned to 2025 unless explicitly changed.
- The main snapshot schema major version should not be changed as part of this work.
- Existing Fangraphs sync scripts should remain the source of truth for roster extraction and stat lookup.
- Candidate artifacts may continue to exist under `public/data/candidates/`, but only approved builds should reach `public/data/latest/`.

Stakeholders:

- The data maintainer who runs and approves snapshot publication.
- End users consuming the depth charts site.

## Goals / Non-Goals

**Goals:**

- Introduce missing-data attribution so empty metrics can be classified as `source_missing`, `lookup_failed`, or `unknown`.
- Use attribution and business-risk tiers to decide whether a candidate can publish automatically, must be manually reviewed, or must be blocked.
- Keep production frontend pages consumer-facing by removing internal warning/status diagnostics from the public contract.
- Make `latest` mean the latest approved snapshot rather than the latest build that merely cleared a coarse threshold.

**Non-Goals:**

- Eliminating all legitimate missing data from published snapshots.
- Replacing Fangraphs ingestion with a new data source or a new language stack.
- Building a generic workflow engine for approvals beyond this depth charts publication flow.
- Adding public-facing operator or maintenance views as part of the main site experience.

## Decisions

### 1) Classify missing rows by cause, not just by emptiness

- Decision: The pipeline will treat fully missing metric rows as attributed cases with three outcomes: `source_missing`, `lookup_failed`, or `unknown`.
- Rationale: Publish safety depends on why data is missing, not only on how many rows are empty.
- Alternative considered: Keep the current warning-count model and tighten thresholds.
- Why not: Thresholds cannot distinguish legitimate Fangraphs-side gaps from script failures, so they either miss real regressions or over-block valid builds.

### 2) Preserve match evidence in the sync stage

- Decision: Batter, SP, and RP sync outputs will preserve enough matching evidence for later attribution, such as whether a row matched by direct name, player ID, normalized name, or not at all.
- Rationale: The sync scripts are the only place where roster context, Fangraphs page identity, and lookup attempts are all visible at once.
- Alternative considered: Infer attribution only in the aggregate pipeline.
- Why not: The aggregate pipeline sees only the final merged rows and loses most of the context needed to prove whether a missing row is legitimate or a lookup failure.

### 3) Use risk tiers for unresolved unknown cases

- Decision: `unknown` rows will be ranked by slot importance: Batter 1-5, SP1-SP3, and RP CL/SU8/SU7 are high risk; Batter 6-7, SP4-SP5, and RP MID are medium risk; long-tail slots are low risk.
- Rationale: The user-facing cost of publishing uncertain data is not uniform across all rows.
- Alternative considered: Treat every `unknown` row the same.
- Why not: That would either force excessive manual review on low-value rows or allow high-impact uncertainty to slip through.

### 4) Block proven failures, manually review high-risk uncertainty

- Decision: Publication will be blocked automatically for structural failures, regression failures, and any attributed `lookup_failed` rows. High-risk `unknown` rows will require explicit operator review before promotion to `latest`.
- Rationale: This gives strict release protection without making the system unusable whenever attribution evidence is incomplete.
- Alternative considered: Automatically block all `unknown` rows.
- Why not: Current Fangraphs variability and evidence quality would make publication too fragile.

### 5) Separate operator diagnostics from the production frontend

- Decision: Internal quality signals stay in candidate/review artifacts and QA outputs, while `/teams`, `/team/:abbr`, and `/about-data` remain consumer-facing.
- Rationale: Users should see approved results, not internal release diagnostics.
- Alternative considered: Keep warning badges and warning detail panels in the production UI.
- Why not: That turns the user site into a release dashboard and weakens the meaning of publishing only approved data.

## Risks / Trade-offs

- [Attribution evidence remains incomplete for some edge cases] -> Mitigation: keep an explicit `unknown` class and route only high-risk unknowns into mandatory review.
- [Extra metadata could make candidate artifacts noisier] -> Mitigation: keep the public frontend contract clean and treat review metadata as operator-facing.
- [Manual review adds operational steps] -> Mitigation: scope required review to high-risk unknowns and known regression hotspots rather than all missing rows.
- [Risk tier rules may need tuning over time] -> Mitigation: document initial tiers in specs and keep the system open to future adjustment through spec changes instead of ad hoc threshold edits.

## Migration Plan

1. Extend the sync layer to emit matching evidence needed for later attribution.
2. Update the pipeline to derive missing-data classifications and publish decisions from that evidence.
3. Rework QA outputs so operator review focuses on high-risk unknowns and explicit blocking failures.
4. Adjust the public frontend contract to remove internal quality-status presentation while preserving freshness metadata.
5. Validate the new gate against the existing regression checks and confirm rollback behavior remains unchanged.

Rollback remains snapshot-based: if the new gating or review workflow behaves incorrectly, operators can keep the previous approved `latest` snapshot or roll back using `public/data/backups/`.

## Open Questions

- What is the lightest review artifact that still gives the operator enough evidence to approve or reject high-risk unknowns?
- Should medium-risk unknowns ever escalate automatically when several occur for the same team or section?
- Which existing regression rows should become permanently encoded as hard publish blockers versus remaining maintainable spot checks?
