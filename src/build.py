# -*- coding: utf-8 -*-
"""サイトを docs/ に書き出すスクリプト。 実行: python3 src/build.py"""
import datetime
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import (KODOMO_CARD_URL, FORM_ENDPOINT, FOUNDED, HISTORY, AREA_INARS, AREA_PUBLIC, AREAS, EMAIL, EVENTS, INARS_COURSES, INARS_LIST_URL, INARS_WORKSHOPS, INARS_WS_LIST_URL, LINE_URL, ORG_NAME,
                     ORG_SHORT, PHOTOS, PLANS, REPORTS, REPORT_CATEGORIES, SITE_URL, SNS, VOLUNTEER_URL)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
STATIC = os.path.join(os.path.dirname(__file__), "static")
TODAY = datetime.date.today().isoformat()
WEEK = "月火水木金土日"

ARROW = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho+B1:wght@800'
         '&amp;family=Zen+Kaku+Gothic+New:wght@400;500;700&amp;display=swap">')

esc = html.escape
written = []  # sitemap 用


def jdate(iso, dots=False):
    d = datetime.date.fromisoformat(iso)
    if dots:
        return d.strftime("%Y.%m.%d")
    return f"{d.year}年{d.month}月{d.day}日（{WEEK[d.weekday()]}）"


def photo(key, alt, prefix, cls="", eager=False):
    f = PHOTOS.get(key)
    if f:
        load = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return f'<img class="photo {cls}" src="{prefix}assets/photos/{esc(f)}" alt="{esc(alt)}" {load}>'
    return f'<div class="ph {cls}" role="img" aria-label="{esc(alt)}（写真準備中）">［写真：{esc(alt)}］</div>'


ORG_LD = {
    "@context": "https://schema.org",
    "@type": "NGO",
    "name": ORG_NAME,
    "alternateName": "Japan Clinical Life Support Association",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/assets/logo.png",
    "email": EMAIL,
    "description": "岡山県備前市を拠点に、胸骨圧迫・AEDの救命講習（PUSHプロジェクト）と、医療従事者向けの急変回避研修（INARS）の開催支援を行う一般社団法人。",
    "address": {"@type": "PostalAddress", "addressRegion": "岡山県", "addressLocality": "備前市", "addressCountry": "JP"},
    "areaServed": ["岡山県", "愛媛県松山市", "中国地方", "四国地方", "日本"],
    "sameAs": list(SNS.values()),
}


def breadcrumb_ld(items):
    return {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + "/" + p}
            for i, (n, p) in enumerate(items)
        ],
    }


def header(prefix, current):
    items = [("about/", "協会について"), ("courses/", "救命講習会"), ("inars/", "INARSコース"), ("reports/", "活動報告"), ("support/", "ご支援")]
    cur = ' aria-current="page"'
    links = "".join(
        f'<a href="{prefix}{href}"{cur if current and "#" not in href and current == href.split("/")[0] else ""}>{label}</a>'
        for href, label in items)
    return f"""<a class="skip" href="#main">本文へ移動</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="{prefix}"><img src="{prefix}assets/logo.png" alt="" width="56" height="56"><span><small>一般社団法人</small><strong>{ORG_SHORT}</strong></span></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="メニューを開く">
<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
</button>
<nav class="nav" id="site-nav" aria-label="メインメニュー">{links}<a class="btn btn-primary" href="{prefix}contact/">お申し込み・ご相談</a></nav>
</div>
</header>"""


def footer(prefix):
    sns = "".join(f'<a href="{u}" rel="noopener">{n}</a>' for n, u in SNS.items())
    year = datetime.date.today().year
    return f"""<footer class="site-footer">
<div class="wrap">
<div class="footer-grid">
<div class="footer-org">
<img src="{prefix}assets/logo.png" alt="" width="84" height="84" loading="lazy">
<strong>一般社団法人<br>{ORG_SHORT}</strong>
<span>共に、命を守る力を。</span>
<span>所在地：岡山県備前市</span>
<span>救命講習会：{AREA_PUBLIC}</span>
<span>INARSコースの支援：{AREA_INARS}</span>
</div>
<div class="footer-col">
<h2>サイト</h2>
<a href="{prefix}about/">協会について</a><a href="{prefix}courses/">救命講習会</a><a href="{prefix}inars/">INARSコース</a><a href="{prefix}reports/">活動報告</a><a href="{prefix}contact/">お申し込み・お問い合わせ</a><a href="{prefix}support/">ご支援のお願い</a>
</div>
<div class="footer-col">
<h2>SNS</h2>{sns}
</div>
<div class="footer-col">
<h2>お問い合わせ</h2>
<a class="hl" href="mailto:{EMAIL}">{EMAIL}</a>
<a class="hl" href="{LINE_URL}" rel="noopener">LINE公式アカウント</a>
</div>
</div>
<p class="copy">© {year} {ORG_NAME}</p>
</div>
</footer>
<div class="mobile-cta" aria-label="お申し込みの近道">
<a href="{prefix}courses/#schedule">講習会の日程・申込</a>
<a href="{LINE_URL}" rel="noopener">LINEで相談</a>
</div>
<script>
(function(){{document.querySelectorAll('[data-copy]').forEach(function(btn){{btn.addEventListener('click',function(){{var t=btn.getAttribute('data-copy'),done=function(){{var o=btn.textContent;btn.textContent='コピーしました';setTimeout(function(){{btn.textContent=o;}},1800);}};if(navigator.clipboard){{navigator.clipboard.writeText(t).then(done,function(){{}});}}}});}});}})();
(function(){{var b=document.querySelector('.menu-btn'),n=document.getElementById('site-nav');if(!b||!n)return;
b.addEventListener('click',function(){{var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o);b.setAttribute('aria-label',o?'メニューを閉じる':'メニューを開く');}});
n.addEventListener('click',function(e){{if(e.target.tagName==='A'){{n.classList.remove('open');b.setAttribute('aria-expanded','false');}}}});}})();
</script>"""


def page(path, title, description, body, current="", ld=None, og_type="website", full_title=None):
    """path: 出力先（例 'about/'）。ディレクトリなら index.html を作る。"""
    depth = path.count("/")
    prefix = "../" * depth
    url = SITE_URL + "/" + path
    t = full_title or f"{title}｜{ORG_NAME}"
    lds = [ORG_LD] + (ld or [])
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    doc = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{ORG_NAME}">
<meta property="og:title" content="{esc(t)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F7F4EE">
<link rel="icon" href="{prefix}favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="{prefix}assets/style.css">
{ld_html}
</head>
<body>
{header(prefix, current)}
<main id="main">
{body(prefix)}
</main>
{footer(prefix)}
</body>
</html>
"""
    write(path, external_tabs(doc))
    written.append(path)


EXT_RE = re.compile(r'<a ([^>]*?)href="(https?://[^"]+)"([^>]*)>(.*?)</a>', re.S)


def external_tabs(doc):
    """外部サイトへのリンクは新しいタブで開く（申込フォームの入力中でも元のページが残るように）。"""
    def fix(m):
        before, url, after, inner = m.groups()
        if url.startswith(SITE_URL) or "target=" in before + after:
            return m.group(0)
        attrs = (before + after).replace('rel="noopener"', "").strip()
        attrs = (" " + " ".join(attrs.split())) if attrs else ""
        return f'<a href="{url}"{attrs} target="_blank" rel="noopener">{inner}<span class="sr-only">（新しいタブで開きます）</span></a>'
    return EXT_RE.sub(fix, doc)


def write(path, text):
    target = os.path.join(OUT, path, "index.html") if (path == "" or path.endswith("/")) else os.path.join(OUT, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)


def redirect(old_path, new_path):
    """旧Wix URL → 新URL の転送ページ。"""
    depth = old_path.strip("/").count("/") + 1
    rel = "../" * depth + new_path
    url = SITE_URL + "/" + new_path
    doc = f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>移動しました｜{ORG_NAME}</title>
<link rel="canonical" href="{url}"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={rel}">
<script>location.replace({json.dumps(rel)});</script></head>
<body><p>このページは移動しました。<a href="{rel}">新しいページへ</a></p></body></html>
"""
    write(old_path.strip("/") + "/", doc)


