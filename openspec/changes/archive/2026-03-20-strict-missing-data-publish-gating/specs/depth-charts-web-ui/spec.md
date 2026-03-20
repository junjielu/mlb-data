## MODIFIED Requirements

### Requirement: Division-based team overview page
The web UI SHALL provide a teams overview page that groups all MLB teams by division and presents approved depth chart entries without exposing internal release diagnostics.

#### Scenario: Overview grouping
- **WHEN** a user opens `/teams`
- **THEN** teams are shown under AL East, AL Central, AL West, NL East, NL Central, and NL West groupings

#### Scenario: Overview remains consumer-facing
- **WHEN** overview data is rendered
- **THEN** each team card links to the approved depth chart detail page
- **AND** the page MUST NOT display internal warning counts, publish-review states, or operator-only quality badges

### Requirement: Data freshness and quality transparency
The web UI MUST display freshness metadata for the approved snapshot while keeping internal quality diagnostics out of the production frontend.

#### Scenario: Freshness metadata display
- **WHEN** a page loads snapshot data
- **THEN** it displays season, generated timestamp, and approved build context needed to understand data recency

#### Scenario: Internal diagnostics stay out of the production UI
- **WHEN** a user browses `/teams`, `/team/:abbr`, or `/about-data`
- **THEN** the production frontend MUST NOT expose row-level warnings, warning summaries, or operator-review queues
