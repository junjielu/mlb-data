## ADDED Requirements

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
