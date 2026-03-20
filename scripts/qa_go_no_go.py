#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(snapshot: dict, quality: dict) -> tuple[str, list[str]]:
    notes: list[str] = []
    go = True

    teams = snapshot.get("teams", [])
    if len(teams) != 30:
        notes.append(f"FAIL Gate0: expected 30 teams, got {len(teams)}")
        go = False
    else:
        notes.append("PASS Gate0: 30 teams present")

    for team in teams:
        abbr = team.get("abbr")
        b = team.get("batter", [])
        sp = team.get("sp", [])
        rp = team.get("rp", [])
        if len(b) < 9 or len(sp) < 5 or len(rp) < 5:
            notes.append(f"FAIL Gate1: {abbr} counts batter={len(b)} sp={len(sp)} rp={len(rp)}")
            go = False

    if go:
        notes.append("PASS Gate1: structural minimums satisfied")

    critical = int(quality.get("summary", {}).get("totalCritical", 0))
    if critical > 0:
        notes.append(f"FAIL Gate2: totalCritical={critical}")
        go = False
    else:
        notes.append("PASS Gate2: no critical warnings")

    build_status = snapshot.get("meta", {}).get("buildStatus", "unknown")
    if build_status == "failed":
        notes.append("FAIL Gate3: buildStatus=failed")
        go = False
    else:
        notes.append(f"PASS Gate3: buildStatus={build_status}")

    decision = "GO" if go else "NO-GO"
    return decision, notes


def write_report(path: Path, decision: str, notes: list[str], snapshot: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# Go/No-Go QA Report",
        "",
        f"- Generated: {ts}",
        f"- Season: {snapshot.get('meta', {}).get('season')}",
        f"- Build ID: {snapshot.get('meta', {}).get('buildId')}",
        f"- Build Status: {snapshot.get('meta', {}).get('buildStatus')}",
        f"- Decision: **{decision}**",
        "",
        "## Checks",
        "",
    ]
    for n in notes:
        lines.append(f"- {n}")
    lines += ["", "## Operator Notes", "", "- Fill in manual UI checks here if needed."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate go/no-go QA report from latest snapshot artifacts.")
    parser.add_argument("--snapshot", type=Path, default=Path("public/data/latest/depth-charts.json"))
    parser.add_argument("--quality", type=Path, default=Path("public/data/latest/quality-report.json"))
    parser.add_argument("--out", type=Path, default=Path("docs/qa/go-no-go.md"))
    args = parser.parse_args()

    snapshot = load_json(args.snapshot)
    quality = load_json(args.quality)
    decision, notes = check(snapshot, quality)
    write_report(args.out, decision, notes, snapshot)
    print(f"Wrote QA report: {args.out} (decision={decision})")
    return 0 if decision == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
