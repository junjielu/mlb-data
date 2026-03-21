## Context

The repository currently has a workable build/review/publish shape, but two cross-cutting problems remain.

First, batter, SP, and RP ingestion do not share one authoritative player-resolution strategy. Batter already leans toward source player identity from the Fangraphs depth chart row, but SP and RP still allow weaker name-based paths to resolve rows. That inconsistency makes the pipeline vulnerable to same-name mismatches and section-specific behavior drift.

Second, the public release boundary is blurred. Candidate, quality, review, and warning-oriented data are still written under `public/data/`, and the published `depth-charts.json` includes operator-oriented warning fields even though the public site is meant to consume approved release data only.

Constraints:

- The maintained season stays pinned to `2025` unless a separate change says otherwise.
- The main public snapshot schema major version does not change as part of this work.
- Fangraphs depth chart roster rows remain the source of truth for slot order and source player identity.
- Candidate and review workflows still need to exist, but they do not need to live in the public static directory.

## Goals / Non-Goals

**Goals:**

- Make Fangraphs roster-row identity the primary key for batter, SP, and RP stats resolution.
- Prevent silent cross-player fallback when the source roster row and resolved stats row disagree.
- Preserve enough internal evidence for QA and operator review without leaking that evidence into public release files.
- Redefine `public/data/latest/` as a clean consumer-facing release surface containing only approved data the frontend should load.
- Keep the existing release workflow shape of candidate build, QA/review, approval, publish, and rollback.

**Non-Goals:**

- Replacing Fangraphs as the source of roster order or player stats.
- Changing the public site IA or adding new end-user pages.
- Eliminating every unresolved Fangraphs edge case in one pass.
- Building a general-purpose artifact management framework outside this depth chart workflow.

## Decisions

### 1) Introduce one shared identity-first resolution model for batter, SP, and RP

- Decision: Every roster row will resolve stats by this priority order: source player ID from the Fangraphs depth chart row, explicit source-row player ID from structured roster data when available, targeted player-ID lookup, and only then constrained name-based diagnosis paths.
- Rationale: The depth chart row already defines the intended player occupying the slot. Resolution should preserve that identity instead of treating names as interchangeable keys.
- Alternative considered: Keep section-specific matching logic and only tighten a few known duplicate-name cases.
- Why not: That preserves drift between batter, SP, and RP and guarantees new mismatch classes will continue to appear in only one section at a time.

### 2) Disallow automatic acceptance of cross-player name matches

- Decision: If a fallback candidate produces a different numeric `matched_player_id` than the source roster row's numeric `source_player_id`, the row MUST NOT be accepted as a successful automatic match.
- Rationale: Same-name ambiguity is precisely the failure mode the user wants to eliminate. A mismatch should become reviewable evidence, not published stats.
- Alternative considered: Accept name matches when the displayed name string is identical.
- Why not: The current NYM bullpen mismatch shows that string equality is not a reliable identity guarantee.

### 3) Split internal build artifacts from public release artifacts

- Decision: Candidate builds, quality reports, review-state outputs, and QA reports will live in an internal artifact area outside the public static release tree, while `public/data/latest/` will contain only release files intended for browser consumption.
- Rationale: The current filesystem layout makes operator workflow metadata part of the public contract by default, even when the frontend does not render it.
- Alternative considered: Keep all files in `public/data/` and rely on the frontend not to read internal ones.
- Why not: That is a policy by convention, not a clean contract boundary, and it makes accidental exposure easy.

### 4) Publish a sanitized release snapshot derived from the reviewed candidate

- Decision: The pipeline will maintain richer internal candidate rows for matching evidence and QA, then derive sanitized public release files by removing warning summaries, review state, and other operator-only fields before promotion.
- Rationale: QA and review need evidence; the frontend does not. One internal representation plus one sanitized release representation keeps both needs explicit.
- Alternative considered: Remove internal evidence from the build completely.
- Why not: That would weaken operator review and make debugging future mismatches harder.

### 5) Keep release gating semantically unchanged but move it off the public surface

- Decision: Review-required, publish-eligible, and blocking-failure semantics remain part of the operator workflow, but those states will exist in internal artifacts and QA outputs rather than in the public release directory or public snapshot payloads.
- Rationale: This preserves operational safety without forcing the release workflow itself into the public data API.
- Alternative considered: Remove review metadata entirely after publish.
- Why not: Operators still need an auditable record of why a candidate was approved or blocked.

## Risks / Trade-offs

- [Some Fangraphs rows still may not resolve by source player ID] -> Mitigation: keep unresolved attribution and review paths, but treat them as explicit uncertainty instead of name-based silent repair.
- [Maintaining internal and public artifact shapes adds transformation logic] -> Mitigation: define one sanitized-release step with narrow, testable field-removal rules.
- [Moving candidate/review artifacts out of `public/` may require script and runbook updates] -> Mitigation: keep command semantics stable and update OpenSpec/tasks to include operator workflow docs.
- [Regression checks may currently depend on public artifact shape] -> Mitigation: pin regression and QA tooling to the internal reviewed candidate or to the sanitized release contract intentionally, rather than mixing both.

## Migration Plan

1. Define the target internal artifact boundary and the target public release boundary.
2. Refactor sync scripts toward a shared identity-first resolution policy and record explicit mismatch evidence when fallback candidates disagree with source identity.
3. Update the aggregate pipeline to consume internal candidate rows, run gating/review on internal artifacts, and emit sanitized public release files only after approval.
4. Update regression and QA scripts to read the correct internal or public artifact for their role.
5. Verify rollback still restores the last approved public release snapshot and does not require republishing operator artifacts.

Rollback remains release-based: if the refactor misbehaves, operators keep the last approved public release in `public/data/latest/` and can restore it from backup while internal candidate artifacts remain available for diagnosis.

## Open Questions

- Should internal artifacts move under a repo-local path such as `artifacts/` or `data/builds/`, or should they remain adjacent to public data under a non-served subtree?
- Should a source-vs-matched player ID disagreement always become `lookup_failed`, or should there be a distinct mismatch classification for operator triage?
- Which fields belong in the public `meta` object after sanitization, especially around freshness and approval timestamps?
