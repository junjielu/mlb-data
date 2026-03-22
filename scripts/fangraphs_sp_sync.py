#!/usr/bin/env python3
import argparse
import json
import re
import time
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

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
    age: str
    url: str
    era: str
    whip: str
    k9: str
    bb9: str
    stuff_plus: str
    location_plus: str
    vfa: str
    babip: str
    match_method: str = 'unmatched'
    source_player_id: str = ''
    matched_player_id: str = ''
    source_id_found_in_stats: bool = False
    exact_name_found_in_stats: bool = False
    normalized_name_found_in_stats: bool = False
    identity_mismatch_found: bool = False
    mismatch_candidate_player_id: str = ''


def http_get(session: requests.Session, url: str, *, params: dict[str, str] | None = None, timeout: int = 45) -> requests.Response:
    last_err: Exception | None = None
    last_status: int | None = None
    for i in range(5):
        try:
            r = session.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                return r
            last_status = r.status_code
            if r.status_code in {403, 429, 500, 502, 503, 504}:
                time.sleep(1.2 * (i + 1))
                continue
            return r
        except requests.RequestException as e:
            last_err = e
            time.sleep(1.2 * (i + 1))

    if last_err is not None:
        raise RuntimeError(f'HTTP request failed after retries for {url}: {last_err}') from last_err
    raise RuntimeError(f'HTTP request failed after retries for {url}: status={last_status}')


def fmt_float(v: object, ndigits: int = 2) -> str:
    if v is None:
        return ''
    try:
        return f'{float(v):.{ndigits}f}'
    except (TypeError, ValueError):
        return ''


def fmt_age(v: object) -> str:
    if v is None:
        return ''
    try:
        age = float(v)
    except (TypeError, ValueError):
        return ''
    if age.is_integer():
        return str(int(age))
    return f'{age:.1f}'.rstrip('0').rstrip('.')


def fetch_pitching_map(session: requests.Session, season: int) -> dict[str, dict]:
    params = dict(
        age='', pos='all', stats='pit', lg='all', qual='0', season=str(season),
        season1=str(season), startdate=f'{season}-03-01', enddate=f'{season}-11-30',
        month='0', hand='', team='0', pageitems='3000', pagenum='1', ind='0',
        rost='0', players='', sortdir='default', sortstat='WAR', type='42'
    )
    url = 'https://www.fangraphs.com/api/leaders/major-league/data'
    res = http_get(session, url, params=params, timeout=45)
    if res.status_code != 200:
        raise RuntimeError(f'Fangraphs pitching API failed: HTTP {res.status_code}')
    rows = res.json().get('data', [])
    out = {}
    for r in rows:
        name = r.get('PlayerName')
        if not name:
            continue
        stuff = r.get('sp_stuff')
        location = r.get('sp_location')
        era = r.get('ERA')
        whip = r.get('WHIP')
        k9 = r.get('K/9')
        bb9 = r.get('BB/9')
        out[name] = {
            'age': fmt_age(r.get('Age')),
            'era': fmt_float(era, 2),
            'whip': fmt_float(whip, 2),
            'stuff_plus': '' if stuff is None else str(int(round(float(stuff)))),
            'location_plus': '' if location is None else str(int(round(float(location)))),
            'k9': fmt_float(k9, 2),
            'bb9': fmt_float(bb9, 2),
            'vfa': fmt_float(r.get('FBv'), 1),
            'babip': fmt_float(r.get('BABIP'), 3).lstrip('0'),
            'playerid': r.get('playerid'),
        }
    return out


def fetch_pitching_row_by_player_id(session: requests.Session, season: int, player_id: int) -> dict[str, Any]:
    params = dict(
        age='', pos='all', stats='pit', lg='all', qual='0', season=str(season),
        season1=str(season), startdate=f'{season}-03-01', enddate=f'{season}-11-30',
        month='0', hand='', team='0', pageitems='3000', pagenum='1', ind='0',
        rost='0', players=str(player_id), sortdir='default', sortstat='WAR', type='42'
    )
    url = 'https://www.fangraphs.com/api/leaders/major-league/data'
    res = http_get(session, url, params=params, timeout=45)
    if res.status_code != 200:
        return {}
    rows = res.json().get('data', [])
    if not rows:
        return {}
    row = rows[0]
    return {
        'age': fmt_age(row.get('Age')),
        'era': fmt_float(row.get('ERA'), 2),
        'whip': fmt_float(row.get('WHIP'), 2),
        'stuff_plus': '' if row.get('sp_stuff') is None else str(int(round(float(row.get('sp_stuff'))))),
        'location_plus': '' if row.get('sp_location') is None else str(int(round(float(row.get('sp_location'))))),
        'k9': fmt_float(row.get('K/9'), 2),
        'bb9': fmt_float(row.get('BB/9'), 2),
        'vfa': fmt_float(row.get('FBv'), 1),
        'babip': fmt_float(row.get('BABIP'), 3).lstrip('0'),
        'playerid': row.get('playerid'),
    }


def normalize_name(name: str) -> str:
    s = unicodedata.normalize('NFKD', name)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def parse_player_ref(href: str) -> str:
    m = re.search(r'/players/[^/]+/(\d+|sa\d+)/stats', href)
    return m.group(1) if m else ''


