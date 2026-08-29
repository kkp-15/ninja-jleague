#!/usr/bin/env python3
"""Jリーグ公式データサイトから日程・結果を取得する。

取得元は https://data.j-league.or.jp/SFMS01/search （公式のデータ公開ページ）。
1リクエストで全380試合が取れるので、サイトに負荷をかけない。
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = ('https://data.j-league.or.jp/SFMS01/search'
       '?competition_years=2026&competition_frame_ids=1&competition_ids=725')


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh)'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')


def parse(html):
    games = []
    for tr in re.findall(r'<tr[^>]*>([\s\S]*?)</tr>', html):
        cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', c)).strip()
                 for c in re.findall(r'<t[dh][^>]*>([\s\S]*?)</t[dh]>', tr)]
        if len(cells) < 9 or '2026/27' not in cells[0]:
            continue
        sec = re.search(r'第(\d+)節', cells[2])
        d = re.match(r'(\d\d)/(\d\d)/(\d\d)', cells[3])
        score = cells[6]
        m = re.match(r'^(\d+)-(\d+)$', score)
        games.append({
            'section': int(sec.group(1)) if sec else None,
            'date': f'20{d.group(1)}-{d.group(2)}-{d.group(3)}' if d else None,
            'home': cells[5], 'away': cells[7],
            'status': 'played' if m else 'pending',
            'hg': int(m.group(1)) if m else None,
            'ag': int(m.group(2)) if m else None,
            'venue': cells[8] if len(cells) > 8 else '',
        })
    return games


def standings(games):
    """勝点は勝3・分1・負0。順位は 勝点→得失点差→総得点（Jリーグ規定の上位3項目）。"""
    t = {}
    def row(n):
        return t.setdefault(n, {'team': n, 'g': 0, 'w': 0, 'd': 0, 'l': 0,
                                'gf': 0, 'ga': 0, 'pts': 0})
    for g in games:
        row(g['home']); row(g['away'])
        if g['status'] != 'played':
            continue
        h, a = t[g['home']], t[g['away']]
        h['g'] += 1; a['g'] += 1
        h['gf'] += g['hg']; h['ga'] += g['ag']
        a['gf'] += g['ag']; a['ga'] += g['hg']
        if g['hg'] > g['ag']:
            h['w'] += 1; a['l'] += 1; h['pts'] += 3
        elif g['hg'] < g['ag']:
            a['w'] += 1; h['l'] += 1; a['pts'] += 3
        else:
            h['d'] += 1; a['d'] += 1; h['pts'] += 1; a['pts'] += 1
    rows = list(t.values())
    for r in rows:
        r['gd'] = r['gf'] - r['ga']
    rows.sort(key=lambda r: (-r['pts'], -r['gd'], -r['gf'], r['team']))
    for i, r in enumerate(rows, 1):
        r['rank'] = i
    return rows


def main():
    games = parse(fetch(URL))
    if len(games) < 300:
        print(f'[error] 試合数が少なすぎる（{len(games)}）。取得に失敗した可能性が高い', file=sys.stderr)
        return 1
    rows = standings(games)
    played = sum(1 for g in games if g['status'] == 'played')
    # 全クラブの消化数が揃っているか＝取りこぼしの検知
    total_from_rows = sum(r['g'] for r in rows)
    if total_from_rows != played * 2:
        print(f'[warn] 消化数の不一致 rows={total_from_rows} games={played*2}', file=sys.stderr)
    jst = timezone(timedelta(hours=9))
    out = {
        'generated_at': datetime.now(jst).strftime('%Y-%m-%dT%H:%M:%S'),
        'as_of': max((g['date'] for g in games if g['status'] == 'played'), default=None),
        'season': '2026/27', 'league': 'J1',
        'total_sections': max((g['section'] or 0) for g in games),
        'played': played, 'pending': len(games) - played,
        'standings': rows, 'games': games,
    }
    os.makedirs(os.path.join(ROOT, 'data'), exist_ok=True)
    with open(os.path.join(ROOT, 'data', 'j1.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f'[ok] data/j1.json  {len(games)}試合（消化{played}）  {len(rows)}クラブ  as_of={out["as_of"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
