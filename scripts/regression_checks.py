#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Regression checks for known critical rows.")
    parser.add_argument("--snapshot", type=Path, default=Path("public/data/latest/depth-charts.json"))
    args = parser.parse_args()

    snapshot = load_snapshot(args.snapshot)

    nyy = find_team(snapshot, "NYY")
    tor = find_team(snapshot, "TOR")
    lad = find_team(snapshot, "LAD")
    ath = find_team(snapshot, "ATH")

    nyy_su7 = find_row(nyy.get("rp", []), "role", "SU7")
    tor_su7 = find_row(tor.get("rp", []), "role", "SU7")
    lad_b5 = find_row(lad.get("batter", []), "order", "5")
    ath_b8 = find_row(ath.get("batter", []), "order", "8")

    failures: list[str] = []

    for label, row, keys in [
        ("NYY SU7", nyy_su7, ["era", "k9", "bb9", "k_pct", "stuff_plus"]),
        ("TOR SU7", tor_su7, ["era", "k9", "bb9", "k_pct", "stuff_plus"]),
    ]:
        if any(not str(row.get(k, "")).strip() for k in keys):
            failures.append(f"{label} has missing RP metrics")

    if "Smith" not in str(lad_b5.get("name", "")):
        failures.append("LAD batter order 5 is not Will Smith")

    if "Muncy" not in str(ath_b8.get("name", "")):
        failures.append("ATH batter order 8 is not Muncy")

    if failures:
        print("Regression checks failed:")
        for f in failures:
            print(f"- {f}")
        return 1

    print("Regression checks passed:")
    print(f"- NYY SU7: {nyy_su7['name']} {nyy_su7['era']} {nyy_su7['k9']} {nyy_su7['bb9']} {nyy_su7['k_pct']} {nyy_su7['stuff_plus']}")
    print(f"- TOR SU7: {tor_su7['name']} {tor_su7['era']} {tor_su7['k9']} {tor_su7['bb9']} {tor_su7['k_pct']} {tor_su7['stuff_plus']}")
    print(f"- LAD batter #5: {lad_b5['name']}")
    print(f"- ATH batter #8: {ath_b8['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
