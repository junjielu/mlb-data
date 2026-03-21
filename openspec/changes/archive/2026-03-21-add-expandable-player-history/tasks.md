## 1. Historical data contract

- [x] 1.1 Define the public row shape for `playerId` and `history` across Batter, SP, and RP in the 2025 depth charts release flow.
- [x] 1.2 Extend the Fangraphs sync/build path so each row can resolve 2024 and 2023 historical season metrics for the same player.
- [x] 1.3 Preserve `playerId` and `history` in the sanitized public snapshot while continuing to exclude operator-only identity and QA fields.

## 2. Team detail interaction

- [x] 2.1 Update the team detail table renderer to support one expanded row per section and inline 2024/2023 history rows beneath the 2025 primary row.
- [x] 2.2 Preserve existing section sorting so only 2025 primary rows are reordered and expanded history rows remain attached to their owning row.
- [x] 2.3 Add styling and row affordances that make expanded history readable without changing the current section layout model.

## 3. Verification and documentation

- [x] 3.1 Verify Batter, SP, and RP sections render `--` for missing historical values and continue opening Fangraphs player links correctly.
- [x] 3.2 Rebuild a candidate depth charts snapshot and confirm the public `depth-charts.json` contract includes consumer-facing `playerId` and `history` data only.
- [x] 3.3 Update supporting OpenSpec or runbook documentation if implementation decisions change the public contract details or historical metric expectations.
