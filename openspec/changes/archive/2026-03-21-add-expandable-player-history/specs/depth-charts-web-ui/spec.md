## ADDED Requirements

### Requirement: Team detail rows support expandable recent history
The web UI SHALL render 2025 depth chart rows by default on `/team/:abbr` and allow users to expand a player row inline to view that player's 2024 and 2023 history within the same section table.

#### Scenario: Team detail loads collapsed primary rows
- **WHEN** a user opens `/team/:abbr`
- **THEN** the Batter, SP, and RP sections initially render only the 2025 primary rows

#### Scenario: Clicking a player row expands recent history
- **WHEN** a user clicks a 2025 player row in the Batter, SP, or RP section
- **THEN** the UI renders inline history rows for seasons 2024 and 2023 directly beneath that player's primary row

#### Scenario: Clicking an expanded player row collapses recent history
- **WHEN** a user clicks a player row that is already expanded
- **THEN** the UI collapses that player's inline 2024 and 2023 history rows

#### Scenario: Expansion is limited per section
- **WHEN** a user expands a player row within Batter, SP, or RP
- **THEN** any previously expanded row in that same section is collapsed
- **AND** expanded state in other sections remains unchanged

### Requirement: Expanded history preserves comparison behavior
The web UI MUST preserve the existing table comparison model when recent history rows are expanded beneath a 2025 primary row.

#### Scenario: Expanded rows align with primary row columns
- **WHEN** the UI renders expanded 2024 and 2023 history rows
- **THEN** the historical rows use the same section-specific column structure as the 2025 primary row
- **AND** each historical row clearly identifies its season

#### Scenario: Sorting remains anchored to primary rows
- **WHEN** a user sorts the Batter, SP, or RP table by any supported column
- **THEN** the sort order is determined by the 2025 primary rows
- **AND** any expanded 2024 and 2023 rows remain attached beneath their owning primary row after sorting

#### Scenario: Missing historical values use existing missing rendering
- **WHEN** a historical metric value is absent in an expanded row
- **THEN** the corresponding table cell renders `--`
- **AND** the historical row remains visible in its expanded position