def section_head(eyebrow, title, right=""):
    return f'<div class="section-head"><div><span class="eyebrow">{eyebrow}</span><h2 class="h2">{title}</h2></div>{right}</div>'


def report_cards(prefix, items):
    out = []
    for r in items:
        out.append(f"""<a class="report-card" data-cat="{esc(r['tag'])}" href="{prefix}reports/{r['slug']}/">
{f'<img src="{prefix}assets/photos/{esc(r["photo"])}" alt="" loading="lazy">' if r.get('photo') else '<div class="ph" aria-hidden="true">［活動写真］</div>'}
<span class="date">{jdate(r['date'], True)}　<span class="tag">{esc(r['tag'])}</span></span>
<h3>{esc(r['title'])}</h3>
</a>""")
    return "".join(out)


def plans_html():
    out = []
    for p in PLANS:
        out.append(f"""<div class="plan{' plan-featured' if p['featured'] else ''}">
<div class="plan-top"><span class="pill">{p['time']}</span><span class="plan-note">{esc(p['note'])}</span></div>
<h3>{esc(p['name'])}</h3>
<p>{esc(p['text'])}</p>
<dl><div><dt>受講料</dt><dd>{esc(p['fee'])}</dd></div><div><dt>対象</dt><dd>{esc(p['target'])}</dd></div></dl>
</div>""")
    return "".join(out)


PROGRAMS = """<div class="grid-2" style="margin-top:24px">
<div class="program"><strong>PUSH<br>プロジェクト</strong><span>市民の方・学生向けの救命講習。胸骨圧迫とAEDで「最初の一歩」を。</span></div>
<div class="program"><strong>INARS<br>急変回避</strong><span>医療・介護・看護教育向け。心停止を未然に防ぐ臨床ライフサポート研修。</span></div>
</div>"""

reports_sorted = sorted(REPORTS, key=lambda r: r["date"], reverse=True)
for _r in REPORTS:
    if _r["tag"] not in REPORT_CATEGORIES:
        sys.exit(f"活動報告「{_r['title']}」の tag「{_r['tag']}」は REPORT_CATEGORIES にありません")


# ======================= pages =======================
def top(prefix):
    latest = reports_sorted[0]
    upcoming = sorted([e for e in EVENTS if e["date"] >= TODAY], key=lambda e: (e["date"], e.get("time", "")))
    if upcoming:
        u = upcoming[0]
        news_html = (f'<a class="news-item" href="{prefix}courses/"><span class="date">{jdate(u["date"], True)}</span>'
                     f'<span class="tag">講習会のお知らせ</span><span>{esc(u["title"].split("（")[0])}　{len(upcoming)}会場で開催予定</span></a>')
        news_more = f'<a class="more" href="{prefix}courses/">日程を見る →</a>'
    else:
        news_html = None
    inars_up = sorted([c for c in INARS_COURSES if c["date"] >= TODAY], key=lambda c: c["date"])

    def next_line(items, label):
        if not items:
            return '<span class="door-next">日程は準備中です</span>'
        d = datetime.date.fromisoformat(items[0]["date"])
        return (f'<span class="door-next">次回 <b>{d.month}/{d.day}（{WEEK[d.weekday()]}）</b>'
                f'{f"ほか{len(items) - 1}{label}" if len(items) > 1 else ""}</span>')

    doors = f"""<section class="section doors-section" aria-labelledby="doors-title">
<div class="wrap">
<div class="center" style="margin-bottom:40px"><span class="eyebrow">FIND YOUR COURSE</span><h2 class="h2" id="doors-title">目的からさがす</h2></div>
<div class="doors">
<a class="door" href="{prefix}courses/#schedule">
<span class="door-for">どなたでも・個人で</span>
<strong>講習会に参加したい</strong>
<span class="door-text">日程を選んで、各講習会の申込フォームから。市民向けの公開講習会は無料です。</span>
{next_line(upcoming, '会場')}
<span class="door-go">日程と申込方法 {ARROW}</span>
</a>
<a class="door" href="{prefix}contact/#request">
<span class="door-for">学校・企業・地域団体・スポーツチーム</span>
<strong>出張講習を依頼したい</strong>
<span class="door-text">人数・会場・時間に合わせて、90分または180分のプランでご提案します。</span>
<span class="door-next">メール・LINEで受付</span>
<span class="door-go">依頼のしかた {ARROW}</span>
</a>
<a class="door" href="{prefix}inars/#schedule">
<span class="door-for">医療従事者・看護教育</span>
<strong>INARSコースを受けたい</strong>
<span class="door-text">院内急変回避研修。お申し込みはMeCCSOの申込ページで受け付けています。</span>
{next_line(inars_up, 'コース')}
<span class="door-go">開催予定と申込 {ARROW}</span>
</a>
</div>
</div>
</section>"""
    return f"""
<section class="hero">
<div class="wrap">
<div class="hero-text">
<span class="eyebrow">岡山・備前市から　救命講習・AED講習</span>
<h1>救える命を、<br>救える社会に。</h1>
<p>現役の看護師・医師など医療の専門職が、胸骨圧迫とAEDの使い方、そして心停止を未然に防ぐ「急変回避（INARS）」の考え方を、わかりやすくお伝えします。</p>
<div class="hero-actions">
<a class="btn btn-primary" href="{prefix}courses/">講習会の日程を見る {ARROW}</a>
<a class="btn btn-outline" href="{prefix}contact/#request">出張講習を依頼する</a>
</div>
</div>
<div class="hero-media">{photo('hero', '胸骨圧迫とAEDの実技練習', prefix, eager=True)}</div>
</div>
</section>

<div class="wrap" style="padding-bottom:clamp(56px,7vw,88px)">
<div class="news">
<span class="news-label">お知らせ</span>
{news_html or f'<a class="news-item" href="{prefix}reports/{latest["slug"]}/"><span class="date">{jdate(latest["date"], True)}</span><span class="tag">{esc(latest["tag"])}</span><span>{esc(latest["title"])}</span></a>'}
{news_more if news_html else f'<a class="more" href="{prefix}reports/">一覧へ →</a>'}
</div>
</div>

{doors}

<section class="section section-navy">
<div class="wrap split">
<div><span class="eyebrow">WHY IT MATTERS</span><h2 class="h2">一歩を踏み出す勇気と、<br>命をつなぐ仕組みを。</h2></div>
<div>
<p>日本では毎年、多くの人が病院の外で突然の心停止に陥っています。救急車が到着するまでのわずか数分間、その場に居合わせた人が何もできなければ、救えるはずの命も救えなくなってしまいます。</p>
<p>しかし、誰かが一歩を踏み出し、胸骨圧迫を行い、AED（自動体外式除細動器）を使うことができれば、救命の可能性は大きく高まります。心停止はいつ、どこで、誰に起こるかわかりません。少しの知識と勇気が、大切な命を救う鍵になります。</p>
</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="center" style="margin-bottom:48px"><span class="eyebrow">OUR STRENGTHS</span><h2 class="h2">当協会の強み</h2></div>
<div class="grid-3">
<div class="card">{photo('strength-1', '講習会の様子', prefix, 'card-photo')}<span class="num">01</span><h3>医療・看護のプロによる<br>確かな指導</h3><p>医療の最前線を知る看護師や専門スタッフが直接指導。マニュアルにとどまらない、現場で「本当に使える」知識と技術が身につきます。</p></div>
<div class="card">{photo('strength-2', '講習会の様子', prefix, 'card-photo')}<span class="num">02</span><h3>「一歩を踏み出す」ための<br>心理的サポート</h3><p>「怖い」「間違えたらどうしよう」という不安に寄り添い、誰でも迷わず動けるようになるための丁寧なカリキュラム（PUSHプログラム等）を重視しています。</p></div>
<div class="card">{photo('strength-3', '講習会の様子', prefix, 'card-photo')}<span class="num">03</span><h3>地域に根ざし、<br>全国へ広がる活動</h3><p>岡山県備前市を拠点に、県内各地と愛媛県松山市で救命講習会を開催。医療従事者向けのINARSコースも、中国・四国を中心に各地で開催を支援しています。</p></div>
</div>
</div>
</section>

<section class="section section-sand">
<div class="wrap">
{section_head('COURSES', '講習プラン', '<p class="lead">学校・企業・地域団体・スポーツチームなどへの出張講習も承ります。人数や会場に合わせてご相談ください。</p>')}
<div class="grid-2">{plans_html()}</div>
{PROGRAMS}
<p style="margin-top:32px"><a class="more" href="{prefix}courses/">講習会案内を見る →</a></p>
</div>
</section>

<section class="section">
<div class="wrap">
{section_head('ACTIVITY', '活動報告', f'<a class="more" href="{prefix}reports/">すべての活動報告を見る →</a>')}
<div class="grid-3">{report_cards(prefix, reports_sorted[:3])}</div>
</div>
</section>

{message_section(prefix)}

{donate_band(prefix)}
"""


