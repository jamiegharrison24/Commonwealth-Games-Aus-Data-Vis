"""Builds the five styled variants (style-a.html ... style-e.html) from index.html.

Each variant keeps every chart, caption and paragraph of index.html and adds:
  - a themed hero (masthead / cover / pack / broadcast open / magazine cover)
  - the shared layout features from css/features.css + js/features.js:
      sticky medal tally, running-track spine, pull-out stickers, scrollytelling bump chart
  - its own skin in css/themes/<theme>.css and chart fonts via window.THEME_VEGA

Run from the repo root:  python scripts/build_styles.py
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / 'index.html').read_text(encoding='utf-8')

THEMES = {
    'a': dict(name='Tabloid', css='a-tabloid', dark_hero=False,
              fonts='family=Anton&family=Oswald:wght@400;500;600;700',
              vega="{ font: 'Oswald', titleFont: 'Anton' }"),
    'b': dict(name='Programme', css='b-programme', dark_hero=False,
              fonts='family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&family=Lora:ital,wght@0,400;0,600;1,400&family=Oswald:wght@400;500;600',
              vega="{ font: 'Oswald', titleFont: 'Playfair Display' }"),
    'c': dict(name='Cards', css='c-cards', dark_hero=True,
              fonts='family=Bebas+Neue',
              vega="{ font: 'Barlow', titleFont: 'Bebas Neue' }"),
    'd': dict(name='Broadcast', css='d-broadcast', dark_hero=True,
              fonts='family=Oswald:ital,wght@0,400;0,500;0,600;0,700',
              vega="{ font: 'Oswald', titleFont: 'Oswald' }"),
    'e': dict(name='Magazine', css='e-magazine', dark_hero=False,
              fonts='family=Archivo:wght@400;500;600;700;800&family=Archivo+Black',
              vega="{ font: 'Archivo', titleFont: 'Archivo Black' }"),
}

CHAPTERS = [  # id, number, short title used in contents blocks
    ('where', '01', 'A Games that moves around the world'),
    ('travel', '02', 'The long way there'),
    ('rise', '03', 'Climbing to the top'),
    ('home', '04', 'No place like home'),
    ('sports', '05', 'Built in the pool'),
    ('greats', '06', 'The greats'),
    ('easier', '07', 'Are the Games getting easier?'),
    ('glasgow', '08', 'Glasgow 2026'),
]

def between(s, start, end):
    i = s.index(start); j = s.index(end, i) + len(end)
    return s[i:j]

HERO_FIG = between(SRC, '<figure class="hero-fig">', '</figure>')
SCOREBOARD = between(SRC, '<div class="scoreboard"', '</div>\n    <p class="scroll-cue">').replace('\n    <p class="scroll-cue">', '')
DEK = re.search(r'<p class="dek">(.*?)</p>', SRC, re.S).group(1)
BYLINE = '<p class="byline">By <strong>Jamie</strong><br>Monash University · FIT3179 Data Visualisation<br>October 2026 · Data to Glasgow 2026</p>'

def ph(label, cls='ph'):
    return f'<div class="{cls}" role="img" aria-label="Photo placeholder: {label}"><span>{label}<br><small>add a CC photo from Wikimedia Commons</small></span></div>'

def contents(item_fmt, wrap_cls):
    items = ''.join(item_fmt(i, n, t) for i, n, t in CHAPTERS)
    return f'<nav class="{wrap_cls}" aria-label="Chapters">{items}</nav>'

# ---------------------------------------------------------------- heroes
def hero_a():
    burst = ('<svg class="burst" viewBox="0 0 100 100" aria-hidden="true"><polygon points="50,2 58,22 79,9 74,32 97,32 80,47 97,62 74,64 80,88 58,77 50,98 42,77 20,88 26,64 3,62 20,47 3,32 26,32 21,9 42,22"/>'
             '<text x="50" y="49" text-anchor="middle" font-size="17">2,771</text><text x="50" y="64" text-anchor="middle" font-size="10">MEDALS!</text></svg>')
    teasers = [
        ('travel', '17,000 km', 'Why Britain is the longest away trip in sport'),
        ('home', 'Home ground', 'Bigger teams, bigger hauls: what hosting is worth'),
        ('easier', 'Stars stay home?', 'Testing the big complaint against the Olympics'),
    ]
    tz = ''.join(f'<a class="teaser" href="#{i}"><b>{h}</b><span>{t}</span><em>Turn to {n}</em></a>'
                 for (i, h, t), n in zip(teasers, ['02', '04', '07']))
    return f'''<header class="hero">
  <div class="t-mast"><div class="wrap"><span class="t-name">The Medal Tally</span><span class="t-date">Commonwealth Games special · 1930–2026</span></div></div>
  <div class="t-strap"><div class="wrap">Inside: <a href="#sports">How the pool built an empire</a> · <a href="#greats">The medal collectors</a> · <a href="#glasgow">Glasgow's shrinking Games</a></div></div>
  <div class="wrap">
    <div class="t-front">
      <div class="t-lead">
        <h1>Green &amp; gold <em>rush</em></h1>
        <p class="t-deck"><span>Aussies top the medal table 15 times in 23 Games, and nobody else is close</span></p>
        <p class="dek">{DEK}</p>
        {BYLINE}
      </div>
      <div class="t-photo">{ph('Emma McKeon, Gold Coast 2018')}<div class="t-cap"><b>McKEON:</b> 20 medals in eight years, 14 of them gold</div>{burst}</div>
    </div>
    <div class="t-teasers">{tz}</div>
    {night('a')}
  </div>
</header>'''

ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
def hero_b():
    toc = contents(lambda i, n, t: f'<a href="#{i}"><span class="r">{ROMAN[int(n)-1]}.</span><span class="t">{t}</span><span class="dots"></span><span class="pg">{n}</span></a>', 'p-toc')
    return f'''<header class="hero">
  <div class="wrap">
    <div class="p-cover">
      <div class="p-seal" aria-hidden="true">Est.<br>Hamilton<br>1930</div>
      <p class="kicker">British Empire &amp; Commonwealth Games · Official souvenir programme</p>
      <h1>Top of the <i>Table</i></h1>
      <div class="p-rule"></div>
      <p class="subhead">How Australia came to own the Commonwealth Games, and whether anyone can still challenge it</p>
      <div class="p-cols">
        <div><p class="dek">{DEK}</p>{BYLINE}</div>
        <div><h2 class="p-toc-h">Programme of events</h2>{toc}</div>
      </div>
    </div>
    {night('b')}
  </div>
</header>'''

def greats_cards(n=6):
    rows = list(csv.DictReader(open(ROOT / 'data' / 'aus_greats.csv', encoding='utf-8')))
    seen = {}
    for r in rows:
        a = seen.setdefault(r['athlete'], dict(r, games=0)); a['games'] += 1
    top = sorted(seen.values(), key=lambda a: int(a['rank']))[:n]
    out = []
    for k, a in enumerate(top):
        rot = [-3, 2, -1, 3, -2, 1][k % 6]
        span = a['first'] if a['first'] == a['last'] else f"{a['first']}–{a['last']}"
        out.append(f'''<div class="cc-card" style="--r:{rot}deg"><div class="cc-in"><span class="cc-sport">{a['sport']}</span>{ph(a['athlete'])}
<div class="cc-name">{a['athlete']}</div><div class="cc-span">{span}</div>
<div class="cc-stats"><div><b>{a['career_total']}</b><small>Medals</small></div><div><b>{a['career_gold']}</b><small>Gold</small></div><div><b>{a['games']}</b><small>Games</small></div></div></div></div>''')
    return out

def hero_c():
    cards = ''.join(greats_cards(3))
    toc = contents(lambda i, n, t: f'<a class="mini" href="#{i}"><b>{n}</b><span>{t}</span></a>', 'c-toc')
    return f'''<header class="hero dark">
  <div class="wrap">
    <div class="c-top">
      <div>
        <p class="kicker">The Australian Commonwealth Games collection · 1930–2026</p>
        <h1>Top of the <span class="gold-word">Table</span></h1>
        <p class="subhead">2,771 medals. 23 Games. Collect the whole set.</p>
        <p class="dek">{DEK}</p>
        {BYLINE}
      </div>
      <div class="c-fan">{cards}</div>
    </div>
    <p class="c-toc-h">This pack contains</p>
    {toc}
    {HERO_FIG}
    {SCOREBOARD}
  </div>
</header>'''

def hero_d():
    rundown = contents(lambda i, n, t: f'<a href="#{i}"><span class="n">{n}</span><span class="t">{t}</span></a>', 'd-rundown')
    ticker = ('<b>AQUATICS</b>1,014 Australian medals since 1930<b>DISTANCE</b>Britain is about 17,000 km from Canberra'
              '<b>HOME</b>Australia\'s biggest team: 473 at the Gold Coast 2018<b>GLASGOW</b>Australia won 171 of 674 medals'
              '<b>OLYMPIANS</b>Fewer than a third of the Commonwealth\'s Olympic medallists now win at the Games')
    return f'''<header class="hero dark">
  <div class="wrap">
    <div class="d-open">
      <div class="d-left">
        <span class="d-live">● Live from Glasgow 2026</span>
        <h1>Top of the <span class="gold-word">Table</span></h1>
        <p class="subhead">How Australia came to own the Commonwealth Games, and whether anyone can still challenge it</p>
        <p class="dek">{DEK}</p>
        {BYLINE}
      </div>
      <div class="d-right">
        <div class="d-bug" aria-label="Australia's all-time tally"><span class="n">AUS</span><span class="g">1,071 GOLD</span><span class="t">2,771</span></div>
        {ph('Ian Thorpe, Manchester 2002', 'ph')}
        <div class="d-lower"><span class="a">EMMA McKEON</span><span class="b">20 medals · most decorated Australian</span></div>
      </div>
    </div>
    <div class="d-rundown-wrap"><p class="d-rundown-h">Coming up</p>{rundown}</div>
    {HERO_FIG}
    {SCOREBOARD}
  </div>
  <div class="d-ticker" aria-hidden="true"><div class="ticker-run">{ticker}{ticker}</div></div>
</header>'''

def hero_e():
    idx = contents(lambda i, n, t: f'<a href="#{i}"><b>{n}</b><span>{t}</span></a>', 'e-index')
    return f'''<header class="hero">
  <div class="e-cover">
    <div class="e-l">
      <p class="kicker">Commonwealth Games · 1930–2026</p>
      <div class="e-big">2,771</div>
      <p class="e-lab">Commonwealth Games medals won by Australia, more than any other nation</p>
      <h1>Top of the Table</h1>
    </div>
    <div class="e-r">
      {ph('Swimmer, green duotone')}
      <p class="subhead">How Australia came to own the Commonwealth Games, and whether anyone can still challenge it</p>
    </div>
  </div>
  <div class="wrap">
    <div class="e-intro"><p class="dek">{DEK}</p>{BYLINE}</div>
    {idx}
    {night('e')}
  </div>
</header>'''

HEROES = dict(a=hero_a, b=hero_b, c=hero_c, d=hero_d, e=hero_e)

# ---------------------------------------------------------------- shared pieces
TALLY = '''<div class="tally" aria-hidden="true"><div class="wrap"><span class="t-team">AUS</span><span class="t-nums"><span><b>2,771</b> medals</span><span><b>1,071</b> gold</span><span><b>15</b>× top of the table</span></span><span class="t-now"></span></div><div class="t-bar"></div></div>
<nav class="spine" aria-label="Chapters"><div class="track"></div><div class="runner"></div></nav>'''

STICKERS = {  # figure containing this vis id -> (position, big, small)
    'vis-hero': ('ml', '87 golds', 'Victoria 1994: Australia\'s most at one Games'),
    'vis-flows': ('br', 'Just 17', 'Australians made the trip to London in 1934'),
    'vis-mekko': ('mr', '57%', 'of all Australian medals came from the pool or athletics'),
    'vis-greats': ('tr', '10 from 11', 'Ian Thorpe and Leisel Jones: ten golds each from 11 medals'),
}

SCROLLY_STEPS = [
    ('1928,1936', '1930–1934', 'England wins the first two Games. Australia, with nine athletes in 1930, finishes fifth.'),
    ('1936,1988', '1938–1986', 'For half a century Australia and England swap first place. Canada takes it once, at home in Edmonton in 1978.'),
    ('1988,2012', '1990–2010', 'From 1990 Australia tops the table six Games in a row.'),
    ('2012,2016', 'Glasgow 2014', 'The one slip: England finishes first, Australia second.'),
    ('2016,2028', '2018–2026', 'Back on top at the Gold Coast, Birmingham and Glasgow.'),
]

def scrollify(h):
    start = h.index('<div class="row">\n      <figure class="reveal span-12">\n        <h3 class="fig-title">Since 1990')
    end = h.index('</div>', h.index('</figure>', start)) + len('</div>')
    fig = h[h.index('<figure', start):h.index('</figure>', start) + len('</figure>')]
    fig = fig.replace('<figure class="reveal span-12">', '<figure>')
    steps = ''.join(f'<div class="step" data-band="{b}"><div><b class="when">{w}</b>{t}</div></div>' for b, w, t in SCROLLY_STEPS)
    block = f'<div class="scrolly"><div class="steps">{steps}</div><div class="stick">{fig}</div></div>'
    return h[:start] + block + h[end:]

def add_stickers(h):
    for vid, (pos, big, small) in STICKERS.items():
        k = h.index(f'id="{vid}"')
        f = h.rindex('<figure', 0, k)
        tag_end = h.index('>', f)
        tag = h[f:tag_end]
        if 'class="' in tag:
            new_tag = tag.replace('class="', 'class="has-sticker ', 1)
        else:
            new_tag = tag + ' class="has-sticker"'
        sticker = f'<div class="sticker {pos}" aria-hidden="true"><b>{big}</b>{small}</div>'
        h = h[:f] + new_tag + '>' + sticker + h[tag_end + 1:]
    return h

def switcher(cur):
    links = [('index.html', 'Original', None)] + [(f'style-{k}.html', f'{k.upper()} · {v["name"]}', k) for k, v in THEMES.items()]
    return '<nav class="switcher" aria-label="Style variants">' + ''.join(
        f'<a href="{u}"{" aria-current=\"page\"" if k == cur else ""}>{t}</a>' for u, t, k in links) + '</nav>'

def night(key):
    inner = f'{HERO_FIG}\n    {SCOREBOARD}'
    return inner if THEMES[key]['dark_hero'] else f'<div class="hero-night dark">{inner}</div>'

def build(key):
    t = THEMES[key]
    h = SRC
    h = h.replace('<title>', f'<title>[{t["name"]}] ', 1)
    head_add = (f'  <link href="https://fonts.googleapis.com/css2?{t["fonts"]}&display=swap" rel="stylesheet">\n'
                f'  <link rel="stylesheet" href="css/features.css">\n'
                f'  <link rel="stylesheet" href="css/themes/{t["css"]}.css">\n'
                f'  <script>window.THEME_VEGA = {t["vega"]};</script>\n')
    h = h.replace('  <script src="https://cdn.jsdelivr.net/npm/vega@', head_add + '  <script src="https://cdn.jsdelivr.net/npm/vega@', 1)
    h = h.replace('<body>', f'<body class="theme-{key}">\n{TALLY}\n{switcher(key)}', 1)
    hs = h.index('<header class="hero dark">'); he = h.index('</header>', hs) + len('</header>')
    h = h[:hs] + HEROES[key]() + h[he:]
    h = scrollify(h)
    if key == 'c':  # collector cards lead into the greats timeline
        cards = ''.join(greats_cards(6))
        anchor = '<div class="row">\n      <figure class="reveal span-12">\n        <h3 class="fig-title">Emma McKeon'
        assert anchor in h
        h = h.replace(anchor, f'<div class="cc-grid" aria-label="Top six collector cards">{cards}</div>\n    ' + anchor, 1)
    h = add_stickers(h)
    h = h.replace('<script src="js/main.js"></script>', '<script src="js/main.js"></script>\n<script src="js/features.js"></script>', 1)
    (ROOT / f'style-{key}.html').write_text(h, encoding='utf-8', newline='\r\n')
    print('wrote', f'style-{key}.html')

if __name__ == '__main__':
    for k in THEMES:
        build(k)
