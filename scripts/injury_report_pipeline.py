#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_source(payload: dict[str, Any]) -> None:
    teams = payload.get("teams")
    meta = payload.get("meta", {})
    if not isinstance(teams, list) or len(teams) != 30:
        raise RuntimeError(f"Expected 30 teams in injury source payload, got {0 if not isinstance(teams, list) else len(teams)}")

    if meta.get("timeframe") != "current":
        raise RuntimeError("Injury source payload must use timeframe=current")

    for team in teams:
        if not team.get("abbr"):
            raise RuntimeError("Injury source payload contains a team without abbr")
        if "available" not in team:
            raise RuntimeError(f"Injury source payload missing availability flag for {team.get('abbr')}")
        injuries = team.get("injuries")
        if not isinstance(injuries, list):
            raise RuntimeError(f"Injury source payload injuries must be a list for {team.get('abbr')}")


def build_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    validate_source(payload)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    meta = dict(payload.get("meta", {}))
    meta["generatedAt"] = generated_at
    meta["stateSemantics"] = {
        "emptyTeamRows": "A team with available=true and an empty injuries array has no current Fangraphs injury entries.",
        "unavailable": "If injuries.json cannot be loaded, the frontend SHALL treat current injury data as temporarily unavailable and keep the last published artifact.",
    }
    return {"meta": meta, "teams": payload["teams"]}


def publish_snapshot(snapshot: dict[str, Any], latest_path: Path, backup_dir: Path) -> None:
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = latest_path.parent / f".injuries_tmp_{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    tmp_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    if latest_path.exists():
        backup_path = backup_dir / f"injuries-pre-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
        shutil.copy2(latest_path, backup_path)

    tmp_path.replace(latest_path)


def refresh(source_path: Path, latest_path: Path, backup_dir: Path) -> None:
    snapshot = build_snapshot(load_json(source_path))
    publish_snapshot(snapshot, latest_path, backup_dir)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Publish standalone current Fangraphs injury data. Empty team arrays mean no current "
            "Fangraphs injury entries; missing injuries.json should be treated by the frontend as temporary unavailability."
        )
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    refresh_parser = sub.add_parser("refresh", help="Validate source injury data and publish latest injuries.json")
    refresh_parser.add_argument("--source", type=Path, default=Path("data/fangraphs_injuries_current.json"))
    refresh_parser.add_argument("--latest", type=Path, default=Path("public/data/latest/injuries.json"))
    refresh_parser.add_argument("--backup-dir", type=Path, default=Path("public/data/backups/injuries"))

    args = parser.parse_args()
    if args.cmd == "refresh":
        refresh(args.source, args.latest, args.backup_dir)
        print(f"Published injury snapshot: {args.latest}")
        return 0
    raise RuntimeError(f"Unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
