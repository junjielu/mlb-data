# Cutover Notes (Notion -> Web UI)

## Primary Consumer Surface
- Web UI under `public/` is now the standard consumer surface.
- Notion is no longer part of the default publication path.

## First Post-Cutover Run
- Build command:
  - `python3 scripts/depth_charts_pipeline.py build --season 2025 --publish`
- Result:
  - Candidate written to `public/data/candidates/20260320-121344/`
  - Published to `public/data/latest/`

## Monitoring Checklist (first run)
- `python3 scripts/regression_checks.py` passes
- `python3 scripts/qa_go_no_go.py` produces either:
  - `GO` for directly publishable builds
  - `REVIEW` for candidates awaiting operator approval
- If review is required:
  - Run `python3 scripts/depth_charts_pipeline.py review --build-id <build_id> --reviewer <name> --note "<summary>"`
  - Then publish with `python3 scripts/depth_charts_pipeline.py publish --build-id <build_id>`
- `/teams` and `/team/:abbr` load correctly in local server

## Rollback Plan
- Use backup snapshot in `public/data/backups/`
- Run:
  - `python3 scripts/depth_charts_pipeline.py rollback --backup-name <backup_dir_name>`