def message_section(prefix):
    return f"""<section class="section section-paper" id="message">
<div class="wrap message">
<div class="message-photo">{photo('representative', '代表理事 浅越博之', prefix) if PHOTOS.get('representative') else f'<div class="message-panel"><img src="{prefix}assets/logo.png" alt="" width="160" height="160" loading="lazy"><p>救える命を、<br>救える社会に。</p></div>'}</div>
<div class="message-body">
<span class="eyebrow">MESSAGE</span>
<h2 class="h2">地域の「最初の一歩」が、<br>命を次へつなぐ。</h2>
<p>私は看護師として医療の最前線に立ち、命の危機に直面する現場を数多く経験してきました。その中で痛感したのは、医療機関にバトンが引き継がれる前――つまり「地域社会でのファーストステップ（初期対応）」がいかに重要かということです。</p>
<p>医療従事者だけでなく、市民の方々、学校、地域コミュニティの誰もが、いざという時に迷わず動ける社会をつくりたい。その想いから、市民向けの「PUSHプロジェクト」や、医療従事者・看護教育のための「INARS」を通じて、実践的な救命スキルの普及とインストラクターの育成に力を注いでいます。</p>
<p>これからも皆様のご理解とご協力をいただきながら、地域の安全と安心のために全力を注いでまいります。</p>
<div class="signature"><small>代表理事</small><strong>浅越 博之</strong></div>
</div>
</div>
</section>"""


def donate_band(prefix):
    return f"""<section class="donate" id="donate-band">
<div class="wrap">
<div><h2>ご支援のお願い</h2><p>私たちの活動は、皆様の温かいご支援によって支えられています。ご寄付・賛助会員・基金の3つの方法で、活動を応援していただけます。</p></div>
<a class="btn btn-light" href="{prefix}support/">ご支援の方法を見る</a>
</div>
</section>"""


def about(prefix):
    blocks = [
        ("push", "救命講習の普及・啓発（PUSHプロジェクト）", "市民の方・学生・企業・スポーツチーム向け",
         "「人が倒れたとき、自分にできること」をシンプルに学ぶ講習会です。胸骨圧迫（心臓マッサージ）とAEDの使い方を中心に、学校、企業、地域コミュニティへ出向いて出張講習を行っています。"),
        ("inars", "院内急変回避研修（INARSコース）の開催支援", "医療従事者・看護教育の現場向け",
         "INARSコースは、入院患者さんのわずかなサインを察知し、急変（心停止など）を未然に回避するための初期対応（ファーストアクション）を学ぶ、医療従事者向けのシミュレーション研修です。当協会は「中四国INARSコース」をはじめ、各地のコースの開催を支援しています。"),
        ("volunteer", "地域社会の安全対策・ボランティア活動", "地域イベント・スポーツ大会",
         "地域のマラソン大会をはじめとするスポーツイベント等での救護・AEDチームとしての協力や、地域イベントでの安全対策ワークショップの開催など、街全体の安全を守る活動に貢献しています。"),
    ]
    b = "".join(f"""<div class="biz">
<div class="biz-media">{photo(k, t, prefix)}</div>
<div class="biz-body"><span class="biz-for">{f}</span><h2>{t}</h2><p>{x}</p></div>
</div>""" for k, t, f, x in blocks)
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ 協会について</p>
<h1>協会について</h1>
<p class="lead">市民向けから医療従事者向けまで、それぞれのレベルに合わせた実践的な救命・ライフサポート研修を展開しています。</p>
<nav class="page-index" aria-label="このページの内容"><a href="#message">代表理事あいさつ</a><a href="#business">事業内容</a><a href="#profile">協会概要・沿革</a></nav>
</div></section>
{message_section(prefix)}
<section class="section" id="business"><div class="wrap">
{section_head('BUSINESS', '事業内容')}
{b}</div></section>
<section class="section section-paper" id="profile"><div class="wrap">
<div class="split" style="color:inherit">
<div>
<span class="eyebrow">PROFILE</span><h2 class="h2">協会概要</h2>
<table class="info-table" style="margin-top:28px">
<tr><th>名称</th><td>{ORG_NAME}</td></tr>
<tr><th>設立</th><td>{FOUNDED}<br><span style="font-size:14px;color:var(--muted)">（活動開始は2013年）</span></td></tr>
<tr><th>代表理事</th><td>浅越 博之</td></tr>
<tr><th>所在地</th><td>岡山県備前市</td></tr>
<tr><th>活動地域</th><td>救命講習会：{AREA_PUBLIC}<br>INARSコースの支援：{AREA_INARS}</td></tr>
<tr><th>連絡先</th><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr>
</table>
</div>
<div style="color:var(--ink)">
<span class="eyebrow">HISTORY</span><h2 class="h2" style="margin-bottom:28px">沿革</h2>
<ol class="history">{''.join(f'<li><span class="history-year">{esc(y)}</span><p>{esc(t)}</p></li>' for y, t in HISTORY)}</ol>
</div>
</div>
</div></section>
{donate_band(prefix)}"""


def event_html(e, past):
    d = datetime.date.fromisoformat(e["date"])
    apply = ""
    if not past and e.get("apply"):
        vol = e.get("volunteer", VOLUNTEER_URL)
        apply = (f'<p class="event-actions"><a class="btn btn-primary" href="{e["apply"]}" rel="noopener">受講を申し込む {ARROW}</a>'
                 f'<a class="btn btn-outline" href="{vol}" rel="noopener">ボランティアで参加する</a></p>')
    fee = f"　参加費：{esc(e['fee'])}" if e.get("fee") and not past else ""
    if not past and not e.get("apply") and e.get("apply_note"):
        apply = f'<p class="place" style="margin-top:8px">{esc(e["apply_note"])}</p>'
    if past:
        status = '<span class="status status-done">終了</span>'
    elif e.get("apply"):
        status = '<span class="status status-open">受付中</span>'
    else:
        status = '<span class="status status-soon">受付準備中</span>'
    return f"""<article class="event{' event-past' if past else ''}">
