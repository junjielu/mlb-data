## ADDED Requirements

### Requirement: Risk-based operator review before publish
The system MUST require operator review before publishing a candidate snapshot when high-risk rows remain classified as `unknown`.

#### Scenario: High-risk unknown requires review
- **WHEN** the pipeline finishes candidate generation and at least one high-risk row is classified as `unknown`
- **THEN** the candidate is marked as requiring operator review
- **AND** the candidate MUST NOT be promoted to `public/data/latest` automatically

#### Scenario: Approved review allows promotion
- **WHEN** a candidate has no blocking failures and all required operator review steps have been approved
- **THEN** the candidate may be promoted to `public/data/latest`
- **AND** the promoted build becomes the approved release snapshot

## MODIFIED Requirements

### Requirement: Quality report generation
The system SHALL produce a quality report for every pipeline run, including structural failures, missing-data attribution, and any operator review requirements.

#### Scenario: Report includes attributed missing summary
- **WHEN** the pipeline finishes candidate generation
- **THEN** it emits `quality-report.json`
- **AND** the report includes counts for `source_missing`, `lookup_failed`, and `unknown` rows

#### Scenario: Report includes review queue
- **WHEN** high-risk `unknown` rows are present
- **THEN** the quality report records those rows as pending operator review
- **AND** the report identifies the team, section, slot, and evidence needed for review

### Requirement: Publish gating and atomic promotion
The system MUST publish a new snapshot to the `latest` path only if structural checks pass, blocking attribution failures are absent, and any required operator review has been approved.

#### Scenario: Automatic gate pass promotion
- **WHEN** the candidate has no structural failures, no regression failures, no `lookup_failed` rows, and no pending review requirements
- **THEN** the candidate is atomically promoted to `public/data/latest`

#### Scenario: Blocking attribution failure prevents promotion
- **WHEN** the candidate contains any `lookup_failed` row or other blocking gate failure
- **THEN** `public/data/latest` remains unchanged
- **AND** the candidate is marked as not publishable

#### Scenario: Pending review prevents automatic promotion
- **WHEN** the candidate contains high-risk `unknown` rows awaiting review
- **THEN** `public/data/latest` remains unchanged
- **AND** the candidate can be promoted only after explicit operator approval

### Requirement: Name and ID fallback matching
The ingestion pipeline SHALL preserve match evidence from fallback resolution so missing metrics can be attributed to source absence, lookup failure, or unresolved uncertainty.

#### Scenario: Evidence preserved for successful fallback
- **WHEN** a roster row resolves through exact name, player ID, normalized name, or other supported fallback logic
- **THEN** the pipeline records which matching method resolved the row
- **AND** the final artifact retains enough evidence to audit that resolution path

#### Scenario: Evidence preserved for unresolved row
- **WHEN** a roster row still has missing metrics after all supported lookup strategies run
- **THEN** the pipeline records the failed lookup context needed to classify the row as `source_missing`, `lookup_failed`, or `unknown`
- **AND** the row is not treated as an unexplained empty result
