#!/usr/bin/env python3
import argparse
import json
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
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
class RPRow:
    role: str
    name: str
    url: str
    era: str
    k9: str
    bb9: str
    k_pct: str
    stuff_plus: str
    match_method: str = 'unmatched'
    source_player_id: str = ''
    matched_player_id: str = ''
    source_id_found_in_stats: bool = False
    exact_name_found_in_stats: bool = False
    normalized_name_found_in_stats: bool = False
    loose_name_found_in_stats: bool = False
    identity_mismatch_found: bool = False
    mismatch_candidate_player_id: str = ''


def make_session() -> requests.Session:
    s = requests.Session()
    s.trust_env = False
    return s


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


def normalize_name(name: str) -> str:
    s = unicodedata.normalize('NFKD', name)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def drop_middle_initials(name_key: str) -> str:
    parts = [p for p in name_key.split(' ') if p]
    if len(parts) <= 2:
        return name_key
    keep = [parts[0]] + [p for p in parts[1:-1] if len(p) > 1] + [parts[-1]]
    return ' '.join(keep)


def clean_player_name(name: str) -> str:
    return re.sub(r'\s+\([^)]+\)$', '', name).strip()


def parse_player_ref(href: str) -> str:
    m = re.search(r'/players/[^/]+/(\d+|sa\d+)/stats', href)
    return m.group(1) if m else ''


def fmt_float(v: Any, ndigits: int = 2) -> str:
    if v is None:
        return ''
    try:
        return f'{float(v):.{ndigits}f}'
    except (TypeError, ValueError):
        return ''


def fmt_int(v: Any) -> str:
    if v is None:
        return ''
    try:
        return str(int(round(float(v))))
    except (TypeError, ValueError):
        return ''


def fmt_pct(v: Any) -> str:
    if v is None:
        return ''
    try:
        return f'{float(v) * 100:.1f}%'
    except (TypeError, ValueError):
        return ''


def fetch_pitching_map(session: requests.Session, season: int) -> dict[str, dict[str, Any]]:
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
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        name = r.get('PlayerName')
        if not name:
            continue
        out[name] = {
            'era': fmt_float(r.get('ERA'), 2),
            'k9': fmt_float(r.get('K/9'), 2),
            'bb9': fmt_float(r.get('BB/9'), 2),
            'k_pct': fmt_pct(r.get('K%')),
            'stuff_plus': fmt_int(r.get('sp_stuff')),
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
        'era': fmt_float(row.get('ERA'), 2),
        'k9': fmt_float(row.get('K/9'), 2),
        'bb9': fmt_float(row.get('BB/9'), 2),
        'k_pct': fmt_pct(row.get('K%')),
        'stuff_plus': fmt_int(row.get('sp_stuff')),
        'playerid': row.get('playerid'),
    }


def extract_bullpen_rows(
    session: requests.Session,
    season: int,
    team_slug: str,
    pitch_map: dict[str, dict[str, Any]],
    pitch_by_id: dict[int, dict[str, Any]],
    pitch_by_name_norm: dict[str, dict[str, Any]],
) -> list[RPRow]:
    url = f'https://www.fangraphs.com/roster-resource/depth-charts/{team_slug}'
    resp = http_get(session, url, timeout=45)
    if resp.status_code != 200:
        raise RuntimeError(f'Depth chart request failed for {team_slug}: HTTP {resp.status_code}')

    soup = BeautifulSoup(resp.text, 'html.parser')
    link_map: dict[str, str] = {}
    id_map: dict[str, int] = {}
    for a in soup.select('a[href*="/players/"]'):
        name = a.get_text(strip=True)
        href = a.get('href', '').strip()
        if not name or '/players/' not in href:
            continue
        if href.startswith('/'):
            href = 'https://www.fangraphs.com' + href
        clean_name = clean_player_name(name)
        link_map.setdefault(clean_name, href)
        player_ref = parse_player_ref(href)
        if player_ref.isdigit():
            id_map.setdefault(clean_name, int(player_ref))

    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data is None or not next_data.string:
        raise RuntimeError(f'Cannot find __NEXT_DATA__ in depth chart page for {team_slug}')

    root = json.loads(next_data.string)
    data = root['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']
    roster = data.get('dataRoster', [])
    bullpen = [r for r in roster if str(r.get('type', '')).strip().lower() == 'mlb-bp']
    role_rank = {'CL': 1, 'SU8': 2, 'SU7': 3, 'MID': 4, 'LR': 5}
    bullpen.sort(key=lambda r: (role_rank.get(str(r.get('role', '')).strip().upper(), 99), str(r.get('role', '')).strip().upper()))

    player_id_cache: dict[int, dict[str, Any]] = {}
    out: list[RPRow] = []
    for r in bullpen:
        role = str(r.get('role', '')).strip().upper()
        raw_name = str(r.get('player', '')).strip()
        name = clean_player_name(raw_name)
        if not role or not name:
            continue

        source_href = link_map.get(name, '')
        source_player_id = parse_player_ref(source_href)
        if not source_player_id:
            raw_pid = str(r.get('playerid', '') or '').strip()
            if raw_pid:
                source_player_id = raw_pid
        source_id_found = source_player_id.isdigit() and int(source_player_id) in pitch_by_id
        exact_name_found = name in pitch_map
        normalized_name_found = normalize_name(name) in pitch_by_name_norm
        loose_name_found = drop_middle_initials(normalize_name(name)) in pitch_by_name_norm
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

        pid: int | None = None
        if source_player_id.isdigit():
            pid = int(source_player_id)
        else:
            pid = id_map.get(name)
        if pid is None:
            try:
                raw_pid = r.get('playerid')
                pid = int(raw_pid) if raw_pid is not None else None
            except (TypeError, ValueError):
                pid = None
        if pid is not None:
            info = pitch_by_id.get(pid, {})
            if info:
                match_method = 'playerid'
            else:
                cached = player_id_cache.get(pid)
                if cached is None:
                    cached = fetch_pitching_row_by_player_id(session, season, pid)
                    player_id_cache[pid] = cached
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
        if not info:
            candidate = pitch_by_name_norm.get(drop_middle_initials(normalize_name(name)), {})
            if candidate:
                candidate_pid = str(candidate.get('playerid', '') or '')
                if not source_player_id.isdigit() or not candidate_pid.isdigit() or candidate_pid == source_player_id:
                    info = candidate
                    match_method = 'loose_name'
                else:
                    record_identity_mismatch(candidate)

        out.append(
            RPRow(
                role=role,
                name=name,
                url=link_map.get(name, f'https://www.fangraphs.com/players/{name.lower().replace(" ", "-")}/stats/pitching'),
                era=info.get('era', ''),
                k9=info.get('k9', ''),
                bb9=info.get('bb9', ''),
                k_pct=info.get('k_pct', ''),
                stuff_plus=info.get('stuff_plus', ''),
                match_method=match_method,
                source_player_id=source_player_id,
                matched_player_id=str(info.get('playerid', '') or ''),
                source_id_found_in_stats=source_id_found,
                exact_name_found_in_stats=exact_name_found,
                normalized_name_found_in_stats=normalized_name_found,
                loose_name_found_in_stats=loose_name_found,
                identity_mismatch_found=identity_mismatch_found,
                mismatch_candidate_player_id=mismatch_candidate_player_id,
            )
        )
    return out