<time datetime="{e['date']}">{d.month}/{d.day}<small>{d.year}年（{WEEK[d.weekday()]}）<br>{esc(e.get('time', ''))}</small></time>
<div>{status}<h3>{esc(e['title'])}</h3><p>{esc(e['text'])}</p><p class="place">会場：{esc(e['place'])}{fee}</p>{apply}</div>
</article>"""


def ld_dates(date, time):
    """「13:00〜18:30」から startDate / endDate を作る（終了時刻がなければ開始と同日）"""
    parts = [p.strip().zfill(5) if p.strip() else "" for p in (time or "").split("〜")]
    start = parts[0] if parts and parts[0] else "00:00"
    d = {"startDate": f"{date}T{start}:00+09:00"}
    d["endDate"] = f"{date}T{parts[1]}:00+09:00" if len(parts) > 1 and parts[1] else d["startDate"]
    return d


def courses_ld():
    out = []
    for e in EVENTS:
        if e["date"] < TODAY:
            continue
        out.append({
            "@context": "https://schema.org", "@type": "Event", "name": e["title"],
            **ld_dates(e["date"], e.get("time")),
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "Place", "name": e["place"], "address": e["place"]},
            "description": e["text"],
            "image": [SITE_URL + "/assets/og.png"],
            "organizer": {"@type": "Organization", "name": ORG_NAME, "url": SITE_URL + "/"},
            "performer": {"@type": "Organization", "name": ORG_NAME},
        })
    return out


FAQ = [
    ("医療の知識がなくても参加できますか？",
     "はい。はじめての方を対象に、看護師など医療の専門職が基本から指導します。"),
    ("参加費はかかりますか？",
     "講習会ごとに「開催予定の講習会」に記載しています。市民向けの公開講習会は無料で開催しています。"),
    ("服装や持ち物は？",
     "動きやすい服装でお越しください。"),
    ("修了証はもらえますか？",
     "受講修了証を交付している講習会があります。各講習会の案内をご確認ください。"),
    ("職場や学校、チームで受けたいのですが。",
     '出張講習を承ります。<a href="{p}contact/#request">出張講習のご依頼</a>から、ご希望の日時・人数・会場をお知らせください。'),
]


def faq_html(prefix):
    return "".join(f'<details><summary>{esc(q)}</summary><p>{a.format(p=prefix)}</p></details>' for q, a in FAQ)


def faq_ld():
    import re
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in FAQ]}


VOLUNTEER_BAND = f"""<section class="section section-navy" id="volunteer"><div class="wrap split">
<div><span class="eyebrow">VOLUNTEER</span><h2 class="h2">講習会の<br>ボランティア募集</h2></div>
<div>
<p>当協会の講習会は、毎回ボランティアの皆さんと一緒に運営しています。ボランティア活動に取り組む方も応援しています。講習会当日の運営や、会場の準備・片付けなどをお手伝いいただいた方には、「ボランティア実績証」を発行します。</p>
<p>学生の方の進学・就職活動や、地域活動の実績づくりにもお役立てください。</p>
<p><a class="btn btn-light" href="{VOLUNTEER_URL}" rel="noopener">ボランティアに申し込む <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a></p>
</div>
</div></section>"""


def courses(prefix):
    upcoming = sorted([e for e in EVENTS if e["date"] >= TODAY], key=lambda e: (e["date"], e.get("time", "")))
    past = sorted([e for e in EVENTS if e["date"] < TODAY], key=lambda e: (e["date"], e.get("time", "")), reverse=True)
    up_html = "".join(event_html(e, False) for e in upcoming) or (
        f'<p class="empty">現在、受付中の講習会はありません。<br>新しい日程は、このページと<a href="{LINE_URL}" rel="noopener">LINE公式アカウント</a>・Instagramでお知らせします。</p>')
    def rec(e):
        d = datetime.date.fromisoformat(e["date"])
        rep = f'<a href="{prefix}reports/{e["report"]}/">開催報告</a>' if e.get("report") else '<span class="none">—</span>'
        return (f'<tr><td class="num">{d.year}.{d.month:02d}.{d.day:02d}</td><td>{esc(e["title"])}</td>'
                f'<td>{esc(e["place"])}</td><td>{rep}</td></tr>')
    past_html = "".join(rec(e) for e in past)
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ 救命講習会</p>
<h1>救命講習会</h1>
<p class="lead">どなたでも参加できる救命講習会（胸骨圧迫・AED・窒息への対応など）の日程と、学校・企業・地域団体向けの出張講習のご案内です。医療従事者向けの研修は<a href="{prefix}inars/">INARSコース</a>をご覧ください。</p>
</div></section>

<section class="section" id="schedule"><div class="wrap">
{section_head('SCHEDULE', '開催予定の講習会')}
<ol class="steps" aria-label="参加までの流れ">
<li><b>1</b><span>下の一覧から、参加したい日程・会場を選ぶ</span></li>
<li><b>2</b><span>「受講を申し込む」または「ボランティアで参加する」から、フォームに入力する</span></li>
<li><b>3</b><span>当日、会場へ。動きやすい服装でお越しください</span></li>
</ol>
<div class="events">{up_html}</div>
<p style="margin-top:20px;font-size:14px;color:var(--muted)">「受付準備中」の講習会は、申込方法が決まり次第このページと<a href="{LINE_URL}" rel="noopener">LINE公式アカウント</a>でお知らせします。</p>
</div></section>

{VOLUNTEER_BAND}

<section class="section section-sand"><div class="wrap">
{section_head('COURSES', '講習プラン', '<p class="lead">学校・企業・地域団体・スポーツチームなどへの出張講習も承ります。人数や会場に合わせてご相談ください。</p>')}
<div class="grid-2">{plans_html()}</div>
{PROGRAMS}
</div></section>

<section class="section section-paper"><div class="wrap">
{section_head('REQUEST', '出張講習のご依頼方法')}
<div class="grid-3">
<div class="card"><span class="num">1</span><h3>お問い合わせ</h3><p>メールまたはLINEで、ご希望の日時・人数・会場・対象の方（年齢や職種）をお知らせください。</p></div>
<div class="card"><span class="num">2</span><h3>内容のご相談</h3><p>目的や時間に合わせて、プランと講習内容をご提案します。資器材は当協会でご用意します。</p></div>
<div class="card"><span class="num">3</span><h3>講習当日</h3><p>医療の専門職が伺い、実技中心で指導します。受講後の修了証の発行もご相談ください。</p></div>
</div>
<p style="margin-top:32px"><a class="btn btn-primary" href="{prefix}contact/#request">講習を依頼する {ARROW}</a></p>
</div></section>

<section class="section"><div class="wrap" style="max-width:calc(860px + var(--gutter)*2)">
{section_head('FAQ', 'よくあるご質問')}
<div class="faq">{faq_html(prefix)}</div>
</div></section>

<section class="section"><div class="wrap">
{section_head('RECORD', '開催実績', f'<a class="more" href="{prefix}reports/">活動報告を見る →</a>')}
<figure class="wide-photo" style="margin:0 0 32px">{photo('courses', '赤磐医師会病院での市民向け救命講習会', prefix)}</figure>
<div class="table-scroll"><table class="record">
<thead><tr><th>開催日</th><th>講習会</th><th>会場</th><th>報告</th></tr></thead>
<tbody>{past_html}</tbody>
</table></div>
</div></section>"""


def reports_index(prefix):
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ 活動報告</p>
<h1>活動報告</h1>
<p class="lead">講習会の開催報告やお知らせを掲載しています。</p>
</div></section>
<section class="section"><div class="wrap">{report_filter()}<div class="grid-3" id="report-list">{report_cards(prefix, reports_sorted)}</div></div></section>"""


def report_filter():
    used = [c for c in REPORT_CATEGORIES if any(r["tag"] == c for r in REPORTS)]
    if len(used) < 2:
        return ""
    btns = '<button type="button" class="chip" aria-pressed="true" data-filter="">すべて</button>' + "".join(
        f'<button type="button" class="chip" aria-pressed="false" data-filter="{esc(c)}">{esc(c)}</button>' for c in used)
    return f"""<div class="chips" role="group" aria-label="カテゴリーで絞り込む">{btns}</div>
<script>
document.addEventListener('DOMContentLoaded',function(){{var bs=document.querySelectorAll('.chip'),cs=document.querySelectorAll('#report-list .report-card');
bs.forEach(function(b){{b.addEventListener('click',function(){{var f=b.getAttribute('data-filter');
bs.forEach(function(x){{x.setAttribute('aria-pressed',x===b?'true':'false');}});
cs.forEach(function(c){{c.hidden=!!f&&c.getAttribute('data-cat')!==f;}});}});}});}});
</script>"""


def report_page(r, i):
    newer = reports_sorted[i - 1] if i > 0 else None
    older = reports_sorted[i + 1] if i + 1 < len(reports_sorted) else None

    def body(prefix):
        nav = []
        nav.append(f'<a href="{prefix}reports/{older["slug"]}/">← {esc(older["title"])}</a>' if older else "<span></span>")
        nav.append(f'<a href="{prefix}reports/{newer["slug"]}/">{esc(newer["title"])} →</a>' if newer else f'<a href="{prefix}reports/">活動報告一覧へ</a>')
        return f"""<section class="page-hero"><div class="wrap" style="max-width:calc(760px + var(--gutter)*2)">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ <a href="{prefix}reports/">活動報告</a></p>
