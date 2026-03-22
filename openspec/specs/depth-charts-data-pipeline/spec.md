# depth-charts-data-pipeline Specification

## Purpose
TBD - created by archiving change frontend-depth-charts-site. Update Purpose after archive.
## Requirements
### Requirement: Public release artifacts are isolated from operator workflow artifacts
The system MUST isolate operator workflow artifacts from public release artifacts so browser-consumable files under `public/data/latest/` contain only approved release data.

#### Scenario: Candidate artifacts stay outside the public release surface
- **WHEN** the pipeline builds a candidate snapshot, quality report, review record, or QA output
- **THEN** those operator artifacts are written to an internal artifact area outside `public/data/latest/`
- **AND** they are not part of the browser-facing release directory by default

#### Scenario: Approved publish emits only consumer-facing files
- **WHEN** a reviewed build is promoted to the public release path
- **THEN** `public/data/latest/` contains only release artifacts intended for frontend consumption
- **AND** it MUST NOT contain candidate-only review records, QA reports, or operator gating files

### Requirement: Unified snapshot generation
The system SHALL generate a unified public depth chart snapshot for a target season that combines Batter, SP, and RP data for all 30 MLB teams while excluding operator-only workflow fields from the published release artifact.

#### Scenario: Successful snapshot generation
- **WHEN** the pipeline publishes an approved release for a valid season (for example 2025)
- **THEN** it produces a public `depth-charts.json` artifact containing exactly 30 teams
- **AND** each team includes `batter`, `sp`, and `rp` sections

#### Scenario: Section order contract
- **WHEN** a team snapshot is generated for public release
- **THEN** the published section order SHALL be Batter, then SP, then RP

#### Scenario: Published rows omit operator diagnostics
- **WHEN** a public release snapshot is generated
- **THEN** published team rows omit warning summaries, review-state fields, and other operator-only diagnostics
- **AND** the public snapshot remains a consumer-facing release contract rather than a QA artifact

### Requirement: Publish gating and atomic promotion
The system MUST publish a new snapshot to the `latest` path only if structural checks pass, blocking attribution failures are absent, and any required operator review has been approved, and the publish step MUST promote sanitized public release artifacts rather than raw internal candidate artifacts.

#### Scenario: Automatic gate pass promotion
- **WHEN** the candidate has no structural failures, no regression failures, no `lookup_failed` rows, and no pending review requirements
- **THEN** the pipeline atomically promotes sanitized release artifacts to `public/data/latest/`

#### Scenario: Blocking attribution failure prevents promotion
- **WHEN** the candidate contains any `lookup_failed` row or other blocking gate failure
- **THEN** `public/data/latest` remains unchanged
- **AND** the candidate is marked as not publishable

#### Scenario: Pending review prevents automatic promotion
- **WHEN** the candidate contains high-risk `unknown` rows awaiting review
- **THEN** `public/data/latest` remains unchanged
- **AND** the candidate can be promoted only after explicit operator approval

### Requirement: Name and ID fallback matching
The ingestion pipeline SHALL treat the Fangraphs depth chart roster row identity as authoritative, preserve match evidence from fallback resolution, and forbid automatic cross-player fallback when the source roster identity and resolved stats identity disagree.

#### Scenario: Source player identity drives successful resolution
- **WHEN** a roster row exposes a numeric source player ID that exists in the stats source
- **THEN** the pipeline resolves the row through that source player ID before considering weaker name-based matching paths
- **AND** the final row records that identity-preserving resolution method

#### Scenario: Mismatched fallback cannot auto-resolve a row
- **WHEN** a fallback candidate matches by name or normalization but resolves to a different numeric player ID than the source roster row
- **THEN** the pipeline MUST NOT accept that candidate as a successful automatic match
- **AND** the row remains unresolved or is routed into operator review evidence instead of publishing mismatched stats

