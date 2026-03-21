#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from regression_checks import get_regression_failures

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
SP_KEYS = ["era", "whip", "k9", "bb9", "stuff_plus", "location_plus"]
RP_KEYS = ["era", "k9", "bb9", "k_pct", "stuff_plus"]


@dataclass
class GateResult:
    build_status: str
    pass_publish: bool
    critical_count: int
    review_required: bool


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


def _slot_value(section: str, row: dict[str, Any]) -> str:
    return str(row.get("order" if section == "batter" else "role", "")).strip()


def _row_key(section: str, row: dict[str, Any]) -> str:
    return f"{_slot_value(section, row) or '?'}|{row.get('name', '?')}"


def _risk_tier(section: str, row: dict[str, Any]) -> str:
    slot = _slot_value(section, row).upper()
    if section == "batter":
        if slot.isdigit():
            order = int(slot)
            if order <= 5:
                return "high"
            if order <= 7:
                return "medium"
        return "low"
    if section == "sp":
        if slot.startswith("SP") and slot[2:].isdigit():
            order = int(slot[2:])
            if order <= 3:
                return "high"
            if order <= 5:
                return "medium"
        return "low"
    if slot in {"CL", "SU8", "SU7"}:
        return "high"
    if slot == "MID":
        return "medium"
    return "low"


def _is_scout_id(source_player_id: str) -> bool:
    return source_player_id.lower().startswith("sa")


def _classify_missing(row: dict[str, Any], section: str) -> tuple[str, str, dict[str, Any]]:
    source_player_id = str(row.get("source_player_id", "")).strip()
    match_method = str(row.get("match_method", "unmatched")).strip() or "unmatched"
    evidence = {
        "matchMethod": match_method,
        "sourcePlayerId": source_player_id,
        "matchedPlayerId": str(row.get("matched_player_id", "")).strip(),
        "sourceIdFoundInStats": bool(row.get("source_id_found_in_stats", False)),
        "exactNameFoundInStats": bool(row.get("exact_name_found_in_stats", False)),
        "normalizedNameFoundInStats": bool(row.get("normalized_name_found_in_stats", False)),
        "looseNameFoundInStats": bool(row.get("loose_name_found_in_stats", False)),
    }
    risk_tier = _risk_tier(section, row)

    if match_method != "unmatched":
        return "source_missing", risk_tier, evidence
    if evidence["sourceIdFoundInStats"] or evidence["exactNameFoundInStats"] or evidence["normalizedNameFoundInStats"] or evidence["looseNameFoundInStats"]:
        return "lookup_failed", risk_tier, evidence
    if _is_scout_id(source_player_id):
        return "source_missing", risk_tier, evidence
    return "unknown", risk_tier, evidence


def _review_item(team: dict[str, Any], section: str, row: dict[str, Any], evidence: dict[str, Any], risk_tier: str) -> dict[str, Any]:
    return {
        "team": team["abbr"],
        "section": section,
        "slot": _slot_value(section, row),
        "player": row.get("name", ""),
        "riskTier": risk_tier,
        "evidence": evidence,
    }