<div class="article-meta"><time class="date" datetime="{r['date']}">{jdate(r['date'], True)}</time><span class="tag">{esc(r['tag'])}</span></div>
<h1 style="font-size:clamp(26px,3.4vw,40px)">{esc(r['title'])}</h1>
</div></section>
<section class="section" style="padding-top:48px"><div class="wrap">
<article class="prose">{f'<figure><img class="photo" src="{prefix}assets/photos/{esc(r["photo"])}" alt="" fetchpriority="high"></figure>' if r.get('photo') else ''}{r['body']}</article>
<nav class="article-nav" aria-label="前後の記事">{''.join(nav)}</nav>
</div></section>"""

    ld = [{
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": r["title"],
        "datePublished": r["date"], "description": r["excerpt"],
        "author": {"@type": "Organization", "name": ORG_NAME},
        "publisher": {"@type": "Organization", "name": ORG_NAME, "logo": {"@type": "ImageObject", "url": SITE_URL + "/assets/logo.png"}},
        "mainEntityOfPage": SITE_URL + f"/reports/{r['slug']}/", "image": SITE_URL + "/assets/og.png",
    }, breadcrumb_ld([("トップ", ""), ("活動報告", "reports/"), (r["title"], f"reports/{r['slug']}/")])]
    page(f"reports/{r['slug']}/", r["title"], r["excerpt"], body, "reports", ld, og_type="article")


CONTACT_TOPICS = ["出張講習・院内開催のご依頼", "講習会についてのご質問", "ご寄付・賛助会員について", "その他（取材など）"]
SUPPORT_TOPIC = "ご寄付・賛助会員について"


def contact_form():
    """お問い合わせフォーム。FORM_ENDPOINT（Google Apps Script）が空なら何も出さない。"""
    if not FORM_ENDPOINT:
        return ""
    opts = "".join(f'<option>{esc(t)}</option>' for t in CONTACT_TOPICS)
    return f"""<section class="section" id="form"><div class="wrap">
<div class="form-layout">
<div>
<span class="eyebrow">FORM</span><h2 class="h2">お問い合わせフォーム</h2>
<p style="margin-top:16px;color:var(--ink-2)">ご用件を選んで、わかる範囲でご記入ください。内容を確認し、ご入力のメールアドレスへ折り返しご連絡します。</p>
<p class="hint" style="margin-top:12px">返信には数日いただくことがあります。お急ぎの場合はLINEでご連絡ください。</p>
</div>
<form class="cform" id="cform" novalidate>
<label><span class="lbl">ご用件<span class="req">必須</span></span>
<select name="topic" id="cf-topic">{opts}</select></label>
<label><span class="lbl">団体名・学校名<span class="opt">任意</span></span><input name="org" type="text" autocomplete="organization"></label>
<div class="row2">
<label><span class="lbl">お名前<span class="req">必須</span></span><input name="name" type="text" autocomplete="name" required></label>
<label><span class="lbl">お電話番号<span class="opt">任意</span></span><input name="tel" type="tel" inputmode="tel" autocomplete="tel"></label>
</div>
<label><span class="lbl">メールアドレス<span class="req">必須</span></span><input name="email" type="email" inputmode="email" autocomplete="email" required></label>
<div id="cf-request" class="cf-group">
<label><span class="lbl">ご希望の日時（候補を2〜3つ）</span><input name="dates" type="text" placeholder="例：12月の平日午後、1月10日（土）午前"></label>
<div class="row2">
<label><span class="lbl">受講人数・対象の方</span><input name="people" type="text" placeholder="例：教職員30名"></label>
<label><span class="lbl">会場（住所）</span><input name="place" type="text" placeholder="例：〇〇小学校 体育館"></label>
</div>
</div>
<label><span class="lbl">お問い合わせ内容<span class="req">必須</span></span><textarea name="message" rows="5" required placeholder="ご要望やご質問をご記入ください"></textarea></label>
<input class="hp" name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="agree"><input name="agree" type="checkbox" required>入力した情報を、お問い合わせへの回答のためにのみ使うことに同意します</label>
<button class="btn btn-primary" type="submit" id="cf-send">送信する</button>
<p class="cf-msg" id="cf-msg" role="status" aria-live="polite"></p>
</form>
</div>
</div></section>
<script>
(function(){{var f=document.getElementById('cform');if(!f)return;
var t=document.getElementById('cf-topic'),g=document.getElementById('cf-request'),m=document.getElementById('cf-msg'),b=document.getElementById('cf-send');
var p=new URLSearchParams(location.search).get('topic');if(p&&[].some.call(t.options,function(o){{return o.text===p;}}))t.value=p;
function sw(){{g.hidden=t.selectedIndex!==0;}}t.addEventListener('change',sw);sw();
f.addEventListener('submit',function(e){{e.preventDefault();m.className='cf-msg';
if(!f.name.value.trim()||!f.message.value.trim()){{m.textContent='お名前とお問い合わせ内容をご記入ください。';m.classList.add('err');return;}}
if(!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(f.email.value.trim())){{m.textContent='メールアドレスをご確認ください。';m.classList.add('err');return;}}
if(!f.agree.checked){{m.textContent='情報の取り扱いへの同意にチェックを入れてください。';m.classList.add('err');return;}}
b.disabled=true;b.textContent='送信しています…';
fetch({json.dumps(FORM_ENDPOINT)},{{method:'POST',mode:'no-cors',body:new URLSearchParams(new FormData(f))}})
.then(function(){{f.reset();sw();m.textContent='送信しました。ありがとうございます。内容を確認し、折り返しご連絡します。';m.classList.add('ok');}})
.catch(function(){{m.textContent='送信できませんでした。お手数ですが、メールかLINEでご連絡ください。';m.classList.add('err');}})
.then(function(){{b.disabled=false;b.textContent='送信する';}});}});}})();
</script>"""


def contact(prefix):
    from urllib.parse import quote
    subj_req = quote("講習のご依頼")
    subj_don = quote("ご寄付について")
    has_form = bool(FORM_ENDPOINT)
    req_door = ("下のフォームか、メール・LINEでご連絡ください。" if has_form
                else "下の「ご依頼の方法」をご覧のうえ、メールかLINEでご連絡ください。")
    req_href = "#form" if has_form else "#request"
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ お申し込み・お問い合わせ</p>
<h1>お申し込み・お問い合わせ</h1>
<p class="lead">ご用件に合わせて、いちばん近い窓口をお選びください。</p>
</div></section>

<section class="section" style="padding-bottom:0"><div class="wrap">
<div class="doors doors-4">
<a class="door" href="{prefix}courses/#schedule"><span class="door-for">どなたでも・個人で</span><strong>講習会に参加したい</strong><span class="door-text">開催予定の一覧から日程を選び、各講習会の申込フォームからお申し込みください。</span><span class="door-go">日程と申込方法 {ARROW}</span></a>
<a class="door" href="{req_href}"><span class="door-for">学校・企業・団体・病院</span><strong>出張講習・院内開催を依頼したい</strong><span class="door-text">{req_door}</span><span class="door-go">ご依頼の方法 {ARROW}</span></a>
<a class="door" href="{prefix}inars/#schedule"><span class="door-for">医療従事者・看護教育</span><strong>INARSコースを受けたい</strong><span class="door-text">各コースの申込はMeCCSOの申込ページで受け付けています。</span><span class="door-go">開催予定と申込 {ARROW}</span></a>
<a class="door" href="{VOLUNTEER_URL}" rel="noopener"><span class="door-for">講習会を一緒に支えたい方</span><strong>ボランティアに参加したい</strong><span class="door-text">講習会当日の運営や準備・片付けのお手伝いです。ボランティア実績証を発行します。</span><span class="door-go">募集フォームへ {ARROW}</span></a>
</div>
</div></section>
{contact_form()}
<section class="section" id="request"><div class="wrap">
<div class="request">
<div>
<span class="eyebrow">REQUEST</span><h2 class="h2">出張講習・院内開催のご依頼</h2>
<p style="margin-top:16px;color:var(--ink-2)">次の項目をお知らせいただくと、プランと費用のご提案がスムーズです。わかる範囲で構いません。</p>
<ul class="checklist">
<li>団体名・ご担当者名・連絡先</li>
<li>ご希望の日時（候補を2〜3つ）</li>
<li>受講人数と、対象の方（年齢・職種など）</li>
<li>会場（住所）と、床に座れるスペースの有無</li>
<li>ご希望の時間（90分／180分）やご要望</li>
</ul>
</div>
<div class="contact-stack">
<div class="contact-card">
<h3>メールで依頼する</h3>
<p class="mail-line"><span class="mail">{EMAIL}</span><button class="copy-btn" type="button" data-copy="{EMAIL}">コピー</button></p>
<a class="btn btn-primary" href="mailto:{EMAIL}?subject={subj_req}">メールアプリを開く</a>
<p class="hint">メールアプリが開かないときは、アドレスをコピーしてお使いください。</p>
</div>
<div class="contact-card">
<h3>LINEで相談する</h3>
<p>日程の空きや、ちょっとした質問もお気軽にどうぞ。</p>
<a class="btn btn-outline" href="{LINE_URL}" rel="noopener">LINE公式アカウントを開く</a>
</div>
</div>
</div>
</div></section>

<section class="section section-sand" id="donate"><div class="wrap prose" style="max-width:860px">
<h2 style="margin-top:0">ご寄付・賛助会員について</h2>
<p>ご寄付・賛助会員・基金によるご支援の方法は、「ご支援のお願い」のページにまとめています。</p>
<p><a class="btn btn-primary" href="{prefix}support/">ご支援のお願いを見る {ARROW}</a></p>
</div></section>"""