#### Scenario: Evidence preserved for unresolved row
- **WHEN** a roster row still has missing metrics after all supported lookup strategies run
- **THEN** the pipeline records the failed lookup context needed to classify the row as `source_missing`, `lookup_failed`, or `unknown`
- **AND** the row is not treated as an unexplained empty result

### Requirement: Published batter rows retain Fangraphs counting stats
The depth charts data pipeline SHALL retain Fangraphs batter counting stats `R`, `HR`, `RBI`, and `SB` on each published batter row in the public `depth-charts.json` artifact when those values are available from the existing batting source response.

#### Scenario: Public batter release includes counting stats
- **WHEN** the pipeline builds and publishes a batter row from the Fangraphs batting leaders response
- **THEN** the published row includes `R`, `HR`, `RBI`, and `SB` fields alongside the existing batter metrics
- **AND** the row continues to preserve the matched player identity and source traceability fields already carried in the public release contract

#### Scenario: Missing counting stats do not introduce operator-only fields
- **WHEN** one or more of the added counting stat values are absent for a batter row
- **THEN** the public release row may leave those counting stat fields empty
- **AND** the published artifact MUST NOT expose operator-only diagnostics or review metadata to explain the absence

### Requirement: Public depth chart rows expose consumer-facing player identity
The depth charts data pipeline SHALL expose a stable consumer-facing `playerId` on each published Batter, SP, and RP row in the public `depth-charts.json` release artifact without exposing operator-only identity resolution diagnostics.

#### Scenario: Published row includes public player identifier
- **WHEN** a public `depth-charts.json` release is generated
- **THEN** each published Batter, SP, and RP row includes a `playerId` field
- **AND** the published row MUST NOT expose operator-only identity matching evidence such as `match_method`, `source_player_id`, or `matched_player_id`

### Requirement: Public depth chart rows include recent season history
The depth charts data pipeline SHALL publish recent season history for each public Batter, SP, and RP row as consumer-facing season entries for 2024 and 2023.

#### Scenario: Published row carries ordered recent history
- **WHEN** recent history is available for a published player row
- **THEN** the row includes a `history` collection with season entries for 2024 and 2023
- **AND** the entries are ordered from most recent season to least recent season

#### Scenario: Historical season entries remain consumer-facing
- **WHEN** a public historical season entry is published
- **THEN** it contains only the season label and consumer-facing baseball metrics needed by the web UI
- **AND** it MUST NOT include operator diagnostics, review metadata, or QA-only fields

#### Scenario: Missing historical values do not block publication
- **WHEN** one or more historical metric values are unavailable for a row's 2024 or 2023 history entry
- **THEN** the release artifact may leave those metric fields empty
- **AND** the row remains publishable without adding operator-only explanation fields to the public contract

### Requirement: Public depth chart rows retain Fangraphs player age
The depth charts data pipeline SHALL retain each Fangraphs player row's current age on public Batter, SP, and RP rows in the published `depth-charts.json` artifact.

#### Scenario: Public release rows include age on primary players
- **WHEN** the pipeline builds and publishes a Batter, SP, or RP row from the Fangraphs source data
- **THEN** the published primary row includes an `age` field sourced from the parsed Fangraphs player row
- **AND** the age field is available for frontend consumption alongside the existing public player fields

#### Scenario: Missing age does not expose operator-only metadata
- **WHEN** Fangraphs does not provide a usable age value for a published Batter, SP, or RP row
- **THEN** the public row may leave the `age` field empty
- **AND** the published artifact MUST NOT expose operator-only diagnostics or review metadata to explain the missing age

### Requirement: Public batter publication exposes platoon lineup views
The depth charts data pipeline SHALL publish the Batter section as a consumer-facing platoon lineup container that preserves separate projected go-to lineups against right-handed and left-handed pitching within the approved public `depth-charts.json` artifact.

#### Scenario: Public batter artifact includes both lineup views
- **WHEN** the pipeline publishes an approved public depth chart snapshot
- **THEN** each team's Batter section includes a `vsR` lineup view and a `vsL` lineup view
- **AND** each lineup view contains the ordered projected batter rows for that handedness

