# -*- coding: utf-8 -*-
"""サイトを docs/ に書き出すスクリプト。 実行: python3 src/build.py"""
import datetime
import html
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import (AREAS, EMAIL, EVENTS, LINE_URL, ORG_NAME, ORG_SHORT, PHOTOS,
                     PLANS, REPORTS, SITE_URL, SNS)

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


def photo(key, alt, prefix, cls=""):
    f = PHOTOS.get(key)
    if f:
        return f'<img class="photo {cls}" src="{prefix}assets/photos/{esc(f)}" alt="{esc(alt)}" loading="lazy">'
    return f'<div class="ph {cls}" role="img" aria-label="{esc(alt)}（写真準備中）">［写真：{esc(alt)}］</div>'


ORG_LD = {
    "@context": "https://schema.org",
    "@type": "NGO",
    "name": ORG_NAME,
    "alternateName": "Japan Clinical Life Support Association",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/assets/logo.png",
    "email": EMAIL,
    "description": "岡山県備前市を拠点に、胸骨圧迫・AEDの救命講習（PUSHプロジェクト）と医療従事者向けの急変回避研修（INARS）を行う一般社団法人。",
    "address": {"@type": "PostalAddress", "addressRegion": "岡山県", "addressLocality": "備前市", "addressCountry": "JP"},
    "areaServed": ["備前市", "赤磐市", "岡山市", "倉敷市"],
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
    items = [("about/", "事業内容"), ("courses/", "講習会案内"), ("reports/", "活動報告"), ("contact/#donate", "ご寄付")]
    cur = ' aria-current="page"'
    links = "".join(
        f'<a href="{prefix}{href}"{cur if current and current == href.split("/")[0] else ""}>{label}</a>'
        for href, label in items)
    return f"""<a class="skip" href="#main">本文へ移動</a>
<header class="site-header">
<div class="wrap">
<a class="brand" href="{prefix}"><img src="{prefix}assets/logo.png" alt="" width="56" height="56"><span><small>一般社団法人</small><strong>{ORG_SHORT}</strong></span></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="メニューを開く">
<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
</button>
<nav class="nav" id="site-nav" aria-label="メインメニュー">{links}<a class="btn btn-primary" href="{prefix}contact/">講習のご依頼・お問い合わせ</a></nav>
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
<span>活動地域：{AREAS}</span>
</div>
<div class="footer-col">
<h2>サイト</h2>
<a href="{prefix}about/">事業内容</a><a href="{prefix}courses/">講習会案内</a><a href="{prefix}reports/">活動報告</a><a href="{prefix}contact/">お問い合わせ・ご寄付</a>
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
<script>
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
    write(path, doc)
    written.append(path)


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
        out.append(f"""<a class="report-card" href="{prefix}reports/{r['slug']}/">
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


# ======================= pages =======================
def top(prefix):
    latest = reports_sorted[0]
    return f"""
<section class="hero">
<div class="wrap">
<div class="hero-text">
<span class="eyebrow">岡山・備前市から　救命講習・AED講習</span>
<h1>救える命を、<br>救える社会に。</h1>
<p>現役の看護師・医師など医療の専門職が、胸骨圧迫とAEDの使い方、そして心停止を未然に防ぐ「急変回避（INARS）」の考え方を、わかりやすくお伝えします。</p>
<div class="hero-actions">
<a class="btn btn-primary" href="{prefix}courses/">講習会の日程を見る {ARROW}</a>
<a class="btn btn-outline" href="{prefix}contact/">出張講習を依頼する</a>
</div>
</div>
<div class="hero-media">{photo('hero', '救命講習会の様子', prefix)}</div>
</div>
</section>

<div class="wrap" style="padding-bottom:clamp(56px,7vw,88px)">
<div class="news">
<span class="news-label">お知らせ</span>
<a class="news-item" href="{prefix}reports/{latest['slug']}/"><span class="date">{jdate(latest['date'], True)}</span><span class="tag">{esc(latest['tag'])}</span><span>{esc(latest['title'])}</span></a>
<a class="more" href="{prefix}reports/">一覧へ →</a>
</div>
</div>

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
<div class="card"><span class="num">01</span><h3>医療・看護のプロによる<br>確かな指導</h3><p>医療の最前線を知る看護師や専門スタッフが直接指導。マニュアルにとどまらない、現場で「本当に使える」知識と技術が身につきます。</p></div>
<div class="card"><span class="num">02</span><h3>「一歩を踏み出す」ための<br>心理的サポート</h3><p>「怖い」「間違えたらどうしよう」という不安に寄り添い、誰でも迷わず動けるようになるための丁寧なカリキュラム（PUSHプログラム等）を重視しています。</p></div>
<div class="card"><span class="num">03</span><h3>地域に根ざした<br>草の根の活動</h3><p>{AREAS.replace('岡山県 ', '')}を中心に、学校・行政・地域団体と連携しながら「命をつなぐ輪」を広げています。</p></div>
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

<section class="section section-paper">
<div class="wrap message">
<div class="message-photo">{photo('representative', '代表理事 浅越博之', prefix)}</div>
<div class="message-body">
<span class="eyebrow">MESSAGE</span>
<h2 class="h2">地域の「最初の一歩」が、<br>命を次へつなぐ。</h2>
<p>私は看護師として医療の最前線に立ち、命の危機に直面する現場を数多く経験してきました。その中で痛感したのは、医療機関にバトンが引き継がれる前――つまり「地域社会でのファーストステップ（初期対応）」がいかに重要かということです。</p>
<p>医療従事者だけでなく、市民の方々、学校、地域コミュニティの誰もが、いざという時に迷わず動ける社会をつくりたい。その想いから、市民向けの「PUSHプロジェクト」や、医療従事者・看護教育のための「INARS」を通じて、実践的な救命スキルの普及とインストラクターの育成に力を注いでいます。</p>
<p>これからも皆様のご理解とご協力をいただきながら、地域の安全と安心のために全力を注いでまいります。</p>
<div class="signature"><small>代表理事</small><strong>浅越 博之</strong></div>
</div>
</div>
</section>

{donate_band(prefix)}
"""


def donate_band(prefix):
    return f"""<section class="donate" id="donate-band">
<div class="wrap">
<div><h2>ご寄付のお願い</h2><p>私たちの活動は、皆様の温かいご支援・ご寄付によって支えられています。お寄せいただいたご寄付は、講習活動の維持・拡大と救命資器材の充実のために大切に使わせていただきます。</p></div>
<a class="btn btn-light" href="{prefix}contact/#donate">寄付について問い合わせる</a>
</div>
</section>"""


def about(prefix):
    blocks = [
        ("push", "救命講習の普及・啓発（PUSHプロジェクト）", "市民の方・学生・企業・スポーツチーム向け",
         "「人が倒れたとき、自分にできること」をシンプルに学ぶ講習会です。胸骨圧迫（心臓マッサージ）とAEDの使い方を中心に、学校、企業、地域コミュニティへ出向いて出張講習を行っています。"),
        ("inars", "院内急変回避研修（INARSコース）", "医療従事者・看護教育の現場向け",
         "医療従事者や看護教育の現場を対象とした、実践的なシミュレーション研修です。入院患者さんのわずかなサインを察知し、急変（心停止など）を未然に回避するための的確な初期対応（ファーストアクション）のスキルをはぐくみます。"),
        ("volunteer", "地域社会の安全対策・ボランティア活動", "地域イベント・スポーツ大会",
         "地域のマラソン大会をはじめとするスポーツイベント等での救護・AEDチームとしての協力や、地域イベントでの安全対策ワークショップの開催など、街全体の安全を守る活動に貢献しています。"),
    ]
    b = "".join(f"""<div class="biz">
<div class="biz-media">{photo(k, t, prefix)}</div>
<div class="biz-body"><span class="biz-for">{f}</span><h2>{t}</h2><p>{x}</p></div>
</div>""" for k, t, f, x in blocks)
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ 事業内容</p>
<h1>事業内容</h1>
<p class="lead">市民向けから医療従事者向けまで、それぞれのレベルに合わせた実践的な救命・ライフサポート研修を展開しています。</p>
</div></section>
<section class="section"><div class="wrap">{b}</div></section>
<section class="section section-sand"><div class="wrap">
{section_head('COURSES', '講習プラン', f'<a class="more" href="{prefix}courses/">講習会案内へ →</a>')}
<div class="grid-2">{plans_html()}</div>
</div></section>
{donate_band(prefix)}"""


def event_html(e, past):
    d = datetime.date.fromisoformat(e["date"])
    apply = ""
    if not past and e.get("apply"):
        apply = f'<p style="margin-top:12px"><a class="btn btn-primary" href="{e["apply"]}" rel="noopener">申し込む {ARROW}</a></p>'
    fee = f"　参加費：{esc(e['fee'])}" if e.get("fee") and not past else ""
    return f"""<article class="event{' event-past' if past else ''}">
<time datetime="{e['date']}">{d.month}/{d.day}<small>{d.year}年（{WEEK[d.weekday()]}）<br>{esc(e.get('time', ''))}</small></time>
<div><h3>{esc(e['title'])}</h3><p>{esc(e['text'])}</p><p class="place">会場：{esc(e['place'])}{fee}</p>{apply}</div>
</article>"""


def courses_ld():
    out = []
    for e in EVENTS:
        if e["date"] < TODAY:
            continue
        start = e.get("time", "").split("〜")[0] or "00:00"
        out.append({
            "@context": "https://schema.org", "@type": "Event", "name": e["title"],
            "startDate": f"{e['date']}T{start}:00+09:00",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {"@type": "Place", "name": e["place"], "address": e["place"]},
            "description": e["text"],
            "organizer": {"@type": "Organization", "name": ORG_NAME, "url": SITE_URL + "/"},
        })
    return out


def courses(prefix):
    upcoming = sorted([e for e in EVENTS if e["date"] >= TODAY], key=lambda e: (e["date"], e.get("time", "")))
    past = sorted([e for e in EVENTS if e["date"] < TODAY], key=lambda e: (e["date"], e.get("time", "")), reverse=True)
    up_html = "".join(event_html(e, False) for e in upcoming) or (
        f'<p class="empty">現在、受付中の講習会はありません。<br>新しい日程は、このページと<a href="{LINE_URL}" rel="noopener">LINE公式アカウント</a>・Instagramでお知らせします。</p>')
    past_html = "".join(event_html(e, True) for e in past)
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ 講習会案内</p>
<h1>講習会案内</h1>
<p class="lead">一般の方向けの救命講習会の日程と、団体向けの出張講習のご案内です。</p>
</div></section>

<section class="section"><div class="wrap">
{section_head('SCHEDULE', '開催予定の講習会')}
<div class="events">{up_html}</div>
</div></section>

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
<p style="margin-top:32px"><a class="btn btn-primary" href="{prefix}contact/">講習を依頼する {ARROW}</a></p>
</div></section>

<section class="section"><div class="wrap">
{section_head('ARCHIVE', 'これまでの講習会')}
<div class="events">{past_html}</div>
</div></section>"""


def reports_index(prefix):
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ 活動報告</p>
<h1>活動報告</h1>
<p class="lead">講習会の開催報告やお知らせを掲載しています。</p>
</div></section>
<section class="section"><div class="wrap"><div class="grid-3">{report_cards(prefix, reports_sorted)}</div></div></section>"""


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
<article class="prose">{r['body']}</article>
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


def contact(prefix):
    subj_req = "講習のご依頼"
    subj_don = "ご寄付について"
    from urllib.parse import quote
    return f"""<section class="page-hero"><div class="wrap">
<p class="breadcrumb"><a href="{prefix}">トップ</a> ／ お問い合わせ・ご寄付</p>
<h1>お問い合わせ・ご寄付</h1>
<p class="lead">講習のご依頼、ご寄付、その他のご質問など、お気軽にご連絡ください。</p>
</div></section>
<section class="section"><div class="wrap">
<div class="contact-grid">
<div class="contact-card"><h2>講習のご依頼</h2><p>ご希望の日時・人数・会場・対象の方をお知らせください。内容や費用についてご提案します。</p><a class="btn btn-primary" href="mailto:{EMAIL}?subject={quote(subj_req)}">メールで依頼する</a></div>
<div class="contact-card"><h2>LINEで相談</h2><p>ちょっとした質問や日程の相談は、LINE公式アカウントからも受け付けています。</p><a class="btn btn-outline" href="{LINE_URL}" rel="noopener">LINEを開く</a></div>
<div class="contact-card" id="donate"><h2>ご寄付について</h2><p>ご寄付の方法や使い道について、ご質問があればお気軽にお問い合わせください。</p><a class="btn btn-outline" href="mailto:{EMAIL}?subject={quote(subj_don)}">寄付について問い合わせる</a></div>
</div>
<p style="margin-top:32px;color:var(--muted)">メールアドレス：<a href="mailto:{EMAIL}">{EMAIL}</a></p>
</div></section>
<section class="section section-sand"><div class="wrap prose" style="max-width:860px">
<h2 style="margin-top:0">ご寄付のお願い</h2>
<p>私たちの活動は、皆様からの温かいご支援・ご寄付によって支えられています。お寄せいただいた寄付金は、講習活動の維持・拡大、救命資器材の充実のために大切に使用させていただきます。</p>
<p>「救える命を、救える社会に」していくため、皆様のご理解とご協力を心よりお願い申し上げます。</p>
</div></section>"""


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
    page("about/", "事業内容", "市民向けの救命講習「PUSHプロジェクト」、医療従事者向けの院内急変回避研修「INARSコース」、マラソン大会等での救護ボランティアなど、日本臨床ライフサポート協会の事業内容です。",
         about, "about", [breadcrumb_ld([("トップ", ""), ("事業内容", "about/")])])
    page("courses/", "講習会案内", "岡山県内（備前市・赤磐市・岡山市・倉敷市）で開催する救命講習会・AED講習の日程と、学校・企業・団体向け出張講習のご案内。防災士資格取得の救命講習として認定された180分コースもあります。",
         courses, "courses", courses_ld() + [breadcrumb_ld([("トップ", ""), ("講習会案内", "courses/")])])
    page("reports/", "活動報告", "日本臨床ライフサポート協会の救命講習会・INARSコースの開催報告とお知らせ。", reports_index, "reports",
         [breadcrumb_ld([("トップ", ""), ("活動報告", "reports/")])])
    for i, r in enumerate(reports_sorted):
        report_page(r, i)
    page("contact/", "お問い合わせ・ご寄付", "救命講習・AED講習の出張依頼、ご寄付、その他のお問い合わせはこちら。メールまたはLINEで受け付けています。",
         contact, "contact", [breadcrumb_ld([("トップ", ""), ("お問い合わせ・ご寄付", "contact/")])])

    # 404（GitHub Pages はルートの 404.html を使う。リンクは絶対URL）
    page("404.html", "ページが見つかりません", "お探しのページは見つかりませんでした。", not_found)
    written.remove("404.html")
    with open(os.path.join(OUT, "404.html"), encoding="utf-8") as f:
        t = f.read()
    t = t.replace('href="assets/', f'href="{SITE_URL}/assets/').replace('src="assets/', f'src="{SITE_URL}/assets/') \
         .replace('href="favicon.png"', f'href="{SITE_URL}/favicon.png"').replace('href="apple-touch-icon.png"', f'href="{SITE_URL}/apple-touch-icon.png"')
    t = t.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"')
    for p in ["about/", "courses/", "reports/", "contact/"]:
        t = t.replace(f'href="{p}', f'href="{SITE_URL}/{p}')
    t = t.replace('href="contact/#donate"', f'href="{SITE_URL}/contact/#donate"').replace('class="brand" href=""', f'class="brand" href="{SITE_URL}/"')
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