def support(prefix):
    from urllib.parse import quote
    m_don = quote("ご寄付について")
    m_mem = quote("賛助会員の入会について")
    m_fund = quote("基金について")
    m_kodomo = quote("こども救命教育募金について")
    if KODOMO_CARD_URL:
        card_btn = f'<a class="btn btn-primary" href="{KODOMO_CARD_URL}" target="_blank" rel="noopener">クレジットカードで寄付する</a>'
    else:
        card_btn = '<span class="btn btn-outline" aria-disabled="true" style="opacity:.6;cursor:default">クレジットカードでの寄付（準備中）</span>'
    def mail_btn(subj, label):
        if FORM_ENDPOINT:  # フォームがあるときは、ご支援の用件を選んだ状態のフォームへ
            return f'<a class="btn btn-primary" href="{prefix}contact/?topic={quote(SUPPORT_TOPIC)}#form">{label.replace("メールする", "問い合わせる").replace("相談する", "問い合わせる")}</a>'
        return f'<a class="btn btn-primary" href="mailto:{EMAIL}?subject={subj}">{label}</a>'
    bank = f"""<table class="info-table bank">
<tr><th colspan="2">三井住友銀行</th></tr>
<tr><td>支店</td><td>トランクNORTH支店（店番号 403）</td></tr>
<tr><td>口座</td><td>普通預金　口座番号 0724022</td></tr>
<tr><td>口座名義</td><td>シャ）ニホンリンショウライフサポートキョウカイ</td></tr>
</table>
<table class="info-table bank">
<tr><th colspan="2">ゆうちょ銀行</th></tr>
<tr><td>ゆうちょ銀行から</td><td>記号 15460　番号 40142831</td></tr>
<tr><td>他の金融機関から</td><td>店名 五四八（ゴヨンハチ）　店番 548<br>普通預金　口座番号 4014283</td></tr>
<tr><td>口座名義</td><td>シャ）ニホンリンショウライフサポートキョウカイ</td></tr>
</table>"""
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ ご支援のお願い</p>
<h1>ご支援のお願い</h1>
<p class="lead">救える人を地域に一人でも増やす活動を続けるために、皆さまのご支援をお願いいたします。ご支援の方法は「ご寄付」「賛助会員」「基金」の3つです。</p>
{f'<p style="margin-top:20px"><a class="btn btn-primary" href="{KODOMO_CARD_URL}" target="_blank" rel="noopener">クレジットカードで寄付する</a></p>' if KODOMO_CARD_URL else ''}
<nav class="page-index" aria-label="このページの内容"><a href="#donation">ご寄付</a><a href="#kodomo">こども救命教育募金</a><a href="#member">賛助会員</a><a href="#fund">基金</a></nav>
</div></section>

<section class="section"><div class="wrap">
<div class="table-scroll"><table class="record compare">
<thead><tr><th>方法</th><th>支援の形</th><th>金額</th><th>お金の返還</th><th>こんな方に</th></tr></thead>
<tbody>
<tr><td><a href="#donation"><b>ご寄付</b></a></td><td>1回ごとのご支援</td><td>自由</td><td>返還しません</td><td>気軽に一度応援したい方</td></tr>
<tr><td><a href="#kodomo"><b>こども救命教育募金</b></a></td><td>子ども向け救命教育に使い道を限ったご寄付</td><td>2,500円から目安あり</td><td>返還しません</td><td>子どもたちに救命を届けたい方</td></tr>
<tr><td><a href="#member"><b>賛助会員</b></a></td><td>年会費による継続的なご支援</td><td>個人：入会金5,000円＋年会費1口5,000円<br>団体・法人：入会金10,000円＋年会費1口10,000円</td><td>返還しません</td><td>継続して支えたい個人・病院・企業の方</td></tr>
<tr><td><a href="#fund"><b>基金</b></a></td><td>活動の土台となる資金をお預かり</td><td>募集のたびにお知らせ</td><td>協会の解散時に返還（利息なし）</td><td>まとまった資金で活動を支えたい方</td></tr>
</tbody></table></div>
<p style="margin-top:16px;font-size:14px;color:var(--muted)">いずれのご支援も、税制上の寄付金控除の対象にはなりませんのでご了承ください。</p>
</div></section>

<section class="section section-paper" id="donation"><div class="wrap prose" style="max-width:860px">
<h2 style="margin-top:0">ご寄付</h2>
<p>金額にかかわらず、1回ごとのご支援を受け付けています。いただいたご寄付は、次のような活動に大切に使わせていただきます。</p>
<ul>
<li>講習用の訓練人形・AEDトレーナーの購入と更新</li>
<li>学校や地域での無料講習会の開催</li>
<li>講習の指導者（インストラクター）の育成</li>
<li>教材・資料の作成</li>
</ul>
<h3>お振込先</h3>
{bank}
<p>お振込みのあと、お名前とご連絡先を {EMAIL} までお知らせください。お礼のご連絡をいたします。領収書が必要な方はその旨もお書き添えください。振込手数料はご負担をお願いいたします。</p>
{'<p>クレジットカードでのご寄付は、<a href="#kodomo">こども救命教育募金</a>で受け付けています。</p>' if KODOMO_CARD_URL else ''}
<p>{mail_btn(m_don, "寄付についてメールする")}</p>
</div></section>

