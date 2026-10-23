import re, json, csv
from wget import fetch
def tosec(m):
    m=m.strip()
    mm=re.match(r'^(?:(\d+):)?(?:(\d+):)?(\d+(?:\.\d+)?)',m)
    if not mm: return None
    parts=[p for p in mm.groups() if p is not None]
    v=0.0
    for p in parts: v=v*60+float(p)
    return v
def clean_mark(x):
    x=re.sub(r"<ref.*?(</ref>|/>)",'',x,flags=re.S)
    x=re.sub(r"'''?\[\[[^\]]*\]\]'''?",'',x); x=re.sub(r'\{\{[^}]*\}\}','',x); x=re.sub(r"'''?[A-Z]{1,3}'''?",'',x)
    x=x.replace('&nbsp;',' ').strip()
    wind=bool(re.search(r'\bw\b|\(w\)|w$',x))
    m=re.search(r'(\d+:\d+(?::\d+)?(?:\.\d+)?|\d+\.\d+|\d+)',x)
    return (m.group(1) if m else None), wind, x
def medalist(cell):
    m=re.search(r'\{\{[Ff]lag(?:CGF)?medalist\|\[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*\|([A-Z]{3})',cell)
    if m: return m.group(1).strip(), m.group(2)
    m=re.search(r'\{\{[Ff]lag(?:CGF)?\|([A-Z]{3})',cell)
    if m: return None, m.group(1)
    return None,None
rows=[]
for sex,title in [('Men',"List of Commonwealth Games medallists in athletics (men)"),('Women',"List of Commonwealth Games medallists in athletics (women)")]:
    t=fetch(title)
    t=t[:t.find('==Disability')] if '==Disability' in t else t
    sections=re.split(r'\n===\s*([^=]+?)\s*===\n',t)
    for k in range(1,len(sections),2):
        ev=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]',r'\1',sections[k]).strip(); body=sections[k+1]
        for blk in re.split(r'\n\|-',body)[1:]:
            b=blk.strip()
            y=re.match(r'\|?\s*(\d{4})',b)
            if not y: continue
            y=int(y.group(1))
            ents=re.findall(r'(\{\{[Ff]lag(?:CGF)?(?:medalist)?\|.*?\}\}(?:[^|]|\|(?!\|))*?)\|\|\s*([^|\n]*)',b)
            for place,(a,m) in enumerate(ents[:3],1):
                ath,cty=medalist(a); mk,w,raw=clean_mark(m)
                rows.append(dict(year=y,sex=sex,event=ev,place=place,athlete=ath,country=cty,mark_raw=mk,wind=w))
# 2026
t=fetch("Athletics at the 2026 Commonwealth Games")
for sex in ['Men','Women']:
    i=t.find(f'==={sex}==='); j=t.find('\n===',i+8); sec=t[i:j]
    for blk in re.split(r'\n\|-',sec)[1:]:
        lines=[l for l in blk.split('\n') if l.strip().startswith('|') and not l.strip().startswith('|}')]
        m=re.search(r'EventLink\|([^|}]+)',blk)
        if not m: continue
        ev=m.group(1).strip(); place=0
        for l in lines[1:]:
            if '||' not in l: continue
            a,b=l.split('||',1); place+=1
            ath,cty=medalist(a); mk,w,raw=clean_mark(b)
            rows.append(dict(year=2026,sex=sex,event=ev,place=place,athlete=ath,country=cty,mark_raw=mk,wind=w))
for r in rows: r['event']=r['event'][0].upper()+r['event'][1:]
json.dump(rows,open('cg_ath.json','w'),indent=0)
import collections
print(len(rows)); c=collections.Counter((r['sex'],r['event']) for r in rows)
for k,v in sorted(c.items()): print(k,v)
print([r for r in rows if r['year']==2022 and r['event']=='100 metres'])
print(sum(1 for r in rows if r['country']=='AUS'))
