#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
import requests

try:
    import cloudscraper  # type: ignore
except Exception:
    cloudscraper = None

try:
    import browser_cookie3  # type: ignore
except Exception:
    browser_cookie3 = None

TEAM_SLUGS = {
    "ARI": "diamondbacks",
    "ATL": "braves",
    "BAL": "orioles",
    "BOS": "red-sox",
    "CHC": "cubs",
    "CHW": "white-sox",
    "CIN": "reds",
    "CLE": "guardians",
    "COL": "rockies",
    "DET": "tigers",
    "HOU": "astros",
    "KCR": "royals",
    "LAA": "angels",
    "LAD": "dodgers",
    "MIA": "marlins",
    "MIL": "brewers",
    "MIN": "twins",
    "NYM": "mets",
    "NYY": "yankees",
    "PHI": "phillies",
    "PIT": "pirates",
    "SDP": "padres",
    "SFG": "giants",
    "SEA": "mariners",
    "STL": "cardinals",
    "TBR": "rays",
    "TEX": "rangers",
    "TOR": "blue-jays",
    "WSN": "nationals",
    "ATH": "athletics",
}

TEAM_NAMES = {
    "ARI": "Arizona Diamondbacks",
    "ATL": "Atlanta Braves",
    "BAL": "Baltimore Orioles",
    "BOS": "Boston Red Sox",
    "CHC": "Chicago Cubs",
    "CHW": "Chicago White Sox",
    "CIN": "Cincinnati Reds",
    "CLE": "Cleveland Guardians",
    "COL": "Colorado Rockies",
    "DET": "Detroit Tigers",
    "HOU": "Houston Astros",
    "KCR": "Kansas City Royals",
    "LAA": "Los Angeles Angels",
    "LAD": "Los Angeles Dodgers",
    "MIA": "Miami Marlins",
    "MIL": "Milwaukee Brewers",
    "MIN": "Minnesota Twins",
    "NYM": "New York Mets",
    "NYY": "New York Yankees",
    "PHI": "Philadelphia Phillies",
    "PIT": "Pittsburgh Pirates",
    "SDP": "San Diego Padres",
    "SFG": "San Francisco Giants",
    "SEA": "Seattle Mariners",
    "STL": "St. Louis Cardinals",
    "TBR": "Tampa Bay Rays",
    "TEX": "Texas Rangers",
    "TOR": "Toronto Blue Jays",
    "WSN": "Washington Nationals",
    "ATH": "Athletics",
}

TABLE_HEADERS = [
    "Name",
    "Team",
    "Pos",
    "Injury / Surgery Date",
    "Injury / Surgery",
    "Status",
    "IL Retro Date",
    "Eligible to Return",
    "Return Date",
    "Latest Update",
]


def make_session(use_cloudscraper: bool = False) -> requests.Session:
    if use_cloudscraper and cloudscraper is not None:
        scraper = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "darwin", "mobile": False})
        scraper.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        return scraper

    session = requests.Session()
    session.trust_env = False
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    return session


def apply_cookie_header(session: requests.Session, cookie_header: str) -> None:
    for part in cookie_header.split(";"):
        item = part.strip()
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        session.cookies.set(key.strip(), value.strip(), domain=".fangraphs.com")


def apply_browser_cookies(session: requests.Session, browser: str) -> None:
    if browser_cookie3 is None:
        raise RuntimeError("browser-cookie3 is not installed; cannot load browser cookies")

    browser = browser.lower()
    loader_map = {
        "chrome": browser_cookie3.chrome,
        "chromium": browser_cookie3.chromium,
        "edge": browser_cookie3.edge,
        "firefox": browser_cookie3.firefox,
        "brave": browser_cookie3.brave,
    }
    if browser not in loader_map:
        raise RuntimeError(f'Unsupported browser "{browser}" for cookie import')

    jar = loader_map[browser](domain_name="fangraphs.com")
    for cookie in jar:
        if "fangraphs.com" in (cookie.domain or ""):
            session.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)


def fetch_html(session: requests.Session, url: str) -> str:
    resp = session.get(url, timeout=45)
    resp.raise_for_status()
    return resp.text


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_title_season(soup: BeautifulSoup) -> int | None:
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    match = re.search(r"\b(20\d{2})\b", title)
    return int(match.group(1)) if match else None


