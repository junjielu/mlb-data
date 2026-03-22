## ADDED Requirements

### Requirement: Public pitcher rows use a unified consumer-facing metric contract
The depth charts data pipeline SHALL publish both SP and RP rows, including recent-history entries, with the same ordered consumer-facing metric set: `ERA`, `WHIP`, `K/9`, `BB/9`, `Stuff+`, `Location+`, `vFA`, and `BABIP`.

#### Scenario: Published SP and RP primary rows share the same metric fields
- **WHEN** the pipeline generates a public `depth-charts.json` release artifact
- **THEN** each published SP and RP primary row includes `era`, `whip`, `k9`, `bb9`, `stuff_plus`, `location_plus`, `vfa`, and `babip`
- **AND** RP rows MUST NOT publish `k_pct` in the public release artifact

#### Scenario: Published pitcher history rows use the same metric contract
- **WHEN** the pipeline publishes 2024 and 2023 history entries for an SP or RP row
- **THEN** each history entry includes only the season label and the consumer-facing pitcher metrics `era`, `whip`, `k9`, `bb9`, `stuff_plus`, `location_plus`, `vfa`, and `babip`
- **AND** RP history entries MUST NOT publish `k_pct`

#### Scenario: Missing unified pitcher metrics do not block publication
- **WHEN** Fangraphs does not provide a usable `whip`, `location_plus`, `vfa`, or `babip` value for a published SP or RP row or history entry
- **THEN** the pipeline may leave that public metric field empty
- **AND** the row remains publishable without exposing operator-only diagnostics

### Requirement: Pitcher ingestion sources vFA and BABIP from Fangraphs
The depth charts data pipeline SHALL source `vfa` and `babip` from Fangraphs for both SP and RP rows before assembling the public depth chart snapshot.

#### Scenario: Current-season pitcher rows retain Fangraphs vFA and BABIP
- **WHEN** the SP or RP sync flow normalizes a Fangraphs pitcher row for the target season
- **THEN** the normalized row includes consumer-facing `vfa` and `babip` values when Fangraphs provides them
- **AND** those values are available to the depth chart publish pipeline for public release

#### Scenario: Historical pitcher rows retain Fangraphs vFA and BABIP
- **WHEN** the pipeline fetches 2024 or 2023 pitcher history for a public SP or RP row
- **THEN** the history lookup preserves `vfa` and `babip` using the same public field names as the current-season row
- **AND** the published history remains consumer-facing rather than source-schema-specific
