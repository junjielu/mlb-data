## MODIFIED Requirements

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
The web UI MUST keep the public experience consumer-facing by limiting freshness context to lightweight section-level updated-time signals and by excluding operator-oriented metadata and diagnostics from public pages.

#### Scenario: Section-level freshness display
- **WHEN** a user opens `/team/:abbr`
- **THEN** the page displays lightweight freshness context for the 2025 depth chart snapshot and the current injury report separately
- **AND** it MUST NOT present those values as one page-wide unified status banner

#### Scenario: Internal diagnostics stay out of the production UI
- **WHEN** a user browses `/teams` or `/team/:abbr`
- **THEN** the production frontend MUST NOT expose row-level warnings, warning summaries, operator-review queues, or release workflow states

## ADDED Requirements

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
