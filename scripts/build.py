#!/usr/bin/env python3
"""data/j1.json から index.html を生成する。"""
import json, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GA4 = 'G-2LM85GJN0L'


def esc(s):
    return html.escape(str(s), quote=True)


def md(iso):
    if not iso:
        return ''
    y, m, d = iso.split('-')
    return f'{int(m)}/{int(d)}'


def build(d):
    rows = d['standings']
    line, hist = d['line'], d['history']
    n = len(rows)
    releg = d['relegation_slots']
    safe_rank = n - releg               # 17位までが残留

    # 残留ラインまであと勝点いくつか
    def need(r):
        gap = line['median'] - r['pts']
        return max(0, gap)

    trs = ''
    for r in rows:
        p = r['prob']
        cls = 'r-releg' if r['rank'] > safe_rank else ('r-acl' if r['rank'] <= 3 else '')
        bar = min(100, max(0, p['releg']))
        trs += (
            f'<tr class="{cls}">'
            f'<td class="rk">{r["rank"]}</td>'
            f'<td class="tm">{esc(r["team"])}</td>'
            f'<td class="pt"><b>{r["pts"]}</b></td>'
            f'<td class="nm">{r["g"]}</td>'
            f'<td class="nm wide">{r["w"]}-{r["d"]}-{r["l"]}</td>'
            f'<td class="nm wide">{r["gd"]:+d}</td>'
            f'<td class="nm">{r["rest"]}</td>'
            f'<td class="nm mx">{r["max"]}</td>'
            f'<td class="pr"><span>{p["releg"]:.0f}%</span>'
            f'<i style="width:{bar:.0f}%"></i></td>'
            f'</tr>')

    hist_tr = ''.join(
        f'<tr><td>{h["season"]}</td><td>{h["clubs"]}クラブ</td>'
        f'<td><b>{h["line"]}</b></td><td>{esc(h["team"])}</td>'
        f'<td>{h["below"]}</td></tr>' for h in hist)

    warn = ''
    if d['confidence'] == 'low':
        warn = (f'<p class="warn">まだ{d["played"]}試合（全{d["played"]+d["pending"]}試合）'
                f'しか消化していません。降格確率は目安としてご覧ください。'
                f'試合が進むほど精度が上がります。</p>')

    return f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>J1残留ライン早見表｜降格ラインは勝点いくつ？2026-27｜無料・登録不要</title>
<meta name="description" content="明治安田J1リーグ2026-27の残留ライン（勝点）を公式データから毎日自動計算。20クラブ制の実際のラインは41〜43点で、よく見る「36点」は18クラブ時代の数字です。各クラブの降格確率・最大到達勝点もひと目でわかります。">
<meta name="theme-color" content="#ff8a3d">
<link rel="canonical" href="https://jleague.kkpwebninja.com/">
<!-- WEBNINJA_UNIFIED_FAVICON -->
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">

<meta property="og:title" content="J1残留ライン早見表｜降格ラインは勝点いくつ？">
<meta property="og:description" content="公式データから毎日自動計算。20クラブ制の残留ラインは41〜43点。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://jleague.kkpwebninja.com/">
<meta property="og:site_name" content="J1残留ライン早見表">
<meta name="twitter:card" content="summary_large_image">

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "J1残留ライン早見表",
  "url": "https://jleague.kkpwebninja.com/",
  "description": "明治安田J1リーグの残留ライン・降格確率を公式データから毎日自動計算します。",
  "applicationCategory": "UtilitiesApplication",
  "operatingSystem": "Web",
  "offers": {{"@type":"Offer","price":"0","priceCurrency":"JPY"}},
  "author": {{"@type":"Organization","name":"web忍者の砦"}}
}}
</script>

<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700;800&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fff8ef;--card:#fff;--ink:#33261a;--sub:#7a6551;--line:#f0dcc0;
  --accent:#ff8a3d;--deep:#e2620f;--danger:#e05252;--safe:#3d9970}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font-family:"M PLUS Rounded 1c",system-ui,-apple-system,sans-serif;line-height:1.7}}
