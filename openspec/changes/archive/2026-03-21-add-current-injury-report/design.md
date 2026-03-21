## Context

The current site serves a single approved 2025 depth chart snapshot through `public/data/latest/depth-charts.json`, and `/team/:abbr` renders Batter, SP, and RP from that one source. The proposed injury addition has different semantics: it is display-only context, it follows Fangraphs' current season rather than the locally pinned 2025 data flow, and its freshness should not block promotion of the core depth chart snapshot.

## Goals / Non-Goals

**Goals:**
- Add a dedicated injury-report data flow that publishes a standalone latest artifact for current-season Fangraphs injury data.
- Allow `/team/:abbr` to render a current injury section without implying that injuries are part of the pinned 2025 depth chart snapshot.
- Preserve the last approved injury snapshot when a new injury fetch fails.
- Keep Fangraphs injury fields available in published data while showing a lighter public presentation focused on readability.

**Non-Goals:**
- Do not merge injury rows into Batter, SP, or RP tables or add row-level injury badges to depth chart entries.
- Do not make injury freshness a blocker for `depth-charts.json` promotion.
- Do not build historical injury browsing, activated/all timeframes, or cross-team injury search in this change.

## Decisions

### 1. Publish injuries as an independent latest artifact
The system will publish injuries to a dedicated artifact such as `public/data/latest/injuries.json` rather than embedding injury rows into `depth-charts.json`.

Rationale:
- Injury data follows Fangraphs' current season while depth chart data remains pinned to 2025.
- This keeps metadata honest and avoids mixing two time bases inside one artifact.
- It isolates failures so injury refreshes do not block main depth chart releases.

Alternatives considered:
- Embed `injuries[]` inside each team object in `depth-charts.json`: simpler for frontend fetches, but it couples unrelated publish semantics and obscures the mixed time model.

### 2. Treat injuries as best-effort display context with stale fallback
The injury pipeline will publish a new latest snapshot only after successful fetch and validation. If a fetch or validation step fails, the previously published latest injury snapshot remains in place.

Rationale:
- Injury data is explicitly display-only.
- Users are better served by a slightly stale injury view than by a missing section or a blocked core release.

Alternatives considered:
- Fail closed and hide injuries when a refresh fails: more strict, but degrades the public page unnecessarily.
- Block the full site publish on injury fetch errors: incompatible with the intended display-only role.

### 3. Render injuries as a lightweight team-page section with separate freshness metadata
The team detail page will add a `Current Injury Report` section after RP. It will present a compact table with `Name`, `Pos`, `Status`, and `Latest Update`, while keeping richer source fields in the injury artifact for future use.

Rationale:
- This preserves the current table-first UI while giving the narrative update field enough prominence to be useful.
- It keeps injuries visually subordinate to the core depth chart tables.

Alternatives considered:
- Make injuries a fourth fully symmetric data table with all source columns: too dense and overstates injury data as a peer to the core metric tables.
- Render injuries as free-form cards: better for prose but departs sharply from the site's current interaction model.

### 4. Make time semantics explicit in section-level copy
The team page will distinguish `2025 Depth Charts` from `Current Injury Report`, with each section showing its own lightweight freshness metadata.

Rationale:
- The page becomes a composed view of multiple snapshots rather than one unified build.
- Clear labels reduce the chance that users misread current-season injuries as part of the 2025 pinned roster snapshot.

Alternatives considered:
- Keep one global updated-time line for the whole page: simpler, but misleading once injuries come from a distinct artifact and season.

## Risks / Trade-offs

- [Mixed time semantics may confuse users] -> Mitigate with explicit section titles and separate updated-time copy for depth charts versus injuries.
- [Fangraphs injury page structure may change] -> Mitigate by isolating the injury parser and validating required output fields before publish.
- [A stale injury snapshot may be mistaken for fresh data] -> Mitigate by surfacing the injury artifact's own update timestamp instead of implying page-wide freshness.
- [Long `Latest Update` text may create uneven rows] -> Mitigate by treating the injury section as a lighter contextual table, not a dense metric grid.

## Migration Plan

1. Add the standalone injury fetch and publish flow and generate a first approved `injuries.json` artifact.
2. Update the frontend to fetch injury data in parallel with the existing depth chart snapshot.
3. Release the UI with separate section-level freshness copy for depth charts and injuries.
4. If rollback is needed, revert the UI change independently and/or restore the previous injury latest artifact without touching the main depth chart snapshot.

## Open Questions

- Should the injury artifact include an explicit stale indicator, or is the last successful update timestamp sufficient for public use?
- Should the UI expose any path to secondary injury fields such as `Eligible to Return`, or should those remain data-only in the first release?
