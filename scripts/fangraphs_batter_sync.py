#!/usr/bin/env python3
import argparse
import json
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

try:
    import cloudscraper  # type: ignore
except Exception:
    cloudscraper = None

try:
    import browser_cookie3  # type: ignore
except Exception:
    browser_cookie3 = None

import requests

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

POS_SET = {'C', '1B', '2B', '3B', 'SS', 'LF', 'CF', 'RF', 'DH', 'OF'}


@dataclass
class BatterRow:
    order: str
    name: str
    position: str
    url: str
    wrc_plus: str
    avg: str
    obp: str
    slg: str
    match_method: str = 'unmatched'
    source_player_id: str = ''
    matched_player_id: str = ''
    source_id_found_in_stats: bool = False
    exact_name_found_in_stats: bool = False
    normalized_name_found_in_stats: bool = False
    loose_name_found_in_stats: bool = False


def make_session(use_cloudscraper: bool = False) -> requests.Session:
    if use_cloudscraper and cloudscraper is not None:
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'mobile': False})
        scraper.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        return scraper

    # Fangraphs batting API is currently more permissive with default python-requests headers.
    s = requests.Session()
    # Avoid unstable proxy settings inherited from environment.
    s.trust_env = False
    return s


def apply_cookie_header(session: requests.Session, cookie_header: str) -> None:
    for part in cookie_header.split(';'):
        item = part.strip()
        if not item or '=' not in item:
            continue
        k, v = item.split('=', 1)
        session.cookies.set(k.strip(), v.strip(), domain='.fangraphs.com')


def apply_browser_cookies(session: requests.Session, browser: str) -> None:
    if browser_cookie3 is None:
        raise RuntimeError('browser-cookie3 is not installed; cannot load browser cookies')

    browser = browser.lower()
    loader_map = {
        'chrome': browser_cookie3.chrome,
        'chromium': browser_cookie3.chromium,
        'edge': browser_cookie3.edge,
        'firefox': browser_cookie3.firefox,
        'brave': browser_cookie3.brave,
    }
    if browser not in loader_map:
        raise RuntimeError(f'Unsupported browser "{browser}" for cookie import')

    jar = loader_map[browser](domain_name='fangraphs.com')
    for c in jar:
        if 'fangraphs.com' in (c.domain or ''):
            session.cookies.set(c.name, c.value, domain=c.domain, path=c.path)


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
    return s.lower().strip()


def normalize_name_loose(name: str) -> str:
    s = normalize_name(name).replace('.', '')
    parts = [p for p in re.split(r'\s+', s) if p]
    if len(parts) >= 3:
        # Remove middle initials / one-letter middle names.
        parts = [parts[0]] + [p for p in parts[1:-1] if len(p) > 1] + [parts[-1]]
    if parts:
        nickname_map = {
            'jacob': 'jake',
            'joseph': 'joey',
            'joshua': 'josh',
            'luisangel': 'luis',
            'maxwell': 'max',
            'michael': 'mike',
            'william': 'will',
        }
        parts[0] = nickname_map.get(parts[0], parts[0])
    return ' '.join(parts)


def clean_player_name(name: str) -> str:
    # Remove roster-resource disambiguation suffixes like "Jacob Wilson (oak)".
    return re.sub(r'\s+\([^)]+\)$', '', name).strip()