def parse_updated_text(soup: BeautifulSoup) -> str:
    text = normalize_space(soup.get_text(" ", strip=True))
    match = re.search(r"Updated:\s*(.+?)\s+Updated:\s*\d{1,2}/\d{1,2}/\d{4}", text)
    if match:
        return match.group(1).strip()
    match = re.search(r"Updated:\s*(.+)", text)
    return match.group(1).strip() if match else ""


def _header_row_texts(table: Any) -> list[str]:
    header_cells = table.select("thead th")
    if not header_cells:
        first_row = table.find("tr")
        if first_row:
            header_cells = first_row.find_all(["th", "td"])
    return [normalize_space(cell.get_text(" ", strip=True)) for cell in header_cells]


def find_injury_table(soup: BeautifulSoup) -> Any | None:
    for table in soup.find_all("table"):
        headers = _header_row_texts(table)
        if headers[: len(TABLE_HEADERS)] == TABLE_HEADERS:
            return table
    return None


def parse_injury_rows(table: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    tbody_rows = table.select("tbody tr")
    if not tbody_rows:
        tbody_rows = table.find_all("tr")[1:]

    for tr in tbody_rows:
        cells = tr.find_all("td")
        if len(cells) < len(TABLE_HEADERS):
            continue

        name_cell = cells[0]
        link = name_cell.find("a", href=True)
        href = normalize_space(link["href"]) if link else ""
        if href.startswith("/"):
            href = f"https://www.fangraphs.com{href}"

        values = [normalize_space(cell.get_text(" ", strip=True)) for cell in cells[: len(TABLE_HEADERS)]]
        rows.append(
            {
                "name": values[0],
                "url": href,
                "team": values[1],
                "position": values[2],
                "injury_date": values[3],
                "injury": values[4],
                "status": values[5],
                "il_retro_date": values[6],
                "eligible_to_return": values[7],
                "return_date": values[8],
                "latest_update": values[9],
            }
        )
    return rows


def fetch_team_injuries(session: requests.Session, abbr: str, slug: str) -> tuple[dict[str, Any], int | None, str]:
    url = f"https://www.fangraphs.com/roster-resource/injury-report/{slug}?groupby=team&timeframe=current"
    soup = BeautifulSoup(fetch_html(session, url), "html.parser")
    table = find_injury_table(soup)
    rows = parse_injury_rows(table) if table is not None else []
    season = parse_title_season(soup)
    source_updated_at = parse_updated_text(soup)
    return (
        {
            "abbr": abbr,
            "name": TEAM_NAMES[abbr],
            "sourceUrl": url,
            "available": True,
            "injuries": rows,
        },
        season,
        source_updated_at,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Fangraphs current injury reports by team.")
    parser.add_argument("--out", type=Path, default=Path("data/fangraphs_injuries_current.json"))
    parser.add_argument("--use-cloudscraper", action="store_true")
    parser.add_argument("--use-browser-cookies", action="store_true")
    parser.add_argument("--cookie-browser", default="chrome")
    parser.add_argument("--cookie-header", default="")
    args = parser.parse_args()

    session = make_session(use_cloudscraper=args.use_cloudscraper)
    if args.use_browser_cookies:
        apply_browser_cookies(session, args.cookie_browser)
    if args.cookie_header.strip():
        apply_cookie_header(session, args.cookie_header.strip())
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    teams: list[dict[str, Any]] = []
    source_season: int | None = None
    source_updated_at = ""
    for abbr, slug in TEAM_SLUGS.items():
        team_payload, team_season, team_updated = fetch_team_injuries(session, abbr, slug)
        teams.append(team_payload)
        if source_season is None and team_season is not None:
            source_season = team_season
        if not source_updated_at and team_updated:
            source_updated_at = team_updated

    payload = {
        "meta": {
            "schemaVersion": "1.0.0",
            "source": "fangraphs",
            "season": source_season,
            "timeframe": "current",
            "generatedAt": generated_at,
            "sourceUpdatedAt": source_updated_at,
            "teamCount": len(teams),
        },
        "teams": teams,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote injury source data: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