<section class="section" id="kodomo"><div class="wrap prose" style="max-width:860px">
<h2 style="margin-top:0">こども救命教育募金</h2>
<p class="lead" style="margin-top:0">子どもたちに「命をつなぐ力」を届けるために</p>
<p>学校や地域の子どもたちに、救命講習を無料で届けるための募金です。使い道を子ども向けの救命教育に限ったご寄付として、ほかのお金と分けて管理します。</p>
<h3>なぜ子どもたちに届けたいのか</h3>
<p>突然の心停止は、学校でも、家庭でも、通学路でも起こります。救急車が着くまでの数分間、そばにいる人が胸骨圧迫とAEDを行えるかどうかが、命を左右します。子どものうちに救命を学んだ経験は一生の力になり、学んだ子どもたちが家族に伝えることで、地域の「助けられる人」が増えていきます。視覚に障がいのある子どもたちが学ぶ学校も含め、すべての子どもが救命を学べる機会をつくりたいと考えています。</p>
<h3>ご寄付でできること</h3>
<table class="info-table">
<tr><th>2,500円</th><td>PUSH練習キット1個（子ども1人分）</td></tr>
<tr><th>10,000円</th><td>PUSH練習キット4個</td></tr>
<tr><th>50,000円</th><td>PUSH練習キット20個（1クラス分）、または訓練用マネキン1体</td></tr>
<tr><th>60,000円</th><td>AEDトレーナー1台</td></tr>
</table>
<h3>今年度の目標</h3>
<p><b>目標額 30万円</b>（2027年7月まで）<br>2027年7月までに、県内の学校3校で無料の救命講習を開催します。</p>
<ul>
<li>PUSH練習キット40個（2クラス分）… 10万円</li>
<li>訓練用マネキン2体 … 10万円</li>
<li>AEDトレーナー1台 … 6万円</li>
<li>出張講習の交通費・準備費 … 4万円</li>
</ul>
<h3>寄付の方法</h3>
<p><b>クレジットカード</b>　スマートフォンから数分で手続きできます。1回だけのご寄付も、毎月のご寄付（500円から）も選べます。寄付のページは、寄付サービス「CONGRANT（コングラント）」で開きます。</p>
<p>{card_btn}</p>
<p><b>銀行振込</b>　<a href="#donation">上記のお振込先</a>へお振込みください。お振込みの際は、お名前の前に<b>「コドモ」</b>とご入力ください（例：コドモ ヤマダタロウ）。</p>
<h3>使い道のご報告</h3>
<p>いただいたご寄付の使い道と、講習を届けた学校・人数は、毎年度の活動報告としてこのホームページで公開します。</p>
<p style="font-size:14px;color:var(--muted)">この募金は返還のないご寄付です（下の「基金」とは別の制度です）。税制上の寄付金控除の対象にはなりません。</p>
<p>{mail_btn(m_kodomo, "募金についてメールする")}</p>
</div></section>

<section class="section" id="member"><div class="wrap prose" style="max-width:860px">
<h2 style="margin-top:0">賛助会員</h2>
<p>協会の活動に賛同し、継続して支えてくださる個人・団体の方を募集しています。病院や企業など、法人でのご入会も歓迎します。</p>
<table class="info-table">
<tr><th>個人</th><td>入会金 5,000円／年会費 1口5,000円（1口以上）</td></tr>
<tr><th>団体・法人</th><td>入会金 10,000円／年会費 1口10,000円（1口以上）</td></tr>
</table>
<h3>お申込み方法</h3>
<ol>
<li>{EMAIL} まで「賛助会員の入会希望」とお知らせください。入会申込書をお送りします。</li>
<li>申込書をお送りいただいたあと、入会金・年会費を<a href="#donation">上記のお振込先</a>へお振込みください。</li>
<li>お振込みの確認をもって入会となります。</li>
</ol>
<p>お納めいただいた入会金・年会費は、返還いたしませんのでご了承ください。</p>
<p>{mail_btn(m_mem, "入会についてメールする")}</p>
</div></section>

<section class="section section-sand" id="fund"><div class="wrap prose" style="max-width:860px">
<h2 style="margin-top:0">基金</h2>
<p>基金は、協会の定款に定めた制度です。活動の土台となる資金をお預かりし、協会が解散するときに利息なしでお返しします。ご寄付と違い、協会の収入ではなく「お預かりするお金」として扱います。募集はご相談をいただいたうえで個別に行っています。</p>
<div class="faq">
<details><summary>基金のきまりとお申込みの流れ</summary>
<p><b>きまり</b></p>
<ul>
<li>お預かりした基金は、協会が解散するまでお返ししません。</li>
<li>返還は解散後の清算のときに、協会のほかの債務を支払ったあとで行います。</li>
<li>利息はつきません。お預かりした額を超えてお返しすることもありません。</li>
<li>返還を受ける権利は、社員総会の同意がない限り、譲渡や質入れなどはできません。</li>
</ul>
<p><b>お申込みの流れ</b></p>
<ol>
<li>{EMAIL} までご相談ください。</li>
<li>協会から募集要項（募集額・払込期日など）をお送りします。</li>
<li>申込書をご提出ください。協会から、お引き受けいただく額（割当）をお知らせします。</li>
<li>期日までにお振込みいただくと、協会から受領書をお送りします。</li>
</ol>
</details>
</div>
<p>土地・建物など、金銭以外のご寄付・ご拠出をお考えの方も、まずはご相談ください。</p>
<p>{mail_btn(m_fund, "基金について相談する")}</p>
</div></section>"""


def inars_ld():
    out = []
    for c in INARS_COURSES:
        if c["date"] < TODAY:
            continue
        out.append({
            "@context": "https://schema.org", "@type": "Event", "name": c["title"],
            **ld_dates(c["date"], c.get("time")),
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "Place", "name": c["place"], "address": c["place"]},
            "description": "医療従事者向けの院内急変回避研修（INARSコース）",
            "image": [SITE_URL + "/assets/og.png"],
            "performer": {"@type": "Organization", "name": "INARSコース インストラクター"},
            # 受講料はサイトに載せない方針のため offers（価格情報）は付けず、申込ページは url で示す
            **({"url": c["url"]} if c.get("url") else {}),
        })
    return out


def inars_row(c, past):
    d = datetime.date.fromisoformat(c["date"])
    btn = ""
    if not past:
        if c.get("url"):
            btn = f'<p style="margin-top:12px"><a class="btn btn-primary" href="{c["url"]}" rel="noopener">詳細・お申し込み（MeCCSO） {ARROW}</a></p>'
        else:
            btn = '<p class="place" style="margin-top:8px">申込受付の準備中です</p>'
    fee = ""  # 受講料は協会のお金ではないため表示しない（MeCCSOの申込ページで案内）
    if past:
        status = '<span class="status status-done">終了</span>'
    elif c.get("url"):
        status = '<span class="status status-open">受付中</span>'
    else:
        status = '<span class="status status-soon">受付準備中</span>'
    return f"""<article class="event{' event-past' if past else ''}">
