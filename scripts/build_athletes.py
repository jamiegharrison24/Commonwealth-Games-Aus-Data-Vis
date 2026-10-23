"""Total athletes at each Games (Wikipedia infobox) -> Australia's share of athletes vs share of medals."""
import re, csv
from games import GAMES
from wget import fetch
OUT='/home/claude/site/data/games.csv'
tot={}; note={}
for y,c,n in GAMES:
    t=fetch(f"{y} {n}")
    m=re.search(r'\|\s*athletes\s*=\s*([^\n]+)',t)
    raw=m.group(1); v=int(re.sub(r'[^\d]','',re.match(r'[\d,]+',raw).group(0)))
    tot[y]=v; note[y]='includes officials' if 'officials' in raw else ''
rows=list(csv.DictReader(open(OUT)))
for r in rows:
    y=int(r['year']); r['total_athletes']=tot[y]; r['athletes_note']=note[y]
    r['aus_athlete_share']=round(int(r['aus_team'])/tot[y],4)
    r['conversion']=round(float(r['aus_share'])/r['aus_athlete_share'],2)
with open(OUT,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(x) for x in rows]
for r in rows: print(r['year'], r['aus_team'], r['total_athletes'], r['aus_athlete_share'], r['aus_share'], r['conversion'], r['athletes_note'])
