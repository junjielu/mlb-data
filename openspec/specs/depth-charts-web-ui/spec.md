# depth-charts-web-ui Specification

## Purpose
TBD - created by archiving change frontend-depth-charts-site. Update Purpose after archive.
## Requirements
### Requirement: Division-based team overview page
The web UI SHALL provide a teams overview page that groups all MLB teams by division and serves as a simple navigation surface for approved depth chart pages.

#### Scenario: Overview grouping
- **WHEN** a user opens `/teams`
- **THEN** teams are shown under AL East, AL Central, AL West, NL East, NL Central, and NL West groupings

#### Scenario: Overview remains consumer-facing
- **WHEN** overview data is rendered
- **THEN** each team card links to the approved depth chart detail page
- **AND** the page MUST NOT display internal warning counts, publish-review states, or operator-only quality badges

#### Scenario: Overview avoids exploratory controls
- **WHEN** a user browses `/teams`
- **THEN** the page MUST NOT display season selection, division filtering, or free-text search controls
- **AND** team cards MUST NOT display roster-count summaries for batter, SP, or RP rows

### Requirement: Team detail page with fixed sections
The web UI SHALL provide a team detail page that renders Batter, SP, RP, and Current Injury Report sections in a fixed order.

#### Scenario: Team route rendering
- **WHEN** a user navigates to `/team/:abbr`
- **THEN** the page renders the selected team's Batter, SP, RP, and Current Injury Report sections

#### Scenario: Fixed section order
- **WHEN** the team detail page loads
- **THEN** Batter appears before SP
- **AND** SP appears before RP
- **AND** RP appears before Current Injury Report

### Requirement: Data freshness and quality transparency
The web UI MUST keep the public experience consumer-facing by limiting freshness context to lightweight section-level updated-time signals and by consuming release artifacts that exclude operator-oriented metadata and diagnostics.

#### Scenario: Section-level freshness display
- **WHEN** a user opens `/team/:abbr`
- **THEN** the page displays lightweight freshness context for the 2025 depth chart snapshot and the current injury report separately
- **AND** it MUST NOT present those values as one page-wide unified status banner

#### Scenario: Internal diagnostics stay out of the production UI
- **WHEN** a user browses `/teams` or `/team/:abbr`
- **THEN** the production frontend MUST NOT expose row-level warnings, warning summaries, operator-review queues, or release workflow states

### Requirement: Source traceability links
The web UI SHALL preserve player source links for data verification using the sanitized public release snapshot rather than internal candidate or QA artifacts.

#### Scenario: Player link behavior
- **WHEN** a user clicks a player name in any table
- **THEN** the corresponding Fangraphs player page opens in a new tab
- **AND** the link target comes from the approved public release data contract

### Requirement: Current injury report presentation
The web UI SHALL present current-season Fangraphs injury data as display-only context on team detail pages without altering Batter, SP, or RP table rows.

#### Scenario: Injury context stays separate from depth chart rows
- **WHEN** current injury data exists for a team
- **THEN** the page renders it in a dedicated `Current Injury Report` section
- **AND** the UI MUST NOT inject injury badges or injury status text into Batter, SP, or RP rows

### Requirement: Lightweight injury table for public browsing
The web UI SHALL render the current injury section as a lightweight table that prioritizes readability of the latest update text.

#### Scenario: Public injury columns
- **WHEN** a team has current injury rows
- **THEN** the injury section displays `Name`, `Pos`, `Status`, and `Latest Update`
- **AND** the `Latest Update` field remains visible as the primary explanatory text for each row

### Requirement: Distinct empty and unavailable injury states
The web UI SHALL distinguish between a team having no current injury entries and the injury dataset being temporarily unavailable.

#### Scenario: No current injury entries
- **WHEN** the injury artifact reports no current injury rows for a team
- **THEN** the page communicates that Fangraphs has no current injury entries for that team

#### Scenario: Injury data unavailable
- **WHEN** the current injury dataset cannot be loaded for the team page
- **THEN** the page communicates that current injury data is temporarily unavailable
- **AND** it MUST NOT imply that the team has no injuries

### Requirement: Missing metric rendering
The web UI SHALL render missing numeric metrics consistently and visibly.

#### Scenario: Missing value presentation
- **WHEN** a metric value is missing in the snapshot
- **THEN** the UI renders `--` in that cell
- **AND** the row remains visible in its original role/order position

