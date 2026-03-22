# Web Delivery Runbook

## Build + Publish

```bash
python3 scripts/depth_charts_pipeline.py build --season 2025 --publish
```

Behavior:
- Writes candidate artifacts to `data/builds/depth-charts/candidates/<build_id>/`
- Publishes sanitized release files to `public/data/latest/` only when gate is eligible
- If high-risk `unknown` rows are present, the build stops at candidate creation with `buildStatus=needs_review`

## Manual Publish Existing Candidate

```bash
python3 scripts/depth_charts_pipeline.py publish --build-id <build_id>
```

Approve a review-required candidate before publish:

```bash
python3 scripts/depth_charts_pipeline.py review --build-id <build_id> --reviewer <name> --note "manual review summary"
```

Force publish (ignore gate):

```bash
python3 scripts/depth_charts_pipeline.py publish --build-id <build_id> --no-require-gate
```

## Rollback

List backups:

```bash
ls -1 public/data/backups
```

Rollback latest:

```bash
python3 scripts/depth_charts_pipeline.py rollback --backup-name <backup_dir_name>
```

## Regression + QA

```bash
python3 scripts/regression_checks.py
python3 scripts/qa_go_no_go.py --build-id <build_id>
```

- QA report output: `docs/qa/go-no-go.md`
- Candidate QA inputs come from `data/builds/depth-charts/candidates/<build_id>/`
- `qa_go_no_go.py` now returns:
  - `GO` when publish can proceed
  - `REVIEW` when high-risk unknown rows require operator approval
  - `NO-GO` when blocking failures are present

## Local Web Verification

```bash
python3 scripts/serve_web.py --host 127.0.0.1 --port 4173
```

Open:
- `http://127.0.0.1:4173/teams`
- `http://127.0.0.1:4173/team/NYY`
- `http://127.0.0.1:4173/about-data`

Production UI expectation:
- The public site shows approved depth chart results and freshness metadata
- Published `depth-charts.json` rows expose consumer-facing `playerId` and inline `history` entries for 2024 and 2023
- Published SP and RP rows use the same metric contract: `ERA`, `WHIP`, `K/9`, `BB/9`, `Stuff+`, `Location+`, `vFA`, `BABIP`
- `/team/:abbr` renders 2025 primary rows by default and can expand inline recent history beneath a player row
- Internal warning counts, publish review state, and operator diagnostics stay in internal artifacts and QA outputs
