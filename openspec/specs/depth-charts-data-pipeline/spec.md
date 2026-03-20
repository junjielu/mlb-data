# depth-charts-data-pipeline Specification

## Purpose
TBD - created by archiving change frontend-depth-charts-site. Update Purpose after archive.
## Requirements
### Requirement: Unified snapshot generation
The system SHALL generate a unified depth chart snapshot for a target season that combines Batter, SP, and RP data for all 30 MLB teams.

#### Scenario: Successful snapshot generation
- **WHEN** the pipeline runs for a valid season (for example 2025)
- **THEN** it produces a `depth-charts.json` artifact containing exactly 30 teams
- **AND** each team includes `batter`, `sp`, and `rp` sections

#### Scenario: Section order contract
- **WHEN** a team snapshot is generated
- **THEN** the published section order SHALL be Batter, then SP, then RP

### Requirement: Quality report generation
The system SHALL produce a quality report for every pipeline run, including warning counts and blocking validation failures.

#### Scenario: Report includes warning summary
- **WHEN** the pipeline finishes successfully
- **THEN** it emits `quality-report.json`
- **AND** the report includes per-team warning counts and total warning count

#### Scenario: Report includes validation failures
- **WHEN** required structural checks fail
- **THEN** the report records the failed checks with severity `critical`

### Requirement: Publish gating and atomic promotion
The system MUST publish a new snapshot to the `latest` path only if gating checks pass.

#### Scenario: Gate pass promotion
- **WHEN** all release gates pass
- **THEN** the candidate artifacts are atomically promoted to `public/data/latest`

#### Scenario: Gate failure blocks promotion
- **WHEN** any critical gate fails
- **THEN** `public/data/latest` remains unchanged
- **AND** the run is marked as failed or partial according to gate policy

### Requirement: Name and ID fallback matching
The ingestion pipeline SHALL resolve player stats using deterministic fallback matching to reduce missing data from naming variance.

#### Scenario: Player ID fallback resolves alias mismatch
- **WHEN** a roster row includes a valid `playerid` but the display name differs from leaders API naming
- **THEN** the pipeline uses `playerid` to map stats before name-based fallback

#### Scenario: Name normalization fallback
- **WHEN** exact name match fails and no valid `playerid` match exists
- **THEN** the pipeline attempts normalized name matching
- **AND** records unresolved rows as warnings, not silent drops