def name_variants(name: str) -> list[str]:
    out = [name]
    no_mid = re.sub(r'\b[A-Z]\.\s*', '', name).replace('  ', ' ').strip()
    if no_mid and no_mid not in out:
        out.append(no_mid)
    suffixes = ('Jr.', 'Jr', 'II', 'III', 'IV')
    for base in list(out):
        no_suffix = re.sub(r'\s+(jr|sr|ii|iii|iv)\.?$', '', base, flags=re.IGNORECASE).strip()
        if no_suffix and no_suffix not in out:
            out.append(no_suffix)
        if no_suffix:
            for suffix in suffixes:
                cand = f'{no_suffix} {suffix}'
                if cand not in out:
                    out.append(cand)
    if name.startswith('Maxwell '):
        out.append(name.replace('Maxwell ', 'Max ', 1))
    first_name_variants = {
        'Jacob': ['Jake'],
        'Jazz': ['Jasrado'],
        'J.J.': ['JJ'],
        'JJ': ['J.J.'],
        'Joseph': ['Joey'],
        'Joshua': ['Josh'],
        'Luisangel': ['Luis'],
        'Michael': ['Mike'],
        'William': ['Will'],
        'Will': ['William'],
    }
    parts = name.split(' ', 1)
    if len(parts) == 2:
        first, rest = parts
        for alias in first_name_variants.get(first, []):
            cand = f'{alias} {rest}'
            if cand not in out:
                out.append(cand)
    special_variants = {
        'Luis V. Garcia': ['Luis Garcia Jr.', 'Luis Garcia'],
    }
    for cand in special_variants.get(name, []):
        if cand not in out:
            out.append(cand)
    return out


def fmt_avg(v: Any) -> str:
    if v is None:
        return ''
    try:
        return f"{float(v):.3f}".lstrip('0')
    except (TypeError, ValueError):
        return ''


def fmt_int(v: Any) -> str:
    if v is None:
        return ''
    try:
        return str(int(round(float(v))))
    except (TypeError, ValueError):
        return ''


def parse_player_ref(href: str) -> str:
    m = re.search(r'/players/[^/]+/(\d+|sa\d+)/stats', href)
    return m.group(1) if m else ''


def fetch_batting_map(session: requests.Session, season: int) -> dict[str, dict[str, str]]:
    params = dict(
        age='', pos='all', stats='bat', lg='all', qual='0', season=str(season),
        season1=str(season), startdate=f'{season}-03-01', enddate=f'{season}-11-30',
        month='0', hand='', team='0', pageitems='3000', pagenum='1', ind='0',
        rost='0', players='', sortdir='default', sortstat='WAR', type='8'
    )
    url = 'https://www.fangraphs.com/api/leaders/major-league/data'
    res = http_get(session, url, params=params, timeout=45)
    if res.status_code != 200:
        raise RuntimeError(f'Fangraphs batting API failed: HTTP {res.status_code}')

    rows = res.json().get('data', [])
    out: dict[str, dict[str, str]] = {}
    for r in rows:
        name = r.get('PlayerName')
        if not name:
            continue

        wrc_val = r.get('wRC+')
        if wrc_val is None:
            wrc_val = r.get('wRCPlus')

        out[name] = {
            'wrc_plus': fmt_int(wrc_val),
            'avg': fmt_avg(r.get('AVG')),
            'obp': fmt_avg(r.get('OBP')),
            'slg': fmt_avg(r.get('SLG')),
            'playerid': r.get('playerid'),
        }
    return out


