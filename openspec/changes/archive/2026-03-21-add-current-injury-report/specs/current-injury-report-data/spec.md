## ADDED Requirements

### Requirement: Standalone current injury snapshot publication
The system SHALL publish Fangraphs RosterResource injury data as a standalone current-season artifact separate from the pinned 2025 depth chart snapshot.

#### Scenario: Successful standalone injury publish
- **WHEN** the injury pipeline completes a successful fetch and validation run
- **THEN** it publishes a latest injury artifact independently of `depth-charts.json`
- **AND** the injury artifact records that it represents Fangraphs current-season injury data

### Requirement: Fangraphs injury field preservation
The system SHALL preserve the source-level injury details needed to support current public rendering and later extensions.

#### Scenario: Published injury rows retain source fields
- **WHEN** an injury row is published for a team
- **THEN** the row includes the player identity, position, status, and latest update text used by the public UI
- **AND** the artifact retains the Fangraphs injury detail fields required for later display expansion

### Requirement: Best-effort latest retention
The system MUST preserve the last approved injury latest artifact when a new current-season injury refresh fails.

#### Scenario: Failed refresh keeps prior latest
- **WHEN** an injury fetch or validation run fails
- **THEN** the existing published injury latest artifact remains available to the frontend
- **AND** the failed refresh does not overwrite the prior approved injury snapshot

### Requirement: Team-scoped current injury availability
The system SHALL organize published injury data by MLB team so a team detail page can load current injury context for a single club.

#### Scenario: Team page can resolve injuries by team
- **WHEN** the frontend requests injury data for a team detail page
- **THEN** the published injury artifact provides the current injury rows for that team
- **AND** a team with no current injury entries is distinguishable from a case where injury data is unavailable
