## Context

The current batter ingest and publish flow already preserves Fangraphs platoon starter lineups under `batter.lineups.vsR` and `batter.lineups.vsL`, but it discards every non-starter row on the RosterResource platoon page by filtering strictly to order slots `1..9`. The public web UI then renders only one lineup at a time behind a `vs RHP` / `vs LHP` toggle, which forces users to mentally diff the two platoon views and hides Fangraphs' handedness-specific bench context that often explains why the two starter groups differ.

This change spans the Fangraphs batter sync layer, the public depth chart publish contract, validation scripts, and the Batter section layout. It is also a public schema evolution, so the design needs a clean contract for starter rows, alternate rows, and rollout gating while keeping the release surface consumer-facing.

## Goals / Non-Goals

**Goals:**
- Publish handedness-specific public alternates for Batter using Fangraphs platoon-page `Bench` rows.
- Keep public batter row shape stable across starters and alternates so the frontend can reuse existing rendering and history behavior.
- Present `vs RHP` and `vs LHP` as a simultaneous comparison surface instead of a view toggle.
- Preserve existing platoon role tagging and public row sanitation across all published batter rows.
- Extend validation so the new alternates collections are part of the approved public contract.

**Non-Goals:**
- Do not change SP, RP, injury, or route-level page structure.
- Do not expose `Proj. IL`, depth-chart notes, or other non-bench roster statuses as public alternates.
- Do not add a separate public artifact for platoon alternates.
- Do not introduce operator-only comparison diagnostics into the public snapshot or UI.

## Decisions

### Decision: Publish handedness-specific `alternates` beside the existing platoon lineups
The public batter container will expand to:

```json
{
  "defaultView": "vsR",
  "lineups": {
    "vsR": [/* 9 starter rows */],
    "vsL": [/* 9 starter rows */]
  },
  "alternates": {
    "vsR": [/* bench rows */],
    "vsL": [/* bench rows */]
  }
}
```

Each alternate row will use the same public consumer-facing row shape as starter rows, including the existing baseball metrics, `playerId`, `age`, `history`, `url`, and `platoonRole` fields.

Rationale:
- Fangraphs platoon pages model the bench separately for each handedness, so a sibling `alternates` container matches the source structure without flattening unlike row types together.
- Reusing the existing row shape minimizes frontend branching and avoids a second class of batter row contract.
- Keeping starters and alternates inside the same batter object preserves the current single-artifact release model.

Alternatives considered:
- Merge starters and alternates into one ordered list with a `status` column: rejected because starter order and alternate grouping are different concepts and would force the frontend to repeatedly partition the same data.
- Add a standalone `batterAlternates` root field on each team: rejected because it spreads one concern across multiple sibling containers and complicates sanitization and consumer reads.

### Decision: Only source `Bench` rows into public alternates
The batter ingest will parse the Fangraphs platoon page statuses and preserve only rows marked `Bench` in public `alternates`. Rows marked with other statuses, including `Proj. IL`, will remain outside the public batter release contract.

Rationale:
- `Bench` represents the consumer-meaningful answer to "who are the primary alternates for this handedness."
- `Proj. IL` is a different semantic category and would pollute alternates with unavailable players.
- This keeps the public contract narrow and avoids mixing healthy roster options with projected absences.

Alternatives considered:
- Publish every non-1..9 row as an alternate: rejected because it would mix bench, injured-list, and possibly future status types into one unstable public meaning.
- Add a second public status field and let the frontend filter: rejected because it expands the contract before the product has a clear use for those extra statuses.

### Decision: Render simultaneous platoon comparison as two linked lineup columns
The Batter section on `/team/:abbr` will render `vs RHP` and `vs LHP` at the same time as two coordinated columns. Each column will show the starter lineup first and a `Primary Alternates` block immediately beneath it. Existing row interactions such as Fangraphs links, inline age, missing-value rendering, and expandable recent history will continue to work within each column independently.

Rationale:
- The user task is comparison, not selection, so simultaneous presentation removes unnecessary interaction cost.
- Keeping starters above alternates preserves the visual hierarchy from Fangraphs without turning the page into four unrelated tables.
- A paired-column layout makes platoon differences obvious while still letting each handedness read top to bottom.

Alternatives considered:
- Keep the toggle and add an alternates subsection below the active lineup: rejected because it still hides one side of the platoon at a time.
- Render four fully independent tables: rejected because it doubles chrome and makes the Batter section visually heavy, especially next to SP and RP.

### Decision: Extend batter validation to require the alternates container but not a fixed alternate count
Publish validation will continue to require at least nine starter rows in both lineup views. In addition, the sanitized public batter container must always include `alternates.vsR` and `alternates.vsL`, but those arrays are not required to meet a fixed minimum length.

Rationale:
- Starter completeness is a hard structural expectation; bench depth is more variable and should not block publication solely because a source page exposes fewer bench rows.
- Requiring the alternates keys themselves keeps the public schema stable for consumers.
- This approach makes the new contract enforceable without overfitting to a transient roster size assumption.

Alternatives considered:
- Require a minimum of three or four alternates per handedness: rejected because roster churn, catcher usage, and Fangraphs editorial choices could create false publish failures.
- Treat alternates as optional and omit empty collections: rejected because it makes frontend rendering and consumer interpretation harder than necessary.

## Risks / Trade-offs

- [Fangraphs may rename or expand platoon row statuses] → Mitigation: isolate status parsing in the batter sync layer and treat only the literal `Bench` status as public alternates until a deliberate schema change expands support.
- [Public batter schema grows further] → Mitigation: keep alternates nested under the existing batter container and reuse the same row shape instead of introducing additional artifact types or status-specific payloads.
- [Side-by-side platoon layout can become cramped on smaller screens] → Mitigation: design the frontend so desktop uses paired columns while mobile can stack the two handedness columns vertically without reintroducing a view toggle.
- [Expandable history state becomes more complex with starter and alternate rows in two columns] → Mitigation: key expanded row state by handedness plus row identity so interactions remain local to the correct column.

## Migration Plan

1. Update Fangraphs batter ingest to capture handedness-specific `Bench` rows separately from the nine starter slots.
2. Update the depth chart pipeline to carry starter lineups plus alternates through candidate generation, sanitation, and publication.
3. Extend regression and QA scripts so batter validation requires both starter lineup views and the public alternates container.
4. Update the team detail Batter section layout to render simultaneous `vs RHP` / `vs LHP` columns with starter and alternate groups.
5. Build a candidate, run regression and go/no-go checks, preview the team detail page locally, and publish after review.

Rollback continues to use the existing `public/data/backups/` path for `depth-charts.json`. If the new batter contract or layout causes downstream issues, restore the prior latest artifact and redeploy the prior frontend bundle.

## Open Questions

- Whether Fangraphs uses any additional bench-like status labels besides `Bench` that should be recognized but still remain out of the public contract for this change.
- Whether alternates should visually reuse the full Batter column set or intentionally collapse to a lighter row presentation in the paired-column layout.
