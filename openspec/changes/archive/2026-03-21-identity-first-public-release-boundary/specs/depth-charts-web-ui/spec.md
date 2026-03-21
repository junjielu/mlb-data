## MODIFIED Requirements

### Requirement: Data freshness and quality transparency
The web UI MUST keep the public experience consumer-facing by limiting freshness context to lightweight section-level updated-time signals and by consuming release artifacts that exclude operator-oriented metadata and diagnostics.

#### Scenario: Section-level freshness display
- **WHEN** a user opens `/team/:abbr`
- **THEN** the page displays lightweight freshness context for the 2025 depth chart snapshot and the current injury report separately
- **AND** it MUST NOT present those values as one page-wide unified status banner

#### Scenario: Internal diagnostics stay out of the production UI
- **WHEN** a user browses `/teams` or `/team/:abbr`
- **THEN** the production frontend MUST NOT expose row-level warnings, warning summaries, operator-review queues, or release workflow states
- **AND** the frontend MUST NOT require QA-only artifact files to render public pages

### Requirement: Source traceability links
The web UI SHALL preserve player source links for data verification using the sanitized public release snapshot rather than internal candidate or QA artifacts.

#### Scenario: Player link behavior
- **WHEN** a user clicks a player name in any table
- **THEN** the corresponding Fangraphs player page opens in a new tab
- **AND** the link target comes from the approved public release data contract