#### Scenario: Existing public batter row fields remain available in each lineup view
- **WHEN** a public batter lineup row is published under `vsR` or `vsL`
- **THEN** the row retains the existing consumer-facing batter metrics, player link, public player identifier, age, and recent history fields
- **AND** the published artifact MUST NOT expose operator-only diagnostics or review metadata in either lineup view

### Requirement: Public batter publication exposes handedness-specific alternates
The depth charts data pipeline SHALL publish the Batter section with handedness-specific public alternates derived from Fangraphs platoon-page bench rows so consumers can inspect each lineup's bench context alongside the approved starter views.

#### Scenario: Public batter artifact includes alternates for both lineup views
- **WHEN** the pipeline publishes an approved public depth chart snapshot
- **THEN** each team's Batter section includes an `alternates` container with `vsR` and `vsL` collections
- **AND** those collections are published alongside the existing `lineups.vsR` and `lineups.vsL` starter views

#### Scenario: Only Fangraphs bench rows are promoted into public alternates
- **WHEN** the batter ingest parses non-starter rows from a Fangraphs platoon lineup page
- **THEN** only rows representing Fangraphs bench entries are included in the public `alternates` collections
- **AND** projected injured-list rows or other non-bench statuses are excluded from the public alternates contract

#### Scenario: Alternate rows retain the existing public batter row shape
- **WHEN** a public batter alternate row is published under `alternates.vsR` or `alternates.vsL`
- **THEN** the row retains the existing consumer-facing batter metrics, player link, public player identifier, age, recent history, and platoon role fields
- **AND** the published artifact MUST NOT expose operator-only diagnostics or review metadata in alternate rows

### Requirement: Public batter rows include consumer-facing platoon role markers
The depth charts data pipeline SHALL derive a lightweight consumer-facing platoon role marker on published batter rows across both starter lineups and alternates so consumers can distinguish one-sided platoon usage from shared handedness usage without comparing every collection manually.

#### Scenario: Batter row is labeled as right-handed-pitching-only option
- **WHEN** a published batter appears only in the `vsR` collection of a given batter row type for the same team
- **THEN** the public row includes a platoon role marker indicating that the player is published only against right-handed pitching

#### Scenario: Batter row is labeled as left-handed-pitching-only option
- **WHEN** a published batter appears only in the `vsL` collection of a given batter row type for the same team
- **THEN** the public row includes a platoon role marker indicating that the player is published only against left-handed pitching

#### Scenario: Shared handedness option remains unlabeled
- **WHEN** a published batter appears in both `vsR` and `vsL` collections for the same team and batter row type
- **THEN** the public row omits the one-sided platoon marker
- **AND** the consumer-facing artifact remains visually quiet for non-platoon entries

### Requirement: Batter publish gating validates both platoon lineup views
The depth charts data pipeline MUST validate structural completeness of both published batter platoon lineup views and the presence of handedness-specific alternates containers before promoting a new public snapshot.

#### Scenario: Missing platoon lineup view blocks publish
- **WHEN** a candidate snapshot is missing either the `vsR` batter lineup or the `vsL` batter lineup for any team
- **THEN** the candidate is marked as not publishable
- **AND** `public/data/latest/depth-charts.json` remains unchanged

#### Scenario: Missing alternates container blocks publish
- **WHEN** a candidate snapshot omits `alternates.vsR` or `alternates.vsL` for any team's Batter section
- **THEN** the candidate is marked as not publishable
- **AND** `public/data/latest/depth-charts.json` remains unchanged

#### Scenario: Existing batter regression baseline remains anchored to default right-handed starter view
- **WHEN** regression checks evaluate known batter lineup fixtures after public alternates are introduced
- **THEN** the existing batter regression cases read from the default `lineups.vsR` starter view
- **AND** the new structural validation still requires both starter lineup views and both alternates collections to be present
