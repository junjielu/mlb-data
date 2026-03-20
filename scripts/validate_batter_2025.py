#!/usr/bin/env python3
import json
from pathlib import Path

REQUIRED_TEAMS = 30


def validate_batter_json(path: Path) -> None:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise RuntimeError('batter json must be an object keyed by team abbr')
    if len(data) != REQUIRED_TEAMS:
        raise RuntimeError(f'expected {REQUIRED_TEAMS} teams, got {len(data)}')

    for team, rows in data.items():
        if len(rows) < 9:
            raise RuntimeError(f'{team}: lineup rows < 9 ({len(rows)})')
        for r in rows[:9]:
            for k in ['order', 'name', 'position', 'wrc_plus', 'avg', 'obp', 'slg']:
                if k not in r:
                    raise RuntimeError(f'{team}: missing key {k}')
            all_empty = all(not str(r.get(k, '')).strip() for k in ['wrc_plus', 'avg', 'obp', 'slg'])
            url = str(r.get('url', '')).strip()
            if all_empty and '/stats?position=' in url:
                raise RuntimeError(
                    f"{team}: unresolved batter mapping for {r.get('order')} {r.get('name')} ({url})"
                )


def validate_payload(path: Path) -> None:
    payload = json.loads(path.read_text(encoding='utf-8'))
    if len(payload) != REQUIRED_TEAMS:
        raise RuntimeError(f'payload rows expected {REQUIRED_TEAMS}, got {len(payload)}')

    required_header = '|Order|Name|Position|wRC+|AVG|OBP|SLG|'
    for i, row in enumerate(payload):
        content = row.get('content', '')
        if '## Batter' not in content:
            raise RuntimeError(f'payload row {i}: missing Batter section')
        if required_header not in content:
            raise RuntimeError(f'payload row {i}: Batter columns mismatch')
        if '## SP' not in content:
            raise RuntimeError(f'payload row {i}: missing SP section')


def main() -> None:
    batter_json = Path('data/fangraphs_batter_2025.json')
    payload_json = Path('data/notion_batter_fix_payload_2025.json')

    if not batter_json.exists():
        raise RuntimeError(f'missing {batter_json}; run batter sync first with season=2025')
    validate_batter_json(batter_json)

    if payload_json.exists():
        validate_payload(payload_json)
        print('Validation passed: batter data and payload format are ready for 2025 sync.')
    else:
        print('Validation passed: batter data file is valid for 2025.')


if __name__ == '__main__':
    main()
