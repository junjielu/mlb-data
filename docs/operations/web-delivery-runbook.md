# Web Delivery Runbook

## Build + Publish

```bash
python3 scripts/depth_charts_pipeline.py build --season 2025 --publish
```

Behavior:
- Writes candidate artifacts to `public/data/candidates/<build_id>/`
- Publishes to `public/data/latest/` only when gate is eligible

## Manual Publish Existing Candidate

```bash
python3 scripts/depth_charts_pipeline.py publish --build-id <build_id>
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
python3 scripts/qa_go_no_go.py
```

- QA report output: `docs/qa/go-no-go.md`

## Local Web Verification

```bash
python3 scripts/serve_web.py --host 127.0.0.1 --port 4173
```

Open:
- `http://127.0.0.1:4173/teams`
- `http://127.0.0.1:4173/team/NYY`
- `http://127.0.0.1:4173/about-data`