def evaluate_quality(teams: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any], GateResult]:
    total_warnings = 0
    total_critical = 0
    total_source_missing = 0
    total_lookup_failed = 0
    total_unknown = 0
    team_warning_counts: dict[str, int] = {}
    review_queue: list[dict[str, Any]] = []
    blocking_failures: list[str] = []

    for team in teams:
        warnings: list[dict[str, Any]] = []

        batter = team["batter"]
        sp = team["sp"]
        rp = team["rp"]

        if len(batter) < 9:
            msg = f"Batter rows {len(batter)} < 9"
            warnings.append(warn("section_too_short", "critical", "batter", msg))
            blocking_failures.append(f"{team['abbr']} batter section too short")
        if len(sp) < 5:
            msg = f"SP rows {len(sp)} < 5"
            warnings.append(warn("section_too_short", "critical", "sp", msg))
            blocking_failures.append(f"{team['abbr']} SP section too short")
        if len(rp) < 5:
            msg = f"RP rows {len(rp)} < 5"
            warnings.append(warn("section_too_short", "critical", "rp", msg))
            blocking_failures.append(f"{team['abbr']} RP section too short")

        section_order = [k for k in team.keys() if k in {"batter", "sp", "rp"}]
        if section_order != ["batter", "sp", "rp"]:
            msg = "Section order must be Batter -> SP -> RP"
            warnings.append(warn("section_order_invalid", "critical", "all", msg))
            blocking_failures.append(f"{team['abbr']} section order invalid")

        for section_name, rows, keys in [
            ("batter", batter, B_KEYS),
            ("sp", sp, SP_KEYS),
            ("rp", rp, RP_KEYS),
        ]:
            for row in rows:
                row_key = _row_key(section_name, row)
                if _all_empty(row, keys):
                    classification, risk_tier, evidence = _classify_missing(row, section_name)
                    row["missingDataClassification"] = classification
                    row["missingRiskTier"] = risk_tier
                    row["reviewRequired"] = classification == "unknown" and risk_tier == "high"
                    severity = "critical" if classification == "lookup_failed" else "warning"
                    message = {
                        "source_missing": "Metrics are absent in Fangraphs source data for this row",
                        "lookup_failed": "Metrics should have resolved but lookup evidence indicates a script-side failure",
                        "unknown": "Metrics remain unresolved and require attribution review",
                    }[classification]
                    warning_entry = warn(f"row_{classification}", severity, section_name, message, row_key)
                    warning_entry["classification"] = classification
                    warning_entry["riskTier"] = risk_tier
                    warning_entry["evidence"] = evidence
                    warnings.append(warning_entry)

                    if classification == "source_missing":
                        total_source_missing += 1
                    elif classification == "lookup_failed":
                        total_lookup_failed += 1
                        blocking_failures.append(f"{team['abbr']} {section_name} {_slot_value(section_name, row)} {row.get('name', '')}: lookup_failed")
                    else:
                        total_unknown += 1
                        if risk_tier == "high":
                            review_queue.append(_review_item(team, section_name, row, evidence, risk_tier))
                elif _partial_empty(row, keys):
                    warnings.append(warn("row_partial_missing", "info", section_name, "Some metrics are missing", row_key))

        team["warnings"] = warnings
        wc = len([w for w in warnings if w["severity"] in {"warning", "critical"}])
        cc = len([w for w in warnings if w["severity"] == "critical"])
        team["warningCount"] = wc
        team["status"] = "critical" if cc > 0 else ("warn" if wc > 0 else "ok")

        total_warnings += wc
        total_critical += cc
        team_warning_counts[team["abbr"]] = wc

    if len(teams) != 30:
        blocking_failures.append(f"Expected 30 teams, got {len(teams)}")

    review_required = bool(review_queue)
    has_blocking_failure = bool(blocking_failures) or total_critical > 0

    if has_blocking_failure:
        build_status = "failed"
        pass_publish = False
    elif review_required:
        build_status = "needs_review"
        pass_publish = False
    else:
        build_status = "success"
        pass_publish = True

    quality = {
        "summary": {
            "totalTeams": len(teams),
            "totalWarnings": total_warnings,
            "totalCritical": total_critical,
            "totalSourceMissing": total_source_missing,
            "totalLookupFailed": total_lookup_failed,
            "totalUnknown": total_unknown,
            "reviewRequiredCount": len(review_queue),
            "blockingFailures": blocking_failures,
        },
        "teams": team_warning_counts,
        "reviewQueue": review_queue,
    }

    return teams, quality, GateResult(build_status=build_status, pass_publish=pass_publish, critical_count=total_critical, review_required=review_required)


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
            "reviewRequired": gate.review_required,
            "reviewApproved": False,
            "source": "fangraphs",
        },
        "teams": teams,
    }

    regression_failures = get_regression_failures(snapshot)
    if regression_failures:
        gate.build_status = "failed"
        gate.pass_publish = False
        gate.critical_count += len(regression_failures)
        quality["summary"]["totalCritical"] += len(regression_failures)
        quality["summary"]["blockingFailures"].extend(regression_failures)
        quality["summary"]["regressionFailures"] = regression_failures
        snapshot["meta"]["buildStatus"] = gate.build_status
    else:
        quality["summary"]["regressionFailures"] = []

    quality_report = {
        "meta": {
            "schemaVersion": SCHEMA_VERSION,
            "season": season,
            "generatedAt": generated_at,
            "buildId": build_id,
            "buildStatus": gate.build_status,
            "publishEligible": gate.pass_publish,
            "reviewRequired": gate.review_required,
            "reviewApproved": False,
        },
        **quality,
    }
    return snapshot, quality_report, build_id