def extract_rotation_rows(
    session: requests.Session,
    season: int,
    team_slug: str,
    pitch_map: dict[str, dict],
    pitch_by_id: dict[int, dict],
    pitch_by_name_norm: dict[str, dict],
) -> list[SPRow]:
    url = f'https://www.fangraphs.com/roster-resource/depth-charts/{team_slug}'
    html = http_get(session, url, timeout=45).text
    soup = BeautifulSoup(html, 'html.parser')
    next_data = soup.find('script', id='__NEXT_DATA__')
    rotation_meta_by_role: dict[str, dict[str, str]] = {}
    if next_data is not None and next_data.string:
        root = json.loads(next_data.string)
        data = root['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']
        roster = data.get('dataRoster', [])
        for roster_row in roster:
            role = str(roster_row.get('role', '')).strip().upper()
            if not re.fullmatch(r'SP\d+', role):
                continue
            rotation_meta_by_role[role] = {
                'age': fmt_age(roster_row.get('age') or roster_row.get('age1')),
                'playerid': str(roster_row.get('playerid', '') or '').strip(),
            }

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
        player_ref = parse_player_ref(href)
        if player_ref.isdigit():
            id_map.setdefault(name, int(player_ref))

    text = soup.get_text('\n')
    a = text.find('Projected Starting Rotation')
    b = text.find('Projected Bullpen')
    seg = text[a:b] if a != -1 and b != -1 else ''
    lines = [ln.strip() for ln in seg.split('\n') if ln.strip()]
    idx = [i for i in range(len(lines) - 1) if re.fullmatch(r'SP\d+', lines[i]) and lines[i + 1] == 'SP']

    player_id_cache: dict[int, dict[str, Any]] = {}
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
        rotation_meta = rotation_meta_by_role.get(role.upper(), {})
        roster_age = rotation_meta.get('age', '')
        source_href = link_map.get(name, '')
        source_player_id = parse_player_ref(source_href)
        if not source_player_id:
            source_player_id = rotation_meta.get('playerid', '')
        source_id_found = source_player_id.isdigit() and int(source_player_id) in pitch_by_id
        exact_name_found = name in pitch_map
        normalized_name_found = normalize_name(name) in pitch_by_name_norm
        info: dict[str, Any] = {}
        match_method = 'unmatched'
        identity_mismatch_found = False
        mismatch_candidate_player_id = ''

        def record_identity_mismatch(candidate: dict[str, Any]) -> None:
            nonlocal identity_mismatch_found, mismatch_candidate_player_id
            candidate_pid = str(candidate.get('playerid', '') or '')
            if not source_player_id.isdigit() or not candidate_pid.isdigit() or candidate_pid == source_player_id:
                return
            identity_mismatch_found = True
            if not mismatch_candidate_player_id:
                mismatch_candidate_player_id = candidate_pid

        source_pid: int | None = None
        if source_player_id.isdigit():
            source_pid = int(source_player_id)
        else:
            source_pid = id_map.get(name)

        if source_pid is not None:
            info = pitch_by_id.get(source_pid, {})
            if info:
                match_method = 'playerid'
            else:
                cached = player_id_cache.get(source_pid)
                if cached is None:
                    cached = fetch_pitching_row_by_player_id(session, season, source_pid)
                    player_id_cache[source_pid] = cached
                if cached:
                    info = cached
                    match_method = 'playerid_api'
        if not info:
            candidate = pitch_map.get(name, {})
            if candidate:
                candidate_pid = str(candidate.get('playerid', '') or '')
                if not source_player_id.isdigit() or not candidate_pid.isdigit() or candidate_pid == source_player_id:
                    info = candidate
                    match_method = 'exact_name'
                else:
                    record_identity_mismatch(candidate)
        if not info:
            candidate = pitch_by_name_norm.get(normalize_name(name), {})
            if candidate:
                candidate_pid = str(candidate.get('playerid', '') or '')
                if not source_player_id.isdigit() or not candidate_pid.isdigit() or candidate_pid == source_player_id:
                    info = candidate
                    match_method = 'normalized_name'
                else:
                    record_identity_mismatch(candidate)
        row_obj = SPRow(
            role=role.lower(),
            name=name,
            age=roster_age or info.get('age', ''),
            url=link_map.get(name, f'https://www.fangraphs.com/players/{name.lower().replace(" ", "-")}/stats/pitching'),
            era=info.get('era', ''),
            whip=info.get('whip', ''),
            k9=info.get('k9', ''),
            bb9=info.get('bb9', ''),
            stuff_plus=info.get('stuff_plus', ''),
            location_plus=info.get('location_plus', ''),
            vfa=info.get('vfa', ''),
            babip=info.get('babip', ''),
            match_method=match_method,
            source_player_id=source_player_id,
            matched_player_id=str(info.get('playerid', '') or ''),
            source_id_found_in_stats=source_id_found,
            exact_name_found_in_stats=exact_name_found,
            normalized_name_found_in_stats=normalized_name_found,
            identity_mismatch_found=identity_mismatch_found,
            mismatch_candidate_player_id=mismatch_candidate_player_id,
        )
        rows.append(row_obj)

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description='Fetch Fangraphs projected SP1-SP5 + ERA, WHIP, K/9, BB/9, Stuff+, Location+, vFA, BABIP for MLB teams.')
    parser.add_argument('--season', type=int, default=2025)
    parser.add_argument('--out', type=Path, default=Path('data/fangraphs_sp_2025.json'))
    args = parser.parse_args()

    s = requests.Session()
    s.trust_env = False
    http_get(s, 'https://www.fangraphs.com', timeout=45)

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
            for r in extract_rotation_rows(s, args.season, slug, pitch_map, pitch_by_id, pitch_by_name_norm)
        ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {args.out} for {len(result)} teams')


if __name__ == '__main__':
    main()
