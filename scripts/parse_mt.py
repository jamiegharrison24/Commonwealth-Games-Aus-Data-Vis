import re
from games import GAMES
from wget import fetch
def medals_template(t):
    i=t.find("{{Medals table")
    if i<0: return None
    # find matching end
    depth=0;j=i
    while j<len(t):
        if t.startswith("{{",j): depth+=1; j+=2; continue
        if t.startswith("}}",j):
            depth-=1; j+=2
            if depth==0: break
            continue
        j+=1
    s=t[i:j]
    d={}
    for k,code,v in re.findall(r'\|\s*(gold|silver|bronze)_([A-Z]{3})\s*=\s*(\d+)',s):
        d.setdefault(code,{})[k]=int(v)
    host=re.search(r'\|\s*host\s*=\s*([A-Z]{3})',s)
    return d, host.group(1) if host else None, s
if __name__=="__main__":
    out={}
    for y,c,n in GAMES:
        for title in [f"{y} {n} medal table", f"{y} {n}"]:
            t=fetch(title)
            if not t: continue
            r=medals_template(t)
            if r and r[0]:
                out[y]=r; break
        d=out.get(y,({},None,''))[0]
        aus=d.get('AUS'); tot=sum(v.get('gold',0) for v in d.values())
        print(y, len(d), 'AUS',aus, 'totalgold',tot, 'host',out.get(y,(0,None))[1])
    