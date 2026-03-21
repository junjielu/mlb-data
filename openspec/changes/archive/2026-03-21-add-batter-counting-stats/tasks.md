## 1. Batter Data Contract

- [x] 1.1 Update `scripts/fangraphs_batter_sync.py` to capture Fangraphs `R`, `HR`, `RBI`, and `SB` values in each batter row alongside the existing metrics.
- [x] 1.2 Verify the generated batter JSON and published snapshot preserve the new counting stat fields without exposing operator-only diagnostics or changing the 2025 season guardrails.

## 2. Batter Table UI

- [x] 2.1 Update the team detail Batter table in `public/app.js` to render `R`, `HR`, `RBI`, and `SB` immediately after `Position` and move `wRC+` to the final column.
- [x] 2.2 Confirm missing counting stat values reuse the existing `--` rendering and make any minimal table styling adjustments required for readability.

## 3. Validation

- [x] 3.1 Run the depth chart build flow needed to produce a candidate or latest snapshot containing the new batter fields.
- [x] 3.2 Validate the local web experience for `/team/:abbr` to confirm the new columns render in the correct order and display approved snapshot data.
