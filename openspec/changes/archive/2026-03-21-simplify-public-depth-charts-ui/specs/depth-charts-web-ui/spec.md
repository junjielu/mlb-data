## MODIFIED Requirements

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

### Requirement: Data freshness and quality transparency
The web UI MUST keep the public experience consumer-facing by limiting freshness context to a lightweight updated-time signal and by excluding operator-oriented metadata and diagnostics from public pages.

#### Scenario: Minimal freshness display
- **WHEN** a user opens `/team/:abbr`
- **THEN** the page displays a lightweight updated-time indicator
- **AND** it MUST NOT display season, source, or build identifier metadata as a status banner

#### Scenario: Internal diagnostics stay out of the production UI
- **WHEN** a user browses `/teams` or `/team/:abbr`
- **THEN** the production frontend MUST NOT expose row-level warnings, warning summaries, operator-review queues, or release workflow states

### Requirement: Public navigation stays focused on depth chart browsing
The web UI SHALL keep the primary public navigation focused on approved team depth chart pages rather than maintenance-oriented explainer content.

#### Scenario: About page removed from primary navigation
- **WHEN** the public site navigation is rendered
- **THEN** it links users to the teams browsing experience
- **AND** it MUST NOT present `/about-data` as a primary public destination
