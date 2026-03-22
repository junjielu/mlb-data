#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_candidate_snapshot(artifact_base: Path) -> Path | None:
    candidates_dir = artifact_base / "candidates"
    if not candidates_dir.exists():
        return None
    candidates = sorted([p for p in candidates_dir.iterdir() if p.is_dir()])
    if not candidates:
        return None
    snapshot = candidates[-1] / "depth-charts.json"
    return snapshot if snapshot.exists() else None


def resolve_snapshot_path(snapshot: Path | None, artifact_base: Path, build_id: str | None) -> Path:
    if snapshot is not None:
        return snapshot
    if build_id:
        return artifact_base / "candidates" / build_id / "depth-charts.json"
    latest_candidate = latest_candidate_snapshot(artifact_base)
    if latest_candidate is not None:
        return latest_candidate
    return Path("public/data/latest/depth-charts.json")


def find_team(snapshot: dict, abbr: str) -> dict:
    for team in snapshot.get("teams", []):
        if team.get("abbr") == abbr:
            return team
    raise RuntimeError(f"Missing team: {abbr}")


def find_row(rows: list[dict], key: str, value: str) -> dict:
    for row in rows:
        if str(row.get(key, "")) == value:
            return row
    raise RuntimeError(f"Missing row where {key}={value}")


def batter_rows(team: dict, view: str = "vsR") -> list[dict]:
    batter = team.get("batter", {})
    if isinstance(batter, dict):
        return list(batter.get("lineups", {}).get(view, []))
    return list(batter or [])


def batter_alternates(team: dict, view: str = "vsR") -> list[dict]:
    batter = team.get("batter", {})
    if isinstance(batter, dict):
        return list(batter.get("alternates", {}).get(view, []))
    return []


def get_regression_failures(snapshot: dict) -> list[str]:
    nyy = find_team(snapshot, "NYY")
    tor = find_team(snapshot, "TOR")
    lad = find_team(snapshot, "LAD")
    ath = find_team(snapshot, "ATH")
    wsn = find_team(snapshot, "WSN")

    nyy_su7 = find_row(nyy.get("rp", []), "role", "SU7")
    tor_su7 = find_row(tor.get("rp", []), "role", "SU7")
    lad_b5 = find_row(batter_rows(lad), "order", "5")
    lad_b6 = find_row(batter_rows(lad), "order", "6")
    ath_b8 = find_row(batter_rows(ath), "order", "8")
    wsn_b4 = find_row(batter_rows(wsn), "order", "4")

    failures: list[str] = []

    for abbr in ("NYY", "TOR", "LAD", "ATH", "WSN"):
        team = find_team(snapshot, abbr)
        batter = team.get("batter", {})
        if not isinstance(batter, dict) or not isinstance(batter.get("alternates"), dict):
            failures.append(f"{abbr} batter alternates container is missing")
            continue
        for view in ("vsR", "vsL"):
            if view not in batter.get("alternates", {}):
                failures.append(f"{abbr} batter alternates.{view} is missing")

    for label, row, keys in [
        ("NYY SU7", nyy_su7, ["era", "k9", "bb9", "k_pct", "stuff_plus"]),
        ("TOR SU7", tor_su7, ["era", "k9", "bb9", "k_pct", "stuff_plus"]),
    ]:
        if any(not str(row.get(k, "")).strip() for k in keys):
            failures.append(f"{label} has missing RP metrics")

    if "Smith" not in str(lad_b5.get("name", "")):
        failures.append("LAD batter order 5 is not Will Smith")

    if str(lad_b6.get("matched_player_id", "")) != "13301":
        failures.append("LAD batter order 6 Max Muncy is not matched to playerid 13301")

    if "Muncy" not in str(ath_b8.get("name", "")):
        failures.append("ATH batter order 8 is not Muncy")

    if str(wsn_b4.get("matched_player_id", "")) != "20391":
        failures.append("WSN batter order 4 Luis García Jr. is not matched to playerid 20391")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Regression checks for known critical rows.")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--build-id")
    parser.add_argument("--artifact-base", type=Path, default=Path("data/builds/depth-charts"))
    args = parser.parse_args()

    snapshot_path = resolve_snapshot_path(args.snapshot, args.artifact_base, args.build_id)
    snapshot = load_snapshot(snapshot_path)

    nyy = find_team(snapshot, "NYY")
    tor = find_team(snapshot, "TOR")
    lad_b5 = find_row(batter_rows(find_team(snapshot, "LAD")), "order", "5")
    lad_b6 = find_row(batter_rows(find_team(snapshot, "LAD")), "order", "6")
    ath_b8 = find_row(batter_rows(find_team(snapshot, "ATH")), "order", "8")
    wsn_b4 = find_row(batter_rows(find_team(snapshot, "WSN")), "order", "4")
    lad_alt_vsr = batter_alternates(find_team(snapshot, "LAD"), "vsR")
    lad_alt_vsl = batter_alternates(find_team(snapshot, "LAD"), "vsL")
    nyy_su7 = find_row(nyy.get("rp", []), "role", "SU7")
    tor_su7 = find_row(tor.get("rp", []), "role", "SU7")
    failures = get_regression_failures(snapshot)

    if failures:
        print("Regression checks failed:")
        for f in failures:
            print(f"- {f}")
        return 1

    print("Regression checks passed:")
    print(f"- Snapshot: {snapshot_path}")
    print(f"- NYY SU7: {nyy_su7['name']} {nyy_su7['era']} {nyy_su7['k9']} {nyy_su7['bb9']} {nyy_su7['k_pct']} {nyy_su7['stuff_plus']}")
    print(f"- TOR SU7: {tor_su7['name']} {tor_su7['era']} {tor_su7['k9']} {tor_su7['bb9']} {tor_su7['k_pct']} {tor_su7['stuff_plus']}")
    print(f"- LAD batter #5: {lad_b5['name']}")
    print(f"- LAD batter #6: {lad_b6['name']} matched_player_id={lad_b6.get('matched_player_id')}")
    print(f"- LAD alternates vsR/vsL: {len(lad_alt_vsr)}/{len(lad_alt_vsl)}")
    print(f"- ATH batter #8: {ath_b8['name']}")
    print(f"- WSN batter #4: {wsn_b4['name']} matched_player_id={wsn_b4.get('matched_player_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
