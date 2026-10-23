import re, collections, json
from games import GAMES
from wget import fetch
MED=re.compile(r'\{\{\s*(gold|silver|bronze)\s*(?:medal)?\s*\}\}|\{\{\s*(gold|silver|bronze)\s*[123]\s*\}\}|\b(Gold|Silver|Bronze)\b',re.I)
def section(t):
    m=re.search(r'^==\s*(?:List of\s+)?Medal(?:l)?(?:ists|s)\s*==',t,re.M|re.I) or re.search(r'^==\s*Medal(?:l)?ist',t,re.M|re.I)
    if not m: return None
    j=t.find('\n==',m.end())
    while j>0 and t[j:j+3]=='\n==' and t[j+3]=='=': j=t.find('\n==',j+3)
    return t[m.start():j]
out=[]
for y,c,n in GAMES:
    t=fetch(f"Australia at the {y} {n}")
    s=section(t)
    if not s: print(y,'no section'); continue
    rows=re.split(r'\n\|-[^\n]*',s)
    cnt=collections.Counter()
    for r in rows:
        mm=MED.search(r)
        if not mm: continue
        med=next(g for g in mm.groups() if g).lower()
        links=[l for l in re.findall(r'\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]',r) if ' at the ' not in l and not l.startswith('File:')]
        names=re.findall(r'\{\{sortname\|([^|}]+)\|([^|}]+)((?:\|[^|}]*)*)\}\}',r)
        people=[]
        for f,l,rest in names:
            ps=[p for p in rest.split('|') if p]
            link=[p for p in ps if '=' not in p]
            dab=[p.split('=',1)[1] for p in ps if p.startswith('dab=')]
            people.append(link[0].strip() if link else (f"{f} {l} ({dab[0]})" if dab else f"{f} {l}").strip())
        people+=links
        SP=r'(?:.*\(sport\)|.*\bsports?|Sport of athletics|Olympic weightlifting|Swimming|Cycling|Fencing|Diving|Weightlifting|Wrestling|Boxing|Rowing|Athletics|Gymnastics|Artistic gymnastics|Rhythmic gymnastics|Shooting|Aquatics|Lawn bowls|Bowls|Hockey|Field hockey|Netball|Squash|Judo|Triathlon|Badminton|Archery|Basketball|Cricket|Tennis|Rugby sevens|Table tennis|Synchronised swimming|Synchronized swimming|Powerlifting|Para powerlifting|Water polo|Beach volleyball|Ten-pin bowling|Tenpin bowling|Australia|Canada|England|New Zealand|Scotland|Wales|India)'
        people=[p for p in people if not re.fullmatch(SP,p) and 'metre' not in p and 'relay' not in p.lower() and 'Commonwealth' not in p and 'national' not in p]
        sp=re.search(r'\[\[([A-Za-z0-9 ()\-]+?) at the \d{4}[^\]|]*\|([^\]]+)\]\]',r)
        out.append(dict(year=y,medal=med,people=list(dict.fromkeys(people)),sport=sp.group(1) if sp else None,row=r[:300]))
        cnt[med]+=1
    print(y,dict(cnt))
json.dump(out,open('aus_medalists_raw.json','w'),indent=0)
