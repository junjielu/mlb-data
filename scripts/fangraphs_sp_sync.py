#!/usr/bin/env python3
import argparse
import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TEAM_SLUGS = {
    'ARI': 'diamondbacks', 'ATL': 'braves', 'BAL': 'orioles', 'BOS': 'red-sox',
    'CHC': 'cubs', 'CHW': 'white-sox', 'CIN': 'reds', 'CLE': 'guardians',
    'COL': 'rockies', 'DET': 'tigers', 'HOU': 'astros', 'KCR': 'royals',
    'LAA': 'angels', 'LAD': 'dodgers', 'MIA': 'marlins', 'MIL': 'brewers',
    'MIN': 'twins', 'NYM': 'mets', 'NYY': 'yankees', 'PHI': 'phillies',
    'PIT': 'pirates', 'SDP': 'padres', 'SFG': 'giants', 'SEA': 'mariners',
    'STL': 'cardinals', 'TBR': 'rays', 'TEX': 'rangers', 'TOR': 'blue-jays',
    'WSN': 'nationals', 'ATH': 'athletics',
}

@dataclass
class SPRow:
    role: str
    name: str
    url: str
    k9: str
    bb9: str
    stuff_plus: str
    location_plus: str


def fmt_float(v: object, ndigits: int = 2) -> str:
    if v is None:
        return ''
    try:
        return f'{float(v):.{ndigits}f}'
    except (TypeError, ValueError):
        return ''


def fetch_pitching_map(session: requests.Session, season: int) -> dict[str, dict]:
    params = dict(
        age='', pos='all', stats='pit', lg='all', qual='0', season=str(season),
        season1=str(season), startdate=f'{season}-03-01', enddate=f'{season}-11-30',
        month='0', hand='', team='0', pageitems='3000', pagenum='1', ind='0',
        rost='0', players='', sortdir='default', sortstat='WAR', type='42'
    )
    url = 'https://www.fangraphs.com/api/leaders/major-league/data'
    rows = session.get(url, params=params, timeout=30).json().get('data', [])
    out = {}
    for r in rows:
        name = r.get('PlayerName')
        if not name:
            continue
        stuff = r.get('sp_stuff')
        location = r.get('sp_location')
        k9 = r.get('K/9')
        bb9 = r.get('BB/9')
        out[name] = {
            'stuff_plus': '' if stuff is None else str(int(round(float(stuff)))),
            'location_plus': '' if location is None else str(int(round(float(location)))),
            'k9': fmt_float(k9, 2),
            'bb9': fmt_float(bb9, 2),
            'playerid': r.get('playerid'),
        }
    return out


def normalize_name(name: str) -> str:
    s = unicodedata.normalize('NFKD', name)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def extract_rotation_rows(
    session: requests.Session,
    team_slug: str,
    pitch_map: dict[str, dict],
    pitch_by_id: dict[int, dict],
    pitch_by_name_norm: dict[str, dict],
) -> list[SPRow]:
    url = f'https://www.fangraphs.com/roster-resource/depth-charts/{team_slug}'
    html = session.get(url, timeout=30).text
    soup = BeautifulSoup(html, 'html.parser')

    link_map: dict[str, str] = {}
    id_map: dict[str, int] = {}
    for a in soup.select('a[href*="/players/"]'):
        name = a.get_text(strip=True)
        href = a.get('href', '').strip()
        if not name or '/players/' not in href:
            continue
        if href.startswith('/'):
            href = 'https://www.fangraphs.com' + href
        link_map.setdefault(name, href)
        m = re.search(r'/players/[^/]+/(\d+|sa\d+)/stats', href)
        if m:
            pid = m.group(1)
            if pid.isdigit():
                id_map.setdefault(name, int(pid))

    text = soup.get_text('\n')
    a = text.find('Projected Starting Rotation')
    b = text.find('Projected Bullpen')
    seg = text[a:b] if a != -1 and b != -1 else ''
    lines = [ln.strip() for ln in seg.split('\n') if ln.strip()]
    idx = [i for i in range(len(lines) - 1) if re.fullmatch(r'SP\d+', lines[i]) and lines[i + 1] == 'SP']

    rows: list[SPRow] = []
    seen: set[str] = set()
    for i in idx:
        role = lines[i]
        if role in seen:
            continue
        seen.add(role)

        j = next((k for k in idx if k > i), len(lines))
        row = lines[i:j]
        if len(row) < 4:
            continue

        name = row[3]
        info = pitch_map.get(name, {})
        if not info:
            pid = id_map.get(name)
            if pid is not None:
                info = pitch_by_id.get(pid, {})
        if not info:
            info = pitch_by_name_norm.get(normalize_name(name), {})
        row_obj = SPRow(
            role=role.lower(),
            name=name,
            url=link_map.get(name, f'https://www.fangraphs.com/players/{name.lower().replace(" ", "-")}/stats/pitching'),
            k9=info.get('k9', ''),
            bb9=info.get('bb9', ''),
            stuff_plus=info.get('stuff_plus', ''),
            location_plus=info.get('location_plus', ''),
        )
        rows.append(row_obj)

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description='Fetch Fangraphs projected SP1-SP5 + K/9, BB/9, Stuff+ for MLB teams.')
    parser.add_argument('--season', type=int, default=2025)
    parser.add_argument('--out', type=Path, default=Path('data/fangraphs_sp_2025.json'))
    args = parser.parse_args()

    s = requests.Session()
    s.get('https://www.fangraphs.com', timeout=30)

    pitch_map = fetch_pitching_map(s, args.season)
    pitch_by_id = {}
    pitch_by_name_norm = {}
    for name, info in pitch_map.items():
        pid = info.get('playerid')
        if isinstance(pid, int):
            pitch_by_id[pid] = info
        pitch_by_name_norm[normalize_name(name)] = info
    result: dict[str, list[dict]] = {}

    for abbr, slug in TEAM_SLUGS.items():
        result[abbr] = [
            asdict(r)
            for r in extract_rotation_rows(s, slug, pitch_map, pitch_by_id, pitch_by_name_norm)
        ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {args.out} for {len(result)} teams')


if __name__ == '__main__':
    main()
