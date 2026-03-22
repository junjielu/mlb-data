## Context

The public depth chart snapshot currently exposes different metric contracts for SP and RP rows. Starters publish `whip` and `location_plus`, while relievers publish `k_pct` instead. The web UI mirrors that split, so users cannot compare the two pitcher sections using a single mental model.

This change also introduces two additional pitcher metrics, `vfa` and `babip`, which must be sourced from Fangraphs, carried through the public `depth-charts.json` artifact, and rendered in both SP and RP sections immediately after `Location+`.

The project constraints are:
- Public artifacts under `public/data/latest/` remain consumer-facing and schema-stable unless intentionally changed.
- Season defaults remain on 2025.
- Fangraphs remains the source of truth for both the current 2025 rows and recent-history rows for 2024 and 2023.

## Goals / Non-Goals

**Goals:**
- Standardize SP and RP public row metrics on one ordered contract: `era`, `whip`, `k9`, `bb9`, `stuff_plus`, `location_plus`, `vfa`, `babip`.
- Remove `k_pct` from the public RP contract and from RP web presentation.
- Extend pitcher history rows so SP and RP use the same consumer-facing metric set as their primary rows.
- Keep missing-value behavior unchanged by allowing absent Fangraphs values to publish as empty strings and render as `--` in the UI.
- Keep the front-end implementation simple by letting SP and RP share a single pitcher column definition.

**Non-Goals:**
- Changing batter contracts or injury-report behavior.
- Introducing a new public schema major version.
- Preserving `k_pct` anywhere in the public UI contract.
- Reworking non-pitcher table layout beyond what is required to fit the new pitcher columns.

## Decisions

### Decision: Standardize the public pitcher keys instead of only standardizing labels

The change will align the underlying public row shape, not just the UI headers. Both SP and RP primary rows and history rows will publish the same ordered metrics after `age`.

Why:
- A shared UI column definition becomes possible only if the public row shape is also shared.
- Regressions become easier to detect because SP and RP can be validated against the same metric contract.

Alternative considered:
- Leave the public RP shape unchanged and render placeholder `--` cells in the UI. Rejected because it produces a visually uniform table over a semantically inconsistent data contract.

### Decision: Remove `k_pct` from the public RP contract rather than demote it to a secondary field

The public artifact and UI will no longer publish `k_pct` for RP rows.

Why:
- The requested product model is a single pitcher comparison table, not a role-specific sabermetric split.
- Retaining `k_pct` in the public contract would leave dead or second-class fields that are no longer part of the primary browsing experience.

Alternative considered:
- Keep `k_pct` in the public snapshot but stop rendering it. Rejected because it preserves stale public surface area without a consumer-facing requirement.

### Decision: Add `vfa` and `babip` at the ingestion layer before snapshot assembly

Both pitcher sync scripts will source `vfa` and `babip` from Fangraphs at the same stage where they currently source ERA, WHIP, K/9, BB/9, Stuff+, and Location+.

Why:
- The snapshot pipeline should not infer or scrape extra metrics from downstream artifacts when the source sync step is already responsible for normalizing Fangraphs rows.
- Keeping the source sync output complete makes candidate builds, review artifacts, and release snapshots consistent.

Alternative considered:
- Only enrich `vfa` and `babip` inside `depth_charts_pipeline.py`. Rejected because it would create divergent pitcher row shapes between raw sync artifacts and the publish pipeline.

### Decision: Treat Fangraphs field-name uncertainty as an implementation-time mapping concern

`vfa` is known to exist conceptually in Fangraphs pitcher data, but the exact response key may vary by endpoint naming. The implementation will verify the actual upstream field names during sync-script updates and centralize the mapping in the Fangraphs normalization layer.

Why:
- The public contract should expose stable local keys (`vfa`, `babip`) regardless of Fangraphs response naming.
- This isolates upstream API quirks from the rest of the pipeline and the UI.

Alternative considered:
- Mirror Fangraphs field names directly into the public contract. Rejected because source naming may be inconsistent or harder to reason about in the UI.

## Risks / Trade-offs

- [Upstream Fangraphs field mismatch for `vfa`] → Verify the actual API response key during implementation and keep the source-to-public key mapping localized to the sync scripts.
- [Some pitcher rows may not have usable `vfa` or `babip` values] → Preserve current missing-value behavior by publishing empty strings and rendering `--`.
- [Public contract change may affect downstream consumers beyond the bundled web UI] → Document the breaking removal of `k_pct` in the proposal and keep the new ordered metric contract explicit in specs.
- [Wider pitcher tables may stress current layout] → Reuse the recent responsive table strategy and let the UI stack or scroll only where the existing table system already does so safely.

## Migration Plan

1. Update Fangraphs SP and RP sync scripts so normalized pitcher rows include the unified metric set.
2. Update `depth_charts_pipeline.py` to publish the new RP fields, add `vfa` and `babip` for both roles, and remove `k_pct` from the public RP contract and history rows.
3. Regenerate a candidate snapshot and run existing regression and go/no-go checks against the updated artifact shape.
4. Update the web UI to use one pitcher column definition shared by SP and RP in the new metric order.
5. Publish the updated snapshot only after the candidate passes validation.
6. If rollback is required, restore the prior `public/data/latest/depth-charts.json` from backup using the existing rollback flow.

## Open Questions

- Which exact Fangraphs API keys should map to public `vfa` for both current-season rows and 2024/2023 history rows?
- Do existing regression checks need explicit assertions for `vfa` and `babip`, or is schema/publish validation sufficient for the initial release?