def extract_lineup_rows(
    session: requests.Session,
    team_slug: str,
    batting_map: dict[str, dict[str, str]],
    batting_by_id: dict[int, dict[str, str]],
    batting_by_name_norm: dict[str, dict[str, str]],
    batting_by_name_loose: dict[str, dict[str, str]],
) -> list[BatterRow]:
    url = f'https://www.fangraphs.com/roster-resource/depth-charts/{team_slug}'
    resp = http_get(session, url, timeout=45)
    if resp.status_code != 200:
        raise RuntimeError(f'Depth chart request failed for {team_slug}: HTTP {resp.status_code}')

    soup = BeautifulSoup(resp.text, 'html.parser')

    link_map: dict[str, str] = {}
    id_map: dict[str, int] = {}
    link_by_norm: dict[str, tuple[str, str, int | None]] = {}
    link_by_loose: dict[str, tuple[str, str, int | None]] = {}
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
        pid_val: int | None = None
        if player_ref.isdigit():
            pid_val = int(player_ref)
            id_map.setdefault(clean_name, pid_val)
        link_by_norm.setdefault(normalize_name(clean_name), (clean_name, href, pid_val))
        link_by_loose.setdefault(normalize_name_loose(clean_name), (clean_name, href, pid_val))

    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data is None or not next_data.string:
        raise RuntimeError(f'Cannot find __NEXT_DATA__ in depth chart page for {team_slug}')

    root = json.loads(next_data.string)
    data = root['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']
    roster = data.get('dataRoster', [])
    lineup = [
        r for r in roster
        if r.get('type') == 'mlb-sl' and re.fullmatch(r'[1-9]', str(r.get('role', '')).strip())
    ]
    lineup.sort(key=lambda r: int(str(r.get('role'))))

    out: list[BatterRow] = []
    for r in lineup:
        order = str(r.get('role', '')).strip()
        position = str(r.get('position', '')).strip()
        raw_name = str(r.get('player', '')).strip()
        name = clean_player_name(raw_name)
        if not name:
            continue

        info: dict[str, str] = {}
        matched_name = name
        match_method = 'unmatched'
        roster_href = link_map.get(name, '')
        if not roster_href:
            norm_hit = link_by_norm.get(normalize_name(name))
            if norm_hit:
                _, roster_href, _ = norm_hit
            else:
                loose_hit = link_by_loose.get(normalize_name_loose(name))
                if loose_hit:
                    _, roster_href, _ = loose_hit
        source_player_id = parse_player_ref(roster_href)
        exact_name_found = name in batting_map
        source_id_found = source_player_id.isdigit() and int(source_player_id) in batting_by_id
        normalized_name_found = normalize_name(name) in batting_by_name_norm
        loose_name_found = normalize_name_loose(name) in batting_by_name_loose
        for cand in name_variants(name):
            if cand in batting_map:
                info = batting_map[cand]
                matched_name = cand
                match_method = 'exact_name'
                break
            pid = id_map.get(cand)
            if pid is not None and pid in batting_by_id:
                info = batting_by_id[pid]
                matched_name = cand
                match_method = 'playerid'
                break
            by_norm = batting_by_name_norm.get(normalize_name(cand), {})
            if by_norm:
                info = by_norm
                matched_name = cand
                match_method = 'normalized_name'
                break
            loose = batting_by_name_loose.get(normalize_name_loose(cand), {})
            if loose:
                info = loose
                matched_name = cand
                match_method = 'loose_name'
                break

        link_name = matched_name
        link_url = ''
        for cand in name_variants(matched_name):
            link_url = link_map.get(cand, '')
            if link_url:
                link_name = cand
                break
            norm_hit = link_by_norm.get(normalize_name(cand))
            if norm_hit:
                link_name, link_url, _ = norm_hit
                break
            loose_hit = link_by_loose.get(normalize_name_loose(cand))
            if loose_hit:
                link_name, link_url, _ = loose_hit
                break
        if not link_url:
            link_url = f'https://www.fangraphs.com/players/{name.lower().replace(" ", "-")}/stats?position=1B/2B/3B/SS/OF'

        out.append(BatterRow(
            order=order,
            name=link_name,
            position=position if position in POS_SET else position,
            url=link_url,
            wrc_plus=info.get('wrc_plus', ''),
            avg=info.get('avg', ''),
            obp=info.get('obp', ''),
            slg=info.get('slg', ''),
            match_method=match_method,
            source_player_id=source_player_id,
            matched_player_id=str(info.get('playerid', '') or ''),
            source_id_found_in_stats=source_id_found,
            exact_name_found_in_stats=exact_name_found,
            normalized_name_found_in_stats=normalized_name_found,
            loose_name_found_in_stats=loose_name_found,
        ))

    out.sort(key=lambda r: int(r.order) if r.order.isdigit() else 99)
    return out


def batter_markdown(rows: list[dict[str, str]]) -> str:
    head = [
        '## Batter',
        '|Order|Name|Position|wRC+|AVG|OBP|SLG|',
        '|---|---|---|---|---|---|---|',
    ]
    body = [
        f"|{r['order']}|[**{r['name']}**]({r['url']})|{r['position']}|{r['wrc_plus']}|{r['avg']}|{r['obp']}|{r['slg']}|"
        for r in rows
    ]
    return '\n'.join(head + body)