<time datetime="{c['date']}">{d.month}/{d.day}<small>{d.year}年（{WEEK[d.weekday()]}）<br>{esc(c.get('time', ''))}</small></time>
<div>{status}<h3>{esc(c['title'])}{f' <span class="tag" style="vertical-align:middle">{esc(c["note"])}</span>' if c.get("note") else ''}</h3><p class="place">会場：{esc(c['place'])}{fee}</p>{btn}</div>
</article>"""


def ws_html(prefix):
    up = sorted([w for w in INARS_WORKSHOPS if w["date"] >= TODAY], key=lambda w: w["date"])
    rows = []
    for w in up:
        d = datetime.date.fromisoformat(w["date"])
        st = '<span class="status status-done">満席</span>' if w.get("full") else '<span class="status status-open">受付中</span>'
        rows.append(f'<tr><td class="num">{d.year}.{d.month:02d}.{d.day:02d}（{WEEK[d.weekday()]}）<br>{esc(w["time"])}</td>'
                    f'<td>{st}<br>{esc(w["title"])}</td><td>{esc(w["place"])}</td>'
                    f'<td><a href="{w["url"]}" rel="noopener">詳細（MeCCSO）</a></td></tr>')
    table = (f'<div class="table-scroll" style="margin-top:28px"><table class="record"><thead><tr><th>開催日</th><th>ワークショップ</th><th>会場</th><th>詳細</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table></div>') if rows else ""
    return f"""<section class="section" id="instructor"><div class="wrap">
{section_head('INSTRUCTOR', 'インストラクターを目指す方へ', f'<a class="more" href="{INARS_WS_LIST_URL}" rel="noopener">全国のワークショップ一覧（MeCCSO）→</a>')}
<p style="max-width:52em;color:var(--ink-2)">INARSの指導者養成ワークショップでは、午前中に指導方法を学び、午後は同じ日のINARSコースにインストラクターとして参加します。中国・四国で開催されるワークショップの日程をご案内します。お申し込みにはMeCCSOのアカウント作成が必要です。</p>
{table}
</div></section>"""


def inars(prefix):
    upcoming = sorted([c for c in INARS_COURSES if c["date"] >= TODAY], key=lambda c: c["date"])
    past = sorted([c for c in INARS_COURSES if c["date"] < TODAY], key=lambda c: c["date"], reverse=True)
    up = "".join(inars_row(c, False) for c in upcoming) or (
        f'<p class="empty">現在、受付中のコースはありません。<br>全国の開催予定は<a href="{INARS_LIST_URL}" rel="noopener">MeCCSOの申込一覧</a>でもご覧いただけます。</p>')
    past_html = "".join(inars_row(c, True) for c in past)
    past_sec = f"""<section class="section"><div class="wrap">
{section_head('ARCHIVE', 'これまでのコース')}
<div class="events">{past_html}</div>
</div></section>""" if past_html else ""
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ INARSコース</p>
<h1>INARSコース</h1>
<p class="lead">医療従事者・看護教育のための院内急変回避研修、INARS（アイナース）コースの日程とお申し込み先をご案内します。当協会は「中四国INARSコース」をはじめ、各地のコースの開催を支援しています。</p>
</div></section>

<section class="section" id="schedule"><div class="wrap">
{section_head('SCHEDULE', '開催予定・お申し込み', f'<a class="more" href="{INARS_LIST_URL}" rel="noopener">全国の開催一覧（MeCCSO）→</a>')}
<div class="events">{up}</div>
<p style="margin-top:20px;font-size:14px;color:var(--muted)">「職員限定」のコースは、開催病院の職員の方のみ受講できます。お申し込みは、医療危機管理支援機構（MeCCSO）の申込ページで受け付けています。「詳細・お申し込み」から、MeCCSOの各コースのページに進めます。受講料・お支払い方法と空き状況（満席・キャンセル待ち）は、各コースの申込画面でご確認ください。</p>
</div></section>

<section class="section section-sand"><div class="wrap">
<div class="split" style="color:inherit">
<div><span class="eyebrow">ABOUT INARS</span><h2 class="h2">INARSコースとは</h2></div>
<div style="color:var(--ink-2)">
<p>INARS（アイナース）は、入院患者さんの「なんか変」「いつもと違う」という小さなサインに気づき、心停止などの急変を未然に防ぐための実践的なシミュレーション研修です。</p>
<p>A（気道）・B（呼吸）・C（循環）・D（意識）・E（外表・体温）の順に観察し、急変の前ぶれをとらえる方法を身につけます。看護師をはじめとする医療従事者や看護教育の現場を対象に、観察から報告・応援要請、初期対応（ファーストアクション）までを、チームで繰り返し練習します。</p>
</div>
</div>
</div></section>

{ws_html(prefix)}

<section class="section section-paper"><div class="wrap">
{section_head('HOST', '院内開催のご相談')}
<div class="grid-3">
<div class="card"><span class="num">1</span><h3>会場のご用意</h3><p>研修室などの会場の確保と、院内での受講者の募集をお願いしています。</p></div>
<div class="card"><span class="num">2</span><h3>開催の準備をサポート</h3><p>インストラクターの手配や受講者の募集など、開催に向けた準備をお手伝いします。</p></div>
<div class="card"><span class="num">3</span><h3>まずはご相談を</h3><p>開催時期や人数、院内限定か公募かなど、ご希望に合わせてご提案します。</p></div>
</div>
<p style="margin-top:32px"><a class="btn btn-primary" href="{prefix}contact/#request">院内開催を相談する {ARROW}</a></p>
</div></section>
{past_sec}"""


def not_found(prefix):
    return f"""<section class="page-hero" style="border:0"><div class="wrap">
<h1>ページが見つかりません</h1>
<p class="lead">お探しのページは移動したか、削除された可能性があります。</p>
<p style="margin-top:24px"><a class="btn btn-primary" href="{SITE_URL}/">トップページへ</a></p>
</div></section>"""


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)

    page("", "", "岡山・備前市で救命講習・AED講習なら日本臨床ライフサポート協会へ。現役の看護師・医師など医療の専門職が、胸骨圧迫・AEDの使い方と心停止を防ぐ「急変回避（INARS）」を実践的に指導します。学校・企業・スポーツチームへの出張講習も。",
         top, "", full_title=f"{ORG_NAME}｜岡山の救命講習・AED講習")
    page("about/", "協会について", "日本臨床ライフサポート協会の代表理事あいさつ、事業内容（市民向け救命講習「PUSHプロジェクト」、医療従事者向け「INARSコース」、救護ボランティア）、協会概要と沿革です。",
         about, "about", [breadcrumb_ld([("トップ", ""), ("協会について", "about/")])])
    page("courses/", "救命講習会", "岡山県内（備前市・赤磐市・岡山市・倉敷市）で開催する救命講習会・AED講習の日程と、学校・企業・団体向け出張講習のご案内。防災士資格取得の救命講習として認定された180分コースもあります。",
         courses, "courses", courses_ld() + [faq_ld(), breadcrumb_ld([("トップ", ""), ("救命講習会", "courses/")])])
    page("inars/", "INARSコース 開催予定・お申し込み", "医療従事者・看護教育向けの院内急変回避研修INARS（アイナース）コース。当協会が開催を支援する中四国INARSコースなどの日程と、MeCCSO申込ページへのご案内です。",
         inars, "inars", inars_ld() + [breadcrumb_ld([("トップ", ""), ("INARSコース", "inars/")])])
    page("reports/", "活動報告", "日本臨床ライフサポート協会の救命講習会・INARSコースの開催報告とお知らせ。", reports_index, "reports",
         [breadcrumb_ld([("トップ", ""), ("活動報告", "reports/")])])
    for i, r in enumerate(reports_sorted):
        report_page(r, i)
    page("support/", "ご支援のお願い", "日本臨床ライフサポート協会へのご支援のお願い。ご寄付・賛助会員（個人・団体）・基金の3つの方法と、お申し込みの流れをご案内します。",
         support, "support", [breadcrumb_ld([("トップ", ""), ("ご支援のお願い", "support/")])])
    page("contact/", "お申し込み・お問い合わせ", "救命講習会への参加、出張講習・院内開催のご依頼、INARSコースのお申し込み、ご寄付のお問い合わせはこちら。メールまたはLINEで受け付けています。",
         contact, "contact", [breadcrumb_ld([("トップ", ""), ("お申し込み・お問い合わせ", "contact/")])])

    # 404（GitHub Pages はルートの 404.html を使う。リンクは絶対URL）
    page("404.html", "ページが見つかりません", "お探しのページは見つかりませんでした。", not_found)
    written.remove("404.html")
    with open(os.path.join(OUT, "404.html"), encoding="utf-8") as f:
        t = f.read()
    t = t.replace('href="assets/', f'href="{SITE_URL}/assets/').replace('src="assets/', f'src="{SITE_URL}/assets/') \
         .replace('href="favicon.png"', f'href="{SITE_URL}/favicon.png"').replace('href="apple-touch-icon.png"', f'href="{SITE_URL}/apple-touch-icon.png"')
    t = t.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"')
    for p in ["about/", "courses/", "inars/", "reports/", "contact/", "support/"]:
        t = t.replace(f'href="{p}', f'href="{SITE_URL}/{p}')
    t = t.replace('class="brand" href=""', f'class="brand" href="{SITE_URL}/"')
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(t)

    # 旧Wix URL からの転送
    redirect("business-contents", "about/")
    redirect("event-list", "courses/")
    redirect("blog-1", "reports/")
    for r in REPORTS:
        for old in r.get("old_paths", []):
            redirect(old, f"reports/{r['slug']}/")

    # sitemap / robots
    urls = "".join(f"<url><loc>{SITE_URL}/{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in written)
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    print(f"built {len(written)} pages → {OUT}")


if __name__ == "__main__":
    build()
