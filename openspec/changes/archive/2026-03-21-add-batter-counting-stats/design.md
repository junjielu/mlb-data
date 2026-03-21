## Context

The current batter ingest path already uses the Fangraphs leaders batting API and matches those rows onto roster-resource lineup slots before publishing `public/data/latest/depth-charts.json`. That API response includes counting stats such as `R`, `HR`, `RBI`, and `SB`, but the current mapper only retains `wRC+`, `AVG`, `OBP`, and `SLG`, so the public contract and web UI omit values the source already provides.

This change crosses the ingest, publish, and frontend layers:
- `scripts/fangraphs_batter_sync.py` defines the batter row shape captured from Fangraphs
- `scripts/depth_charts_pipeline.py` promotes sanitized batter rows into the public snapshot
- `public/app.js` defines the Batter table columns and missing-value rendering

The repository guardrails still apply:
- season handling stays pinned to `2025`
- public artifacts remain consumer-facing and MUST NOT expose operator-only diagnostics
- `public/data/latest/depth-charts.json` remains the frontend contract, so any added fields must be intentional and documented

## Goals / Non-Goals

**Goals:**
- Extend public batter rows with Fangraphs counting stats `R`, `HR`, `RBI`, and `SB`
- Show the new counting stats on the team detail Batter table immediately after `Position`
- Move `wRC+` to the final Batter column so the counting stats and slash stats remain grouped ahead of it
- Preserve current missing-value behavior by rendering `--` for absent values
- Keep the change low-risk by reusing the existing Fangraphs batting source and current publish flow

**Non-Goals:**
- Changing season scope, routing, or injury-report behavior
- Introducing a new data source, a second batting endpoint, or a new operator workflow
- Expanding review gating to treat the new counting stats as new blocking publish criteria in this change
- Redesigning the table layout beyond the added columns and any minimal spacing adjustment required for readability

## Decisions

### Decision: Reuse the existing Fangraphs batting API response
The ingest layer will continue using the current Fangraphs leaders batting endpoint and add `R`, `HR`, `RBI`, and `SB` from the same response rows that already provide `AVG`, `OBP`, `SLG`, and `wRC+`.

Rationale:
- The source already returns the needed fields, so no second fetch path is necessary.
- This keeps player identity resolution unchanged because the same matched row feeds both existing and new metrics.

Alternatives considered:
- Fetch a separate batting endpoint or player page per batter. Rejected because it adds request volume and another failure mode without improving fidelity.

### Decision: Extend the public batter row contract directly
The public release artifact will carry the new counting stat keys on each batter row rather than deriving them only in the browser.

Rationale:
- The web UI already renders from the approved public snapshot, so keeping the fields in `depth-charts.json` preserves the existing release boundary.
- It keeps frontend rendering simple and avoids creating hidden client-side derivation rules.

Alternatives considered:
- Hydrate counting stats only at runtime in the browser. Rejected because it would bypass the release artifact contract and couple the frontend to live Fangraphs availability.

### Decision: Do not expand blocking QA gates in the first change
The pipeline will continue to use the existing batter metric completeness keys for publish gating, while the web UI will still render `--` for any missing newly added counting stat values.

Rationale:
- This change is primarily a contract and presentation enhancement, not a gate recalibration.
- Expanding blocking completeness rules at the same time would mix a UI-focused change with an operational policy shift and increase rollout risk.

Alternatives considered:
- Add `R`, `HR`, `RBI`, and `SB` to `B_KEYS` and gate on them immediately. Rejected for now because it could unexpectedly block publishes for data that is otherwise acceptable to display as optional enhancement fields.

## Risks / Trade-offs

- [Wider public row shape] → Document the schema change in specs and keep the added fields limited to the existing Fangraphs batter row model.
- [Table width growth on smaller screens] → Keep the column insertion scoped and allow minimal CSS adjustments only if readability degrades.
- [Source rows may occasionally omit a counting stat] → Preserve the existing `--` rendering contract so rows remain visible and usable.
- [Future operators may assume the new fields are gated like existing metrics] → State explicitly in specs and design that the first version does not change blocking publish criteria.

## Migration Plan

1. Update batter ingest to capture `R`, `HR`, `RBI`, and `SB` from the existing Fangraphs batting response.
2. Publish a new candidate and verify the resulting public batter rows include the new keys while remaining sanitized.
3. Update the web UI to render the four new Batter columns after `Position` and place `wRC+` at the end of the Batter table.
4. Validate the team detail page in local preview and publish through the normal depth chart release flow.
5. If rollback is required, use the existing `public/data/backups/`-based publish rollback flow to restore the prior `depth-charts.json`.

## Open Questions

- No open questions are required to start implementation; the source field availability has already been confirmed from the current Fangraphs batting API response.
