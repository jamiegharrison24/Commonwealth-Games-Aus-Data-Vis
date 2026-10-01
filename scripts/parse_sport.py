import re, json
from games import GAMES
from wget import fetch
from parse_mt import medals_template
def clean(x):
    x=re.sub(r'<ref[^>]*/>','',x); x=re.sub(r'<ref.*?</ref>','',x,flags=re.S)
    x=re.sub(r'\{\{(?:GamesSport|flagIOCsport|sport)\|([^|}]+)[^}]*\}\}',r'\1',x)
    x=re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]',r'\1',x)
    x=re.sub(r"'''?",'',x); x=re.sub(r'\{\{[^}]*\}\}','',x)
    x=re.sub(r'^\s*(?:align|style|bgcolor|scope)[^|]*\|(?!\|)','',x.strip())
    return x.strip()
def by_sport(t):
    i=[m.start() for m in re.finditer(r'by sport',t,re.I)]
    for st in i:
        seg=t[st:st+15000]
        tb0=t.rfind("{|",0,st)
        if tb0>=0 and t.find("\n|}",tb0)>st: seg=t[tb0:tb0+20000]
        # template form
        if "{{Medals table" in seg[:3000]:
            j=seg.find("{{Medals table"); s=seg[j:seg.find("\n}}",j)+3]
            rows={}
            for k,n,v in re.findall(r'(gold|silver|bronze)_(\d+)\s*=\s*(\d+)',s): rows.setdefault(n,{})[k]=int(v)
            for n,nm in re.findall(r'name_(\d+)\s*=\s*([^\n|]*(?:\{\{[^}]*\}\})?[^\n|]*)',s):
                if n in rows: rows[n]['sport']=clean(nm)
            res=[r for r in rows.values() if 'sport' in r]
            if res: return res
        j=seg.find("{|")
        if j<0: continue
        tb=seg[j:seg.find("\n|}",j)]
        res=[]
        for row in re.split(r'\n\|-[^\n]*',tb)[1:]:
            cells=[]
            for line in row.split('\n'):
                line=line.strip()
                if not line or line.startswith('|+'): continue
                if line[0] in '|!': line=line[1:]
                for c in re.split(r'\|\||!!',line): cells.append(clean(c))
            cells=[c for c in cells if c!='']
            if not cells: continue
            nums=[c for c in cells[1:] if re.fullmatch(r'\d+',c)]
            name=cells[0]
            if re.search(r'[A-Za-z]',name) and len(nums)>=3 and not re.search(r'total|sport',name,re.I):
                res.append({'sport':name,'gold':int(nums[0]),'silver':int(nums[1]),'bronze':int(nums[2])})
        if res: return res
    return None
if __name__=="__main__":
    allr={}
    for y,c,n in GAMES:
        t=fetch(f"Australia at the {y} {n}")
        r=by_sport(t) if t else None
        mt=medals_template(fetch(f"{y} {n} medal table") or fetch(f"{y} {n}"))
        mt=mt[0].get('AUS') if mt else None
        if r:
            g=sum(x['gold'] for x in r); s=sum(x['silver'] for x in r); b=sum(x['bronze'] for x in r)
            ok=(g,s,b)==(mt['gold'],mt['silver'],mt['bronze'])
            print(y, len(r), (g,s,b), mt, 'OK' if ok else 'MISMATCH', [x['sport'] for x in r])
            allr[y]=r
        else: print(y,'NONE')
    json.dump(allr,open('aus_by_sport_raw.json','w'),indent=1)