### Requirement: Public navigation stays focused on depth chart browsing
The web UI SHALL keep the primary public navigation focused on approved team depth chart pages rather than maintenance-oriented explainer content.

#### Scenario: About page removed from primary navigation
- **WHEN** the public site navigation is rendered
- **THEN** it links users to the teams browsing experience
- **AND** it MUST NOT present `/about-data` as a primary public destination

### Requirement: Batter table displays counting stats after position
The web UI SHALL display batter counting stats `R`, `HR`, `RBI`, and `SB` on the team detail page Batter table immediately after the `Position` column, keep `AVG`, `OBP`, and `SLG` ahead of `wRC+`, and place `wRC+` in the final Batter column.

#### Scenario: Team detail batter columns include counting stats
- **WHEN** a user opens `/team/:abbr`
- **THEN** the Batter table columns appear in the order `Order`, `Name`, `Position`, `R`, `HR`, `RBI`, `SB`, `AVG`, `OBP`, `SLG`, `wRC+`
- **AND** each counting stat cell is rendered from the approved public `depth-charts.json` artifact rather than a live Fangraphs request

### Requirement: Newly added batter counting stats use existing missing-value treatment
The web UI MUST apply the existing missing metric presentation to batter counting stats `R`, `HR`, `RBI`, and `SB`.

#### Scenario: Missing batter counting stat presentation
- **WHEN** any of the newly added batter counting stat fields are empty in the public snapshot
- **THEN** the corresponding Batter table cell renders `--`
- **AND** the row remains visible in its original lineup order

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

### Requirement: Team detail player names display age inline
The web UI SHALL display a player's age inline to the right of the linked player name on Batter, SP, and RP primary rows on `/team/:abbr`.

#### Scenario: Batter row shows age beside name
- **WHEN** a Batter primary row has an age value in the approved public snapshot
- **THEN** the team detail page renders that age inline to the right of the player's linked name
- **AND** the age display remains part of the same name cell rather than a separate table column

#### Scenario: Pitcher rows show age beside name
- **WHEN** an SP or RP primary row has an age value in the approved public snapshot
- **THEN** the team detail page renders that age inline to the right of the player's linked name
- **AND** the existing role/order columns and metric columns remain unchanged

#### Scenario: Missing age stays visually quiet
- **WHEN** a Batter, SP, or RP primary row has no age value in the public snapshot
- **THEN** the team detail page renders the linked player name without an age label
- **AND** it MUST NOT show a missing-value placeholder beside the name

### Requirement: Batter section supports platoon lineup view switching
The web UI SHALL render the team detail Batter section as a switchable platoon lineup view so users can inspect projected starters against right-handed and left-handed pitching without leaving `/team/:abbr`.

#### Scenario: Batter section defaults to right-handed-pitching view
- **WHEN** a user opens `/team/:abbr`
- **THEN** the Batter section initially renders the `vs RHP` lineup view from the approved public snapshot
- **AND** the page provides a visible control to switch the Batter section to the `vs LHP` lineup view

#### Scenario: User switches to left-handed-pitching view
- **WHEN** a user selects the `vs LHP` control in the Batter section
- **THEN** the Batter table rerenders using the approved `vsL` lineup rows for that team
- **AND** the existing Batter columns, sorting, missing-value rendering, and expandable history behavior remain available in the selected view

### Requirement: Batter platoon-only starters are labeled inline
The web UI SHALL surface platoon-only starter context directly in the Batter table so users can tell when a player starts only against one pitcher handedness.

#### Scenario: Right-handed-pitching-only starter is labeled
- **WHEN** a Batter row in the active lineup view carries the public marker for a player who starts only against right-handed pitching
- **THEN** the team detail page renders a lightweight inline label beside that player's name indicating `vs RHP only`
- **AND** the label remains secondary to the player name and metrics

#### Scenario: Left-handed-pitching-only starter is labeled
- **WHEN** a Batter row in the active lineup view carries the public marker for a player who starts only against left-handed pitching
- **THEN** the team detail page renders a lightweight inline label beside that player's name indicating `vs LHP only`
- **AND** the label remains secondary to the player name and metrics

#### Scenario: Everyday starter remains unlabeled in the name cell
- **WHEN** a Batter row represents a player who starts in both lineup views
- **THEN** the team detail page renders the linked player name without a platoon-only label
- **AND** it MUST NOT show a placeholder or neutral badge for the player
