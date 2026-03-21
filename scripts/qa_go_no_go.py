#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_candidate_paths(artifact_base: Path) -> tuple[Path, Path] | None:
    candidates_dir = artifact_base / "candidates"
    if not candidates_dir.exists():
        return None
    candidates = sorted([p for p in candidates_dir.iterdir() if p.is_dir()])
    if not candidates:
        return None
    candidate = candidates[-1]
    snapshot = candidate / "depth-charts.json"
    quality = candidate / "quality-report.json"
    if snapshot.exists() and quality.exists():
        return snapshot, quality
    return None


def resolve_artifact_paths(snapshot: Path | None, quality: Path | None, artifact_base: Path, build_id: str | None) -> tuple[Path, Path]:
    if snapshot is not None and quality is not None:
        return snapshot, quality
    if build_id:
        candidate = artifact_base / "candidates" / build_id
        return candidate / "depth-charts.json", candidate / "quality-report.json"
    latest_candidate = latest_candidate_paths(artifact_base)
    if latest_candidate is not None:
        return latest_candidate
    return Path("public/data/latest/depth-charts.json"), Path("public/data/latest/quality-report.json")


def check(snapshot: dict, quality: dict) -> tuple[str, list[str], list[str], list[dict]]:
    notes: list[str] = []
    blocking: list[str] = []
    review_queue = list(quality.get("reviewQueue", []))

    teams = snapshot.get("teams", [])
    if len(teams) != 30:
        notes.append(f"FAIL Gate0: expected 30 teams, got {len(teams)}")
        blocking.append(f"Expected 30 teams, got {len(teams)}")
    else:
        notes.append("PASS Gate0: 30 teams present")

    for team in teams:
        abbr = team.get("abbr")
        b = team.get("batter", [])
        sp = team.get("sp", [])
        rp = team.get("rp", [])
        if len(b) < 9 or len(sp) < 5 or len(rp) < 5:
            notes.append(f"FAIL Gate1: {abbr} counts batter={len(b)} sp={len(sp)} rp={len(rp)}")
            blocking.append(f"{abbr} counts batter={len(b)} sp={len(sp)} rp={len(rp)}")

    if not blocking:
        notes.append("PASS Gate1: structural minimums satisfied")

    explicit_blockers = list(quality.get("summary", {}).get("blockingFailures", []))
    if explicit_blockers:
        notes.append(f"FAIL Gate2: blockingFailures={len(explicit_blockers)}")
        blocking.extend(explicit_blockers)
    else:
        notes.append("PASS Gate2: no blocking attribution or regression failures")

    build_status = snapshot.get("meta", {}).get("buildStatus", "unknown")
    if build_status == "failed":
        notes.append("FAIL Gate3: buildStatus=failed")
        blocking.append("buildStatus=failed")
    elif build_status == "needs_review":
        notes.append("REVIEW Gate3: buildStatus=needs_review")
    else:
        notes.append(f"PASS Gate3: buildStatus={build_status}")

    review_required = bool(quality.get("meta", {}).get("reviewRequired", False)) and not bool(quality.get("meta", {}).get("reviewApproved", False))
    if review_required and review_queue:
        notes.append(f"REVIEW Gate4: {len(review_queue)} high-risk unknown rows require operator approval")
    elif review_required:
        notes.append("REVIEW Gate4: operator review required")
    else:
        notes.append("PASS Gate4: no pending operator review")

    if blocking:
        decision = "NO-GO"
    elif review_required:
        decision = "REVIEW"
    else:
        decision = "GO"
    return decision, notes, blocking, review_queue


def write_report(path: Path, decision: str, notes: list[str], blocking: list[str], review_queue: list[dict], snapshot: dict, quality: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# Go/No-Go QA Report",
        "",
        f"- Generated: {ts}",
        f"- Season: {snapshot.get('meta', {}).get('season')}",
        f"- Build ID: {snapshot.get('meta', {}).get('buildId')}",
        f"- Build Status: {snapshot.get('meta', {}).get('buildStatus')}",
        f"- Publish Eligible: {quality.get('meta', {}).get('publishEligible')}",
        f"- Decision: **{decision}**",
        "",
        "## Checks",
        "",
    ]
    for n in notes:
        lines.append(f"- {n}")
    if blocking:
        lines += ["", "## Blocking Failures", ""]
        for item in blocking:
            lines.append(f"- {item}")
    if review_queue:
        lines += ["", "## Pending Review Queue", ""]
        for item in review_queue:
            lines.append(
                f"- {item.get('team')} {item.get('section')} {item.get('slot')} {item.get('player')} "
                f"(risk={item.get('riskTier')}, sourcePlayerId={item.get('evidence', {}).get('sourcePlayerId', '')}, "
                f"matchMethod={item.get('evidence', {}).get('matchMethod', '')})"
            )
    lines += ["", "## Operator Notes", "", "- Record review outcome or publish decision here."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate go/no-go QA report from internal candidate artifacts or the current public release.")
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--quality", type=Path)
    parser.add_argument("--build-id")
    parser.add_argument("--artifact-base", type=Path, default=Path("data/builds/depth-charts"))
    parser.add_argument("--out", type=Path, default=Path("docs/qa/go-no-go.md"))
    args = parser.parse_args()

    snapshot_path, quality_path = resolve_artifact_paths(args.snapshot, args.quality, args.artifact_base, args.build_id)
    snapshot = load_json(snapshot_path)
    quality = load_json(quality_path)
    decision, notes, blocking, review_queue = check(snapshot, quality)
    write_report(args.out, decision, notes, blocking, review_queue, snapshot, quality)
    print(f"Wrote QA report: {args.out} (decision={decision}, snapshot={snapshot_path}, quality={quality_path})")
    return 0 if decision == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