def rp_markdown(rows: list[dict[str, str]]) -> str:
    head = [
        '## RP',
        '|Role|Name|ERA|K/9|BB/9|K%|stuff+|',
        '|---|---|---|---|---|---|---|',
    ]
    body = [
        f"|{r['role']}|[**{r['name']}**]({r['url']})|{r['era']}|{r['k9']}|{r['bb9']}|{r['k_pct']}|{r['stuff_plus']}|"
        for r in rows
    ]
    return '\n'.join(head + body)


def strip_existing_rp(content: str) -> str:
    if '\n## RP\n' in content:
        return content.split('\n## RP\n', 1)[0]
    if content.startswith('## RP\n'):
        return ''
    return content


def update_notion_payload(payload_path: Path, rp_data: dict[str, list[dict[str, str]]], out_path: Path) -> None:
    payload = json.loads(payload_path.read_text(encoding='utf-8'))
    if len(payload) != len(TEAM_SLUGS):
        raise RuntimeError(f'Unexpected payload length {len(payload)} (expected {len(TEAM_SLUGS)})')

    updated = 0
    for row in payload:
        team = str(row.get('team', '')).strip()
        if not team:
            continue
        content = str(row.get('content', ''))
        base = strip_existing_rp(content).rstrip()
        rp_rows = rp_data.get(team, [])
        row['content'] = base + '\n\n' + rp_markdown(rp_rows)
        row['rp_count'] = len(rp_rows)
        updated += 1

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Updated payload rows: {updated}, wrote: {out_path}')


def validate_rp_data(data: dict[str, list[dict[str, str]]], season: int) -> None:
    if season != 2025:
        raise RuntimeError(f'Validation guard failed: expected season=2025, got {season}')
    if len(data) != 30:
        raise RuntimeError(f'Validation failed: expected 30 teams, got {len(data)}')

    short_teams = [(team, len(rows)) for team, rows in data.items() if len(rows) < 5]
    if short_teams:
        short = ', '.join([f'{t}:{n}' for t, n in short_teams[:8]])
        raise RuntimeError(f'Validation failed: RP rows < 5 for teams: {short}')

    print('Validation passed: season=2025, teams=30, each team has at least 5 RP rows.')


def main() -> None:
    parser = argparse.ArgumentParser(description='Fetch Fangraphs projected bullpen (RP) + pitching stats and update Notion payload.')
    parser.add_argument('--season', type=int, default=2025)
    parser.add_argument('--out', type=Path, default=Path('data/fangraphs_rp_2025.json'))
    parser.add_argument('--payload-in', type=Path, default=Path('data/notion_batter_fix_payload_2025_nocookie_v2_corrected.json'))
    parser.add_argument('--payload-out', type=Path, default=Path('data/notion_rp_fix_payload_2025.json'))
    parser.add_argument('--skip-payload-update', action='store_true')
    args = parser.parse_args()

    if args.season != 2025:
        raise RuntimeError('This workflow is pinned to 2025 validation. Use --season 2025.')

    s = make_session()
    pitch_map = fetch_pitching_map(s, args.season)
    pitch_by_id: dict[int, dict[str, Any]] = {}
    pitch_by_name_norm: dict[str, dict[str, Any]] = {}
    for name, info in pitch_map.items():
        pid = info.get('playerid')
        if isinstance(pid, int):
            pitch_by_id[pid] = info
        pitch_by_name_norm[normalize_name(name)] = info

    result: dict[str, list[dict[str, str]]] = {}
    for abbr, slug in TEAM_SLUGS.items():
        rows = extract_bullpen_rows(s, args.season, slug, pitch_map, pitch_by_id, pitch_by_name_norm)
        result[abbr] = [asdict(r) for r in rows]

    validate_rp_data(result, args.season)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote RP data: {args.out}')

    if not args.skip_payload_update:
        update_notion_payload(args.payload_in, result, args.payload_out)


if __name__ == '__main__':
    main()
