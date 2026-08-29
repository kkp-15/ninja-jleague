#!/usr/bin/env python3
"""残留ライン・降格確率・優勝確率を計算する。

野球のマジックと違い、サッカーは勝点3/1/0で引分がある。
「あと何勝で確定」より「勝点いくつで残留できるか」が読者の関心なので、
残留ラインを主役に据える。

まだ3節しか消化していない時期に確率を断定すると嘘になるので、
消化率が低いときは「参考値」と明示する（判断は呼び出し側）。
"""
import json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRIALS = 20000
SEED = 20260828
RELEGATION_SLOTS = 3     # 下位3クラブがJ2へ自動降格（2026/27）
# 2025年J1の全380試合で実測: 引分25.5%・ホーム勝率44.2%（2026-08-28に確認）。
# 今季30試合の実測は20.0%だが母数が小さいので、過去シーズンの値を使う。
DRAW_RATE = 0.255
HOME_EDGE = 1.10         # ホーム勝率44.2% vs アウェイ30.3% から逆算した目安


def load():
    with open(os.path.join(ROOT, 'data', 'j1.json'), encoding='utf-8') as f:
        return json.load(f)


def strength(r, k=8):
    """平均回帰。試合数が少ないうちは 1.5点/試合（勝点の期待値）へ寄せる。"""
    return (r['pts'] + k * 1.5) / (r['g'] + k) if (r['g'] + k) else 1.5


def simulate(d, trials=TRIALS, seed=SEED):
    rows = d['standings']
    idx = {r['team']: i for i, r in enumerate(rows)}
    n = len(rows)
    st = [strength(r) for r in rows]
    pend = [(idx[g['home']], idx[g['away']]) for g in d['games']
            if g['status'] == 'pending' and g['home'] in idx and g['away'] in idx]
    # 各カードの勝敗確率を事前に決める（ホームアドバンテージ込み）
    probs = []
    for h, a in pend:
        sh, sa = st[h] * HOME_EDGE, st[a]
        pw = sh / (sh + sa) * (1 - DRAW_RATE)
        pl = sa / (sh + sa) * (1 - DRAW_RATE)
        probs.append((pw, pw + DRAW_RATE, pl))

    res = [{'champ': 0, 'top3': 0, 'releg': 0, 'acl': 0} for _ in range(n)]
    line_samples = []                          # 18位（残留最下位）の最終勝点
    rng = random.Random(seed)
    rand = rng.random
    base_pts = [r['pts'] for r in rows]
    base_gd = [r['gd'] for r in rows]

    for _ in range(trials):
        pts = base_pts[:]
        for gi, (h, a) in enumerate(pend):
            x = rand(); pw, pd, _ = probs[gi]
            if x < pw: pts[h] += 3
            elif x < pd: pts[h] += 1; pts[a] += 1
            else: pts[a] += 3
        order = sorted(range(n), key=lambda i: (-pts[i], -base_gd[i]))
        for rank, i in enumerate(order, 1):
            if rank == 1: res[i]['champ'] += 1
            if rank <= 3: res[i]['top3'] += 1
            if rank > n - RELEGATION_SLOTS: res[i]['releg'] += 1
        line_samples.append(pts[order[n - RELEGATION_SLOTS - 1]])   # 17位＝残留の最下位

    line_samples.sort()
    def pct(p):
        return line_samples[min(len(line_samples) - 1, int(len(line_samples) * p))]

    out = {}
    for i, r in enumerate(rows):
        out[r['team']] = {k: round(v / trials * 100, 1) for k, v in res[i].items()}
    return out, {
        'median': pct(0.50), 'p25': pct(0.25), 'p75': pct(0.75),
        'safe': pct(0.90),   # ここまで積めば9割方残れる
    }


def bounds(d):
    """各クラブの理論上の最大・最小勝点。「まだ届く／もう届かない」の根拠になる。"""
    rows = d['standings']
    rest = {r['team']: 0 for r in rows}
    for g in d['games']:
        if g['status'] != 'pending':
            continue
        for t in (g['home'], g['away']):
            if t in rest:
                rest[t] += 1
    out = {}
    for r in rows:
        n = rest[r['team']]
        out[r['team']] = {'rest': n, 'max': r['pts'] + n * 3, 'min': r['pts']}
    return out


# 過去の実際の残留ライン（当サイトで公式データから算出。2026-08-28検証）
# 20クラブ制になってからは 41〜43 点。ネット上に多い「36点」は18クラブ時代の数字で、
# いまの20クラブ・38節には当てはまらない。ここを正しく出せることが本サイトの価値。
HISTORY = [
    {'season': '2025', 'clubs': 20, 'line': 43, 'team': '東京Ｖ', 'below': 35, 'champ': 76},
    {'season': '2024', 'clubs': 20, 'line': 41, 'team': '柏',     'below': 38, 'champ': 72},
    {'season': '2023', 'clubs': 18, 'line': 34, 'team': '湘南',   'below': 34, 'champ': 71},
]


def main():
    d = load()
    probs, line = simulate(d)
    bd = bounds(d)
    for r in d['standings']:
        r.update(bd[r['team']])
        r['prob'] = probs[r['team']]
    d['line'] = line
    d['history'] = HISTORY
    d['trials'] = TRIALS
    d['relegation_slots'] = RELEGATION_SLOTS
    # 消化率が低いうちは確率を断定しない
    d['confidence'] = 'low' if d['played'] < 380 * 0.25 else 'ok'
    with open(os.path.join(ROOT, 'data', 'j1.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f'[ok] 残留ライン 中央値{line["median"]}／9割安全圏{line["safe"]}  信頼度={d["confidence"]}')
    for r in d['standings'][:3] + d['standings'][-3:]:
        p = r['prob']
        print(f'   {r["rank"]:>2} {r["team"]:<8} 勝点{r["pts"]:>3} 最大{r["max"]:>3} '
              f'優勝{p["champ"]:>5.1f}% 降格{p["releg"]:>5.1f}%')
    return 0


if __name__ == '__main__':
    sys.exit(main())
