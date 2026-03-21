## Context

The current public depth charts release contract is intentionally consumer-facing: `public/data/latest/depth-charts.json` exposes only the approved 2025 snapshot used by the web UI, while candidate-only diagnostics remain in the internal build area. The current team detail page renders Batter, SP, and RP as flat tables, so users can inspect the latest 2025 row for each player but cannot compare that row against recent seasons without leaving the page.

This change spans the data pipeline and the frontend. The pipeline must expose a stable public player identifier and recent historical season values without leaking operator-only identity matching evidence. The frontend must render those new public fields as inline expandable rows while preserving the existing consumer-facing table model, missing-value treatment, and Fangraphs links.

## Goals / Non-Goals

**Goals:**
- Expose a stable public `playerId` for every published Batter, SP, and RP row.
- Attach consumer-facing historical season data for 2024 and 2023 to each published row.
- Keep public history data within the existing `depth-charts.json` release artifact instead of exposing internal candidate diagnostics.
- Add inline expansion on `/team/:abbr` so a 2025 primary row can reveal 2024 and 2023 beneath it.
- Preserve existing sort behavior, missing-value rendering, and player link behavior.

**Non-Goals:**
- Add season pickers, search, filters, or new overview-page interactions.
- Reintroduce operator diagnostics, review state, or QA artifacts into the public release surface.
- Expand history beyond 2024 and 2023 in this change.
- Alter the current injury report flow or mix injury data into Batter, SP, or RP rows.
- Introduce separate player detail pages, charts, or trend visualizations.

## Decisions

### Expose a consumer-facing `playerId` instead of reusing internal traceability fields

The public contract will add a dedicated `playerId` field derived from the existing identity resolution result, rather than exposing internal fields such as `source_player_id`, `matched_player_id`, or `match_method`.

Rationale:
- The frontend needs a stable row identity for expansion state and future player-level features.
- Existing internal fields are tied to operator workflows and carry diagnostic semantics that should remain private.
- A dedicated public field keeps the release contract consumer-facing while still making row identity explicit.

Alternatives considered:
- Expose `matched_player_id` directly: rejected because it leaks internal resolution vocabulary into the public contract.
- Key expansion purely by player name or URL: rejected because names are not sufficiently stable and URLs are presentation data, not a durable public identifier.

### Model history as a row-level `history` collection

Each published Batter, SP, and RP row will carry a `history` collection containing season entries for 2024 and 2023. Each entry will include a `season` field plus the same section-specific metric fields used by the current row where available.

Rationale:
- `history` keeps 2025 as the primary row shape and makes prior seasons clearly subordinate.
- An array of season entries is easier to extend than embedding season numbers as top-level field names.
- The frontend can render the current row and the expanded rows from one normalized structure.

Alternatives considered:
- Add top-level `2024_*` and `2023_*` fields: rejected because it bloats the row shape and makes rendering harder to generalize.
- Publish a separate `player-history.json`: rejected for this change because the team detail page already depends on `depth-charts.json`, and keeping recent history attached to each row avoids additional client-side joins for the initial version.

### Preserve a single table model with inline subrows

The frontend will continue to render one table per section. A clicked 2025 row expands inline 2024 and 2023 subrows directly beneath the primary row using the same column structure.

Rationale:
- Inline subrows preserve direct column-by-column comparison.
- Reusing one table avoids introducing separate nested tables or cards with a different reading pattern.
- Existing sorting and missing-value formatting can be reused with minimal conceptual change.

Alternatives considered:
- Render history in a nested card or modal: rejected because it breaks side-by-side numeric comparison.
- Insert a second table under each section for historical rows: rejected because it disconnects history from its owning player row.

### Allow only one expanded row per section

Each of Batter, SP, and RP will track at most one expanded player row at a time.

Rationale:
- Team detail pages are already vertically dense, and multiple simultaneous expansions would quickly become noisy.
- Per-section single expansion keeps state management simple and predictable.
- Users can still compare multiple players by opening them one at a time without losing section context.

Alternatives considered:
- Allow multiple expanded rows per section: rejected because it increases page length and visual clutter.
- Allow only one expanded row for the whole page: rejected because it would create unnecessary coupling across Batter, SP, and RP.

### Sort only the 2025 primary rows

Section sorting will continue to reorder only the 2025 primary rows. Any expanded 2024 and 2023 rows remain attached beneath their owning primary row after sorting.

Rationale:
- The existing sort model is centered on the currently visible depth chart rows.
- Users interpret the historical rows as context for the 2025 player, not as independent sortable entities.
- This avoids ambiguous behavior such as sorting 2024 subrows across different owners.

Alternatives considered:
- Include historical rows in the sort set: rejected because it breaks the ownership relationship between primary and historical rows.
- Disable sorting when a row is expanded: rejected because it unnecessarily weakens the current UX.

## Risks / Trade-offs

- [Historical Fangraphs metrics may not be uniformly available for every section] → Keep the public row shape stable, allow empty historical metric values, and rely on the existing `--` rendering in the frontend.
- [Additional historical lookups can increase build time and request volume] → Scope this change to 2024 and 2023 only, reuse existing player identity resolution where possible, and keep the publish target limited to the 2025 pipeline.
- [Public contract growth increases snapshot size] → Limit history to two prior seasons and keep only consumer-facing fields in the published artifact.
- [Current spec language about public traceability is ambiguous] → Update the data-pipeline spec to define `playerId` as the public identity field while keeping operator-only evidence internal.

## Migration Plan

1. Extend the internal build snapshot generation path so each row can resolve a public `playerId` and recent history before sanitization.
2. Update public snapshot sanitization so `playerId` and `history` are preserved while operator-only matching evidence remains excluded.
3. Update the team detail renderer to track one expanded row per section and render inline 2024 and 2023 subrows.
4. Verify that sorting, missing-value rendering, and Fangraphs links continue to work with expanded rows.
5. Publish the new release artifact through the existing depth charts pipeline.

Rollback follows the existing `public/data/backups/` release rollback path. If the new contract or UI behaves incorrectly, restore the prior latest snapshot and redeploy the previous frontend bundle.

## Open Questions

- Whether historical advanced pitching metrics such as `stuff_plus` and `location_plus` will be available for both prior seasons with the same reliability as current-season values.
- Whether the public `playerId` should always be a numeric Fangraphs player ID string or allow scout-style IDs when Fangraphs roster rows do not expose a numeric identifier.