def update_notion_payload(payload_path: Path, batter_data: dict[str, list[dict[str, str]]], out_path: Path) -> None:
    payload = json.loads(payload_path.read_text(encoding='utf-8'))
    if len(payload) != len(TEAM_SLUGS):
        raise RuntimeError(f'Unexpected payload length {len(payload)} (expected {len(TEAM_SLUGS)})')

    updated = 0
    for row in payload:
        team = str(row.get('team', '')).strip()
        if not team:
            continue
        content = row.get('content', '')
        if '## SP' not in content:
            continue

        sp_part = content.split('## SP', 1)[1]
        rows = batter_data.get(team, [])
        row['content'] = batter_markdown(rows) + '\n\n## SP' + sp_part
        updated += 1

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Updated payload rows: {updated}, wrote: {out_path}')


def validate_batter_data(data: dict[str, list[dict[str, str]]], season: int) -> None:
    if season != 2025:
        raise RuntimeError(f'Validation guard failed: expected season=2025, got {season}')

    if len(data) != 30:
        raise RuntimeError(f'Validation failed: expected 30 teams, got {len(data)}')

    missing_lineup = []
    for team, rows in data.items():
        if len(rows) < 9:
            missing_lineup.append((team, len(rows)))

    if missing_lineup:
        short = ', '.join([f'{t}:{n}' for t, n in missing_lineup[:8]])
        raise RuntimeError(f'Validation failed: lineup rows < 9 for teams: {short}')

    print('Validation passed: season=2025, teams=30, each team has at least 9 batter rows.')


def main() -> None:
    parser = argparse.ArgumentParser(description='Fetch Fangraphs projected lineup + batting stats and update Notion payload.')
    parser.add_argument('--season', type=int, default=2025)
    parser.add_argument('--out', type=Path, default=Path('data/fangraphs_batter_2025.json'))
    parser.add_argument('--payload-in', type=Path, default=Path('data/notion_sp_fix_payload_v3.json'))
    parser.add_argument('--payload-out', type=Path, default=Path('data/notion_batter_fix_payload_2025.json'))
    parser.add_argument('--skip-payload-update', action='store_true')
    parser.add_argument('--use-cloudscraper', action='store_true')
    parser.add_argument('--use-browser-cookies', action='store_true')
    parser.add_argument('--cookie-browser', default='chrome')
    parser.add_argument('--cookie-header', default='')
    args = parser.parse_args()

    if args.season != 2025:
        raise RuntimeError('This workflow is pinned to 2025 validation. Use --season 2025.')

    s = make_session(use_cloudscraper=args.use_cloudscraper)
    if args.use_browser_cookies:
        apply_browser_cookies(s, args.cookie_browser)
    if args.cookie_header.strip():
        apply_cookie_header(s, args.cookie_header.strip())

    batting_map = fetch_batting_map(s, args.season)
    batting_by_id: dict[int, dict[str, str]] = {}
    batting_by_name_norm: dict[str, dict[str, str]] = {}
    batting_by_name_loose: dict[str, dict[str, str]] = {}
    for name, info in batting_map.items():
        pid = info.get('playerid')
        if isinstance(pid, int):
            batting_by_id[pid] = info
        batting_by_name_norm[normalize_name(name)] = info
        batting_by_name_loose[normalize_name_loose(name)] = info

    result: dict[str, list[dict[str, str]]] = {}
    for abbr, slug in TEAM_SLUGS.items():
        rows = extract_lineup_rows(s, slug, batting_map, batting_by_id, batting_by_name_norm, batting_by_name_loose)
        result[abbr] = [asdict(r) for r in rows]

    validate_batter_data(result, args.season)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote batter data: {args.out}')

    if not args.skip_payload_update:
        update_notion_payload(args.payload_in, result, args.payload_out)


if __name__ == '__main__':
    main()
