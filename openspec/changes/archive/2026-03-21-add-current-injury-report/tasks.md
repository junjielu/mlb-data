## 1. Injury Data Flow

- [x] 1.1 Add a Fangraphs injury sync flow that fetches current-team injury rows and writes a standalone source artifact.
- [x] 1.2 Add validation and publish logic for a standalone `injuries` latest artifact with retain-previous-latest behavior on failed refreshes.
- [x] 1.3 Document the injury artifact metadata and team-level empty versus unavailable states in the publishing flow.

## 2. Team Page Integration

- [x] 2.1 Update the frontend data loading path so team detail pages can consume the standalone injury artifact alongside `depth-charts.json`.
- [x] 2.2 Add a `Current Injury Report` section after RP using a lightweight table with `Name`, `Pos`, `Status`, and `Latest Update`.
- [x] 2.3 Replace page-wide freshness assumptions with section-level freshness copy for the 2025 depth chart snapshot and the current injury report.

## 3. Verification

- [x] 3.1 Verify that a successful injury refresh publishes current-team injury rows without changing the core depth chart release flow.
- [x] 3.2 Verify that a failed injury refresh preserves the previously published injury latest artifact and produces the correct public fallback behavior.
- [x] 3.3 Validate the team page states for teams with current injury rows, no current injury rows, and injury data unavailable.
