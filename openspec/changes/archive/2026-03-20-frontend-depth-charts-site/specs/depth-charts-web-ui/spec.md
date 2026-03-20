## ADDED Requirements

### Requirement: Division-based team overview page
The web UI SHALL provide a teams overview page that groups all MLB teams by division and displays data status indicators.

#### Scenario: Overview grouping
- **WHEN** a user opens `/teams`
- **THEN** teams are shown under AL East, AL Central, AL West, NL East, NL Central, and NL West groupings

#### Scenario: Team status visibility
- **WHEN** overview data is rendered
- **THEN** each team card displays an `OK`, `Warning`, or `Critical` status badge
- **AND** warning count is visible when warnings exist

### Requirement: Team detail page with fixed sections
The web UI SHALL provide a team detail page that renders Batter, SP, and RP tables in a fixed order.

#### Scenario: Team route rendering
- **WHEN** a user navigates to `/team/:abbr`
- **THEN** the page renders the selected team's Batter, SP, and RP tables

#### Scenario: Fixed section order
- **WHEN** the team detail page loads
- **THEN** Batter appears before SP
- **AND** SP appears before RP

### Requirement: Data freshness and quality transparency
The web UI MUST display snapshot freshness metadata and warning summaries so users can assess trust in displayed values.

#### Scenario: Freshness metadata display
- **WHEN** a page loads snapshot data
- **THEN** it displays season, generated timestamp, and build status

#### Scenario: Warning detail access
- **WHEN** warnings are present for a team
- **THEN** the page displays a warning summary
- **AND** users can view warning details tied to section/row context

### Requirement: Missing metric rendering
The web UI SHALL render missing numeric metrics consistently and visibly.

#### Scenario: Missing value presentation
- **WHEN** a metric value is missing in the snapshot
- **THEN** the UI renders `--` in that cell
- **AND** the row remains visible in its original role/order position

### Requirement: Source traceability links
The web UI SHALL preserve player source links for data verification.

#### Scenario: Player link behavior
- **WHEN** a user clicks a player name in any table
- **THEN** the corresponding Fangraphs player page opens in a new tab