def _review_status(snapshot: dict[str, Any], quality: dict[str, Any]) -> dict[str, Any]:
    return {
        "buildId": snapshot["meta"]["buildId"],
        "required": bool(quality["meta"].get("reviewRequired", False)),
        "approved": False,
        "approvedAt": "",
        "reviewer": "",
        "note": "",
    }


def write_candidate(base: Path, build_id: str, snapshot: dict[str, Any], quality: dict[str, Any]) -> Path:
    out = base / "candidates" / build_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "depth-charts.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "quality-report.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "review-status.json").write_text(json.dumps(_review_status(snapshot, quality), ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def _load_candidate(candidate: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    snapshot = json.loads((candidate / "depth-charts.json").read_text(encoding="utf-8"))
    quality = json.loads((candidate / "quality-report.json").read_text(encoding="utf-8"))
    review_path = candidate / "review-status.json"
    if review_path.exists():
        review = json.loads(review_path.read_text(encoding="utf-8"))
    else:
        review = _review_status(snapshot, quality)
    return snapshot, quality, review


def _write_candidate_state(candidate: Path, snapshot: dict[str, Any], quality: dict[str, Any], review: dict[str, Any]) -> None:
    (candidate / "depth-charts.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    (candidate / "quality-report.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    (candidate / "review-status.json").write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")


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
    _snapshot, quality, review = _load_candidate(candidate)
    if args.require_gate and not quality.get("meta", {}).get("publishEligible", False):
        if quality.get("meta", {}).get("reviewRequired") and not review.get("approved", False):
            raise RuntimeError("Candidate requires operator review before publish. Run the review subcommand first or use --no-require-gate to force.")
        raise RuntimeError("Gate check failed for candidate. Use --no-require-gate to force.")
    latest = atomic_publish(candidate, args.data_base)
    print(f"Published latest snapshot: {latest}")
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    candidate = args.data_base / "candidates" / args.build_id
    if not candidate.exists():
        raise RuntimeError(f"Candidate build not found: {candidate}")
    snapshot, quality, review = _load_candidate(candidate)
    if quality.get("summary", {}).get("blockingFailures"):
        raise RuntimeError("Cannot approve review while blocking failures remain.")

    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    review.update(
        {
            "required": bool(quality.get("meta", {}).get("reviewRequired", False)),
            "approved": True,
            "approvedAt": ts,
            "reviewer": args.reviewer,
            "note": args.note,
        }
    )
    snapshot["meta"]["buildStatus"] = "success"
    snapshot["meta"]["reviewApproved"] = True
    snapshot["meta"]["approvedAt"] = ts
    quality["meta"]["buildStatus"] = "success"
    quality["meta"]["reviewApproved"] = True
    quality["meta"]["publishEligible"] = True
    _write_candidate_state(candidate, snapshot, quality, review)
    print(f"Approved candidate review: {candidate}")
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    rollback_latest(args.data_base, args.backup_name)
    print(f"Rolled back latest using backup: {args.backup_name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Depth charts snapshot pipeline (build/review/publish/rollback).")
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

    review = sub.add_parser("review", help="Approve a review-required candidate before publish")
    review.add_argument("--build-id", required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--note", default="")
    review.add_argument("--data-base", type=Path, default=Path("public/data"))
    review.set_defaults(func=cmd_review)

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