header{{background:linear-gradient(160deg,#ff8a3d,#e2620f);color:#fff;padding:22px 16px 26px;text-align:center}}
h1{{margin:0 0 6px;font-size:21px;font-weight:900;line-height:1.4}}
.sub{{font-size:12.5px;opacity:.92}}
main{{max-width:760px;margin:0 auto;padding:16px 12px 40px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:16px;margin-bottom:14px}}
h2{{font-size:17px;font-weight:800;margin:0 0 4px;color:var(--deep)}}
.stamp{{font-size:11.5px;color:#9a8778;margin:0 0 12px}}
.hero{{text-align:center;padding:6px 0 2px}}
.hero .num{{font-size:60px;font-weight:900;color:var(--accent);line-height:1;letter-spacing:-.02em}}
.hero .unit{{font-size:22px;font-weight:900}}
.hero .lab{{font-size:13px;color:var(--sub);font-weight:700;margin-top:4px}}
.range{{display:flex;justify-content:center;gap:18px;margin-top:12px;flex-wrap:wrap}}
.range div{{font-size:12.5px;color:var(--sub)}}
.range b{{display:block;font-size:20px;color:var(--ink);font-weight:900}}
.warn{{font-size:12px;color:#9a4b00;background:#fff3e0;border-radius:8px;padding:9px 11px;margin:12px 0 0}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{background:#faf1e4;font-size:11.5px;color:var(--sub);padding:7px 3px;font-weight:700}}
td{{padding:8px 3px;border-bottom:1px solid #f6ece0;text-align:center}}
.tm{{text-align:left;font-weight:700;white-space:nowrap}}
.rk{{color:var(--sub);font-weight:700;width:2em}}
.pt b{{font-size:16px;color:var(--accent)}}
.nm{{font-variant-numeric:tabular-nums;color:var(--sub)}}
.mx{{font-weight:700;color:var(--ink)}}
.pr{{position:relative;min-width:66px}}
.pr span{{font-weight:700;font-size:12.5px}}
.pr i{{display:block;height:4px;background:var(--danger);border-radius:2px;margin-top:3px;opacity:.55}}
tr.r-releg{{background:#fdecea}}
tr.r-releg .pr span{{color:var(--danger)}}
tr.r-acl{{background:#eef7ee}}
.scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
@media (max-width:520px){{
  .wide{{display:none}}          /* 狭い画面では勝分負・得失を隠して主要列を読みやすく */
  td,th{{padding-left:2px;padding-right:2px}}
  .tm{{font-size:13.5px}}
}}
.note{{font-size:12px;color:var(--sub);line-height:1.8;margin:12px 0 0}}
footer{{text-align:center;font-size:11.5px;color:var(--sub);padding:20px 12px 30px}}
footer a{{color:#8a6a4a}}
</style>
<header>
  <h1>J1の残留ラインは勝点いくつ？</h1>
  <div class="sub">明治安田J1リーグ 2026-27／全{d['played']+d['pending'] and 38}節・下位{releg}クラブが自動降格</div>
</header>
<main>

<div class="card">
  <h2>今シーズンの残留ライン（推定）</h2>
  <p class="stamp">{md(d['as_of'])} 終了時点の成績で計算／{d['trials']:,}回シミュレーション</p>
  <div class="hero">
    <div><span class="num">{line['median']}</span><span class="unit">点</span></div>
    <div class="lab">17位（残留の最下位）の最終勝点の中央値</div>
  </div>
  <div class="range">
    <div>だいたいこの範囲<b>{line['p25']}〜{line['p75']}点</b></div>
    <div>9割方安全<b>{line['safe']}点</b></div>
  </div>
  {warn}
</div>

<div class="card">
  <h2>各クラブの状況</h2>
  <p class="stamp">最大到達＝残り試合を全勝した場合の勝点。まだ届くかどうかの根拠になります。</p>
  <div class="scroll">
  <table>
    <thead><tr><th>順</th><th>クラブ</th><th>勝点</th><th>試</th><th class="wide">勝分負</th>
    <th class="wide">得失</th><th>残</th><th>最大</th><th>降格</th></tr></thead>
    <tbody>{trs}</tbody>
  </table>
  </div>
  <p class="note">赤＝現在の降格圏（下位{releg}クラブ）／緑＝上位3クラブ。
  降格確率は残り{d['pending']}試合を{d['trials']:,}回シミュレーションし、下位{releg}位で終わった割合です。</p>
</div>

<div class="card">
  <h2>過去の残留ラインは何点だった？</h2>
  <p class="stamp">Jリーグ公式データから当サイトで算出</p>
  <div class="scroll">
  <table>
    <thead><tr><th>シーズン</th><th>形式</th><th>残留ライン</th><th>その順位のクラブ</th><th>降格圏最上位</th></tr></thead>
    <tbody>{hist_tr}</tbody>
  </table>
  </div>
  <p class="note"><b>「残留ラインは勝点36」という説明をよく見かけますが、これは18クラブ時代の数字です。</b>
  20クラブ・38節になった2024年以降は<b>41〜43点</b>が実際のラインでした。
  試合数が32から38に増えたぶん、必要な勝点も上がっています。</p>
</div>

<div class="card">
  <h2>この数字の出し方</h2>
  <p class="note">
  Jリーグ公式のデータサイトから全{d['played']+d['pending']}試合の日程と結果を取得し、
  消化済みの成績から各クラブの強さを推定して、残り試合を1試合ずつ{d['trials']:,}回シミュレーションしています。
  引分率は25.5%（2025年J1の全380試合の実測値）、ホームの勝率が高い分も織り込んでいます。<br>
  シーズン序盤は成績の差が偶然によるところも大きいため、強さの推定は平均へ寄せています。
  試合が進むほど実際の成績が反映され、精度が上がります。
  </p>
</div>

</main>
<footer>
  データ出典: <a href="https://data.j-league.or.jp/" target="_blank" rel="noopener">Jリーグ公式データサイト</a><br>
  当サイトは非公式のファンサイトです。正確な情報は公式サイトをご確認ください。
</footer>

<!-- WEBNINJA_UNIFIED_FOOTER -->
<footer style="text-align:center;padding:2rem 1rem 2.5rem;font-size:0.78rem;color:#94a3b8;line-height:2;border-top:1px solid #f0e6d2;margin-top:0;background:#fffcf7;">
  <div style="font-weight:800;color:#8b6b3d;font-size:0.85rem;margin-bottom:0.4rem;">web忍者の砦</div>
  <div>
    <a href="https://kkpwebninja.com/" target="_blank" rel="noopener" style="color:#8b6b3d;text-decoration:none;margin:0 0.5rem;">本丸トップ</a>·
    <a href="https://privacypolicy.kkpwebninja.com/" target="_blank" rel="noopener" style="color:#8b6b3d;text-decoration:none;margin:0 0.5rem;">プライバシーポリシー</a>·
    <a href="https://kkpwebninja.com/otoiawase" target="_blank" rel="noopener" style="color:#8b6b3d;text-decoration:none;margin:0 0.5rem;">お問い合わせ</a>·
    <a href="https://x.com/kkp_webninja" target="_blank" rel="noopener" style="color:#8b6b3d;text-decoration:none;margin:0 0.5rem;">@kkp_webninja</a>
  </div>
  <div style="margin-top:0.5rem;color:#bfa97a;">© 2025-2026 web忍者の砦</div>
</footer>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());gtag('config','{GA4}');</script>
'''


def main():
    with open(os.path.join(ROOT, 'data', 'j1.json'), encoding='utf-8') as f:
        d = json.load(f)
    out = build(d)
    with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'[ok] index.html  {len(out):,}文字')


if __name__ == '__main__':
    main()
