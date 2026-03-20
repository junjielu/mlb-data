#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"

TEAM_META = {
    "ARI": {"name": "Arizona Diamondbacks", "division": "NL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/ari.png"},
    "ATL": {"name": "Atlanta Braves", "division": "NL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/atl.png"},
    "BAL": {"name": "Baltimore Orioles", "division": "AL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/bal.png"},
    "BOS": {"name": "Boston Red Sox", "division": "AL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/bos.png"},
    "CHC": {"name": "Chicago Cubs", "division": "NL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/chc.png"},
    "CHW": {"name": "Chicago White Sox", "division": "AL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/chw.png"},
    "CIN": {"name": "Cincinnati Reds", "division": "NL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/cin.png"},
    "CLE": {"name": "Cleveland Guardians", "division": "AL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/cle.png"},
    "COL": {"name": "Colorado Rockies", "division": "NL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/col.png"},
    "DET": {"name": "Detroit Tigers", "division": "AL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/det.png"},
    "HOU": {"name": "Houston Astros", "division": "AL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/hou.png"},
    "KCR": {"name": "Kansas City Royals", "division": "AL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/kc.png"},
    "LAA": {"name": "Los Angeles Angels", "division": "AL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/laa.png"},
    "LAD": {"name": "Los Angeles Dodgers", "division": "NL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/lad.png"},
    "MIA": {"name": "Miami Marlins", "division": "NL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/mia.png"},
    "MIL": {"name": "Milwaukee Brewers", "division": "NL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/mil.png"},
    "MIN": {"name": "Minnesota Twins", "division": "AL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/min.png"},
    "NYM": {"name": "New York Mets", "division": "NL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/nym.png"},
    "NYY": {"name": "New York Yankees", "division": "AL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/nyy.png"},
    "PHI": {"name": "Philadelphia Phillies", "division": "NL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/phi.png"},
    "PIT": {"name": "Pittsburgh Pirates", "division": "NL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/pit.png"},
    "SDP": {"name": "San Diego Padres", "division": "NL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/sd.png"},
    "SFG": {"name": "San Francisco Giants", "division": "NL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/sf.png"},
    "SEA": {"name": "Seattle Mariners", "division": "AL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/sea.png"},
    "STL": {"name": "St. Louis Cardinals", "division": "NL Central", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/stl.png"},
    "TBR": {"name": "Tampa Bay Rays", "division": "AL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/tb.png"},
    "TEX": {"name": "Texas Rangers", "division": "AL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/tex.png"},
    "TOR": {"name": "Toronto Blue Jays", "division": "AL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/tor.png"},
    "WSN": {"name": "Washington Nationals", "division": "NL East", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/wsh.png"},
    "ATH": {"name": "Athletics", "division": "AL West", "logo_url": "https://a.espncdn.com/i/teamlogos/mlb/500/oak.png"},
}

B_KEYS = ["wrc_plus", "avg", "obp", "slg"]
SP_KEYS = ["k9", "bb9", "stuff_plus", "location_plus"]
RP_KEYS = ["era", "k9", "bb9", "k_pct", "stuff_plus"]


@dataclass
class GateResult:
    build_status: str
    pass_publish: bool
    critical_count: int


def load_json(path: Path) -> dict[str, list[dict[str, Any]]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError(f"Expected dict JSON at {path}")
    return obj


def _all_empty(row: dict[str, Any], keys: list[str]) -> bool:
    for k in keys:
        v = str(row.get(k, "")).strip()
        if v:
            return False
    return True


def _partial_empty(row: dict[str, Any], keys: list[str]) -> bool:
    vals = [str(row.get(k, "")).strip() for k in keys]
    return any(not v for v in vals) and any(v for v in vals)


def warn(code: str, severity: str, section: str, message: str, row_key: str | None = None) -> dict[str, Any]:
    out = {
        "code": code,
        "severity": severity,
        "scope": "row" if row_key else "section",
        "section": section,
        "message": message,
    }
    if row_key:
        out["rowKey"] = row_key
    return out


def evaluate_quality(teams: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any], GateResult]:
    total_warnings = 0
    total_critical = 0
    total_row_all_missing = 0
    team_warning_counts: dict[str, int] = {}

    for team in teams:
        warnings: list[dict[str, Any]] = []

        batter = team["batter"]
        sp = team["sp"]
        rp = team["rp"]

        if len(batter) < 9:
            warnings.append(warn("section_too_short", "critical", "batter", f"Batter rows {len(batter)} < 9"))
        if len(sp) < 5:
            warnings.append(warn("section_too_short", "critical", "sp", f"SP rows {len(sp)} < 5"))
        if len(rp) < 5:
            warnings.append(warn("section_too_short", "critical", "rp", f"RP rows {len(rp)} < 5"))

        section_order = [k for k in team.keys() if k in {"batter", "sp", "rp"}]
        if section_order != ["batter", "sp", "rp"]:
            warnings.append(warn("section_order_invalid", "critical", "all", "Section order must be Batter -> SP -> RP"))

        for row in batter:
            row_key = f"{row.get('order','?')}|{row.get('name','?')}"
            if _all_empty(row, B_KEYS):
                warnings.append(warn("row_all_missing", "warning", "batter", "All batter metrics are empty", row_key))
                total_row_all_missing += 1
            elif _partial_empty(row, B_KEYS):
                warnings.append(warn("row_partial_missing", "info", "batter", "Some batter metrics are missing", row_key))

        for row in sp:
            row_key = f"{row.get('role','?')}|{row.get('name','?')}"
            if _all_empty(row, SP_KEYS):
                warnings.append(warn("row_all_missing", "warning", "sp", "All SP metrics are empty", row_key))
                total_row_all_missing += 1
            elif _partial_empty(row, SP_KEYS):
                warnings.append(warn("row_partial_missing", "info", "sp", "Some SP metrics are missing", row_key))

        for row in rp:
            row_key = f"{row.get('role','?')}|{row.get('name','?')}"
            if _all_empty(row, RP_KEYS):
                warnings.append(warn("row_all_missing", "warning", "rp", "All RP metrics are empty", row_key))
                total_row_all_missing += 1
            elif _partial_empty(row, RP_KEYS):
                warnings.append(warn("row_partial_missing", "info", "rp", "Some RP metrics are missing", row_key))

        team["warnings"] = warnings
        wc = len([w for w in warnings if w["severity"] in {"warning", "critical"}])
        cc = len([w for w in warnings if w["severity"] == "critical"])
        team["warningCount"] = wc
        team["status"] = "critical" if cc > 0 else ("warn" if wc > 0 else "ok")

        total_warnings += wc
        total_critical += cc
        team_warning_counts[team["abbr"]] = wc

    structural_failure = len(teams) != 30 or total_critical > 0

    # Threshold-based non-critical gate.
    # Start with permissive thresholds because prospects/injured players can legitimately have no season sample.
    per_team_over = [t["abbr"] for t in teams if len([w for w in t["warnings"] if w["code"] == "row_all_missing"]) > 5]
    too_many_missing = total_row_all_missing > 60 or bool(per_team_over)

    if structural_failure:
        build_status = "failed"
        pass_publish = False
    elif too_many_missing:
        build_status = "partial_success"
        pass_publish = False
    else:
        build_status = "success"
        pass_publish = True

    quality = {
        "summary": {
            "totalTeams": len(teams),
            "totalWarnings": total_warnings,
            "totalCritical": total_critical,
            "totalRowAllMissing": total_row_all_missing,
            "teamsOverRowAllMissingThreshold": per_team_over,
        },
        "teams": team_warning_counts,
    }

    return teams, quality, GateResult(build_status=build_status, pass_publish=pass_publish, critical_count=total_critical)


def build_snapshot(season: int, batter_path: Path, sp_path: Path, rp_path: Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    batter = load_json(batter_path)
    sp = load_json(sp_path)
    rp = load_json(rp_path)

    build_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    teams: list[dict[str, Any]] = []
    for abbr in TEAM_META:
        teams.append(
            {
                "abbr": abbr,
                "name": TEAM_META[abbr]["name"],
                "division": TEAM_META[abbr]["division"],
                "logoUrl": TEAM_META[abbr]["logo_url"],
                "lastUpdated": generated_at,
                "batter": batter.get(abbr, []),
                "sp": sp.get(abbr, []),
                "rp": rp.get(abbr, []),
            }
        )

    teams, quality, gate = evaluate_quality(teams)

    snapshot = {
        "meta": {
            "schemaVersion": SCHEMA_VERSION,
            "season": season,
            "generatedAt": generated_at,
            "buildId": build_id,
            "buildStatus": gate.build_status,
            "source": "fangraphs",
        },
        "teams": teams,
    }

    quality_report = {
        "meta": {
            "schemaVersion": SCHEMA_VERSION,
            "season": season,
            "generatedAt": generated_at,
            "buildId": build_id,
            "buildStatus": gate.build_status,
            "publishEligible": gate.pass_publish,
        },
        **quality,
    }
    return snapshot, quality_report, build_id


def write_candidate(base: Path, build_id: str, snapshot: dict[str, Any], quality: dict[str, Any]) -> Path:
    out = base / "candidates" / build_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "depth-charts.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "quality-report.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def atomic_publish(candidate_dir: Path, base: Path) -> Path:
    latest = base / "latest"
    backups = base / "backups"
    backups.mkdir(parents=True, exist_ok=True)

    build_id = candidate_dir.name
    tmp = base / f".latest_tmp_{build_id}"
    old = base / f".latest_old_{build_id}"

    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(candidate_dir, tmp)

    if latest.exists():
        backup_dir = backups / f"pre-{build_id}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        shutil.copytree(latest, backup_dir)
        if old.exists():
            shutil.rmtree(old)
        latest.rename(old)
    else:
        backup_dir = backups / f"pre-{build_id}-none"
        backup_dir.mkdir(exist_ok=True)

    try:
        tmp.rename(latest)
        if old.exists():
            shutil.rmtree(old)
    except Exception:
        if latest.exists():
            shutil.rmtree(latest)
        if old.exists():
            old.rename(latest)
        raise

    return latest


def rollback_latest(base: Path, backup_name: str) -> None:
    latest = base / "latest"
    backup = base / "backups" / backup_name
    if not backup.exists():
        raise RuntimeError(f"Backup not found: {backup}")

    restore_tmp = base / f".latest_restore_{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    if restore_tmp.exists():
        shutil.rmtree(restore_tmp)
    shutil.copytree(backup, restore_tmp)

    if latest.exists():
        latest_backup = base / "backups" / f"rollback-from-latest-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        shutil.copytree(latest, latest_backup)
        shutil.rmtree(latest)

    restore_tmp.rename(latest)


def cmd_build(args: argparse.Namespace) -> int:
    snapshot, quality, build_id = build_snapshot(
        season=args.season,
        batter_path=args.batter,
        sp_path=args.sp,
        rp_path=args.rp,
    )
    data_base = args.data_base
    candidate = write_candidate(data_base, build_id, snapshot, quality)
    print(f"Wrote candidate snapshot: {candidate}")

    if args.publish:
        if not quality["meta"]["publishEligible"]:
            print("Publish skipped: gate failed (publishEligible=false)")
            return 2
        latest = atomic_publish(candidate, data_base)
        print(f"Published latest snapshot: {latest}")

    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    candidate = args.data_base / "candidates" / args.build_id
    if not candidate.exists():
        raise RuntimeError(f"Candidate build not found: {candidate}")
    quality = json.loads((candidate / "quality-report.json").read_text(encoding="utf-8"))
    if args.require_gate and not quality.get("meta", {}).get("publishEligible", False):
        raise RuntimeError("Gate check failed for candidate. Use --no-require-gate to force.")
    latest = atomic_publish(candidate, args.data_base)
    print(f"Published latest snapshot: {latest}")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    rollback_latest(args.data_base, args.backup_name)
    print(f"Rolled back latest using backup: {args.backup_name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Depth charts snapshot pipeline (build/publish/rollback).")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Build candidate snapshot and quality report")
    b.add_argument("--season", type=int, default=2025)
    b.add_argument("--batter", type=Path, default=Path("data/fangraphs_batter_2025.json"))
    b.add_argument("--sp", type=Path, default=Path("data/fangraphs_sp_2025.json"))
    b.add_argument("--rp", type=Path, default=Path("data/fangraphs_rp_2025.json"))
    b.add_argument("--data-base", type=Path, default=Path("public/data"))
    b.add_argument("--publish", action="store_true")
    b.set_defaults(func=cmd_build)

    pub = sub.add_parser("publish", help="Publish an existing candidate build to latest")
    pub.add_argument("--build-id", required=True)
    pub.add_argument("--data-base", type=Path, default=Path("public/data"))
    pub.add_argument("--require-gate", action=argparse.BooleanOptionalAction, default=True)
    pub.set_defaults(func=cmd_publish)

    rb = sub.add_parser("rollback", help="Rollback latest to a backup directory name")
    rb.add_argument("--backup-name", required=True)
    rb.add_argument("--data-base", type=Path, default=Path("public/data"))
    rb.set_defaults(func=cmd_rollback)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
