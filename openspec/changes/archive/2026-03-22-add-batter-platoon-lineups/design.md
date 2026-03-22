## Context

The current depth charts pipeline publishes each team's Batter section as a single ordered array in `public/data/latest/depth-charts.json`, and the frontend renders that array as one batter table on `/team/:abbr`. That model matched the earlier Fangraphs depth chart page ingest, but it no longer captures the richer platoon lineup data now available on Fangraphs RosterResource `platoon-lineups/<team>` pages, which expose separate go-to lineups against right-handed and left-handed pitching.

This change crosses the Fangraphs batter ingest script, the depth chart publish pipeline, the public artifact contract, frontend rendering, and the existing regression / QA gates. It also changes a public consumer-facing schema, so the design must define a clear transition for build validation and rollback.

## Goals / Non-Goals

**Goals:**
- Publish both `vsR` and `vsL` projected batter lineups in the approved public depth chart snapshot.
- Keep the existing public batter row shape for metrics, identity, age, and history so only the batter container changes materially.
- Surface a lightweight consumer-facing platoon marker for players who start only versus one pitcher handedness.
- Preserve the existing Batter table interaction model in the web UI by switching between lineup views instead of rendering multiple independent batter sections.
- Extend structural and regression validation so batter gates remain meaningful after the schema change.

**Non-Goals:**
- Do not change SP, RP, or injury data contracts.
- Do not add historical actual game lineups or daily lineup tracker summaries.
- Do not expose operator-only comparison diagnostics about why a player is platoon-tagged.
- Do not redesign the page route structure or add new public data artifacts outside `depth-charts.json`.

## Decisions

### Decision: Publish batter as a lineup container with `vsR` and `vsL`
The public batter section will change from a single array to an object:

```json
{
  "defaultView": "vsR",
  "lineups": {
    "vsR": [/* batter rows */],
    "vsL": [/* batter rows */]
  }
}
```

Each lineup row will continue to use the existing public batter row fields such as `order`, `name`, `position`, `runs`, `hr`, `rbi`, `sb`, `avg`, `obp`, `slg`, `wrc_plus`, `playerId`, `history`, and `age`.

Rationale:
- `vsR` and `vsL` are separate nine-man lineups, not merely alternate order values on the same row set.
- Keeping row shape stable limits frontend and publish-sanitization churn to the batter container and view selection logic.
- The contract remains consumer-facing and does not need a second browser artifact.

Alternatives considered:
- Keep `batter` as the default `vsR` array and add a sibling `batterPlatoon` object: rejected because it duplicates public semantics and creates a long-lived migration burden.
- Add `vsROrder` / `vsLOrder` fields on a merged row list: rejected because platoon-only starters and lineup membership become ambiguous when the two views do not share the same nine players.

### Decision: Derive consumer-facing platoon role markers in the publish pipeline
The publish pipeline will derive a lightweight row field such as `platoonRole` for batter lineup rows:
- empty when the player appears in both lineup views
- `vsR_only` when the player appears only in the `vsR` lineup
- `vsL_only` when the player appears only in the `vsL` lineup

Rationale:
- The label is consumer-facing product meaning, not operator-only evidence.
- Deriving it once in the pipeline keeps all consumers consistent and avoids duplicating cross-view comparison logic in the browser.
- The field stays intentionally narrow and does not expose internal comparison metadata.

Alternatives considered:
- Compute labels only in the frontend: rejected because it duplicates logic and makes other consumers reimplement lineup comparison.
- Publish verbose comparison payloads listing the opposite-hand lineup membership: rejected because it bloats the public contract for a simple display cue.

### Decision: Keep the Batter section as one table with a lineup view switcher
The frontend will continue to render one Batter section on `/team/:abbr`, but it will add a `vs RHP` / `vs LHP` switcher above the table. The active view will determine which lineup array is passed into the existing table rendering path.

The platoon role marker will render as a quiet inline label in the name cell, alongside the existing age treatment, rather than as a dedicated table column.

Rationale:
- Users still think of Batter as a single section; the new concern is which projected lineup view they are examining.
- Reusing the existing table structure preserves sorting, missing-value rendering, and expandable history behavior.
- Inline labeling makes platoon-only starters obvious without widening the table or competing with baseball stats.

Alternatives considered:
- Render two full batter tables at once: rejected because it doubles visual weight and makes team detail pages much harder to scan.
- Add a dedicated `Platoon` column: rejected because the information is secondary context and does not justify a persistent wide column.

### Decision: Anchor existing batter regression checks to `vsR` while extending structure gates to both lineup views
The QA and regression scripts will treat both `vsR` and `vsL` as required structural lineup views for each team. Existing named batter regression cases will remain anchored to the `vsR` view unless a future change explicitly broadens them.

Rationale:
- Current regression coverage was authored against the legacy single-lineup model, which best maps to the default `vsR` view during migration.
- Requiring both lineup views structurally catches missing `vsL` data without forcing an immediate redesign of all known regression fixtures.
- This keeps rollout risk controlled while still making the new schema enforceable.

Alternatives considered:
- Duplicate every regression assertion for `vsL`: rejected for the initial change because it adds work without evidence that the existing regression set is the right left-handed baseline.
- Validate only `vsR` and ignore `vsL` gates: rejected because it would let half the new public contract degrade silently.

## Risks / Trade-offs

- [Public batter schema becomes breaking for existing consumers] → Mitigate by documenting the contract change in proposal/specs, updating the bundled frontend in the same change, and relying on the existing publish rollback path if downstream breakage appears.
- [Fangraphs platoon page payload shape may differ from the current depth chart ingest assumptions] → Mitigate by treating `platoon-lineups/<team>` as the source of truth for batter lineup membership and isolating parsing changes to the batter sync layer.
- [Dual lineups may contain the same player with different order slots, complicating row state in the browser] → Mitigate by including lineup view in batter row identity when tracking expanded state.
- [Platoon role labels may be noisy if shown for every player] → Mitigate by rendering labels only for one-sided starters and keeping everyday starters unlabeled.

## Migration Plan

1. Update the Fangraphs batter ingest to fetch platoon lineup data and emit both `vsR` and `vsL` lineup views in candidate snapshots.
2. Update the depth chart publish pipeline to sanitize the new batter container, retain existing public batter row fields, and derive consumer-facing `platoonRole` markers.
3. Update regression and QA scripts so structural checks require both lineup views and existing batter assertions read from `vsR`.
4. Update the frontend Batter section to switch between lineup views and display platoon-only labels in the name cell.
5. Build a new candidate, run regression and go/no-go checks, preview `/team/:abbr`, and publish.

Rollback will continue to use the existing `public/data/backups/` flow for `depth-charts.json`. If the new public batter contract or UI behavior causes problems after publish, restore the previous `latest` snapshot and redeploy the prior frontend bundle.

## Open Questions

- Whether the batter sync layer can read both platoon lineups reliably from a single `platoon-lineups/<team>` payload or should fetch `viewmode=r` and `viewmode=l` separately.
- Whether the public snapshot should keep `defaultView: "vsR"` as a literal contract field or let the frontend hardcode the initial choice.
