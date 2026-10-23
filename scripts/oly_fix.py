import re, html, json, glob
from oly import ED, KEEP, cells
out=[]
def parse_table(tb, mark_col=None):
    rows=re.findall(r'<tr[^>]*>(.*?)</tr>',tb,re.S)
    if not rows: return {}
    hdr=cells(rows[0]); res={}
    for tr in rows[1:]:
        c=cells(tr)
        if not c: continue
        p=c[0].strip('=').strip()
        if p in ('1','2','3','4','5','6','7','8') and p not in res:
            if mark_col is not None: fm=c[mark_col] if mark_col<len(c) else None
            else:
                fm=None
                if 'Final' in hdr:
                    fi=hdr.index('Final'); fm=c[fi] if fi<len(c) else None
                else:
                    ds=[x for x in c[4:] if re.search(r'\d',x) and x not in ('Gold','Silver','Bronze')]
                    fm=ds[0] if ds else None
            res[p]={'name':c[2],'noc':c[3],'mark':fm}
    return res
for y,e in ED.items():
    s=open(f"oly/e{e}_ath.html").read()
    evs={}
    for rid,name in re.findall(r'<a href="/results/(\d+)">([^<]+)</a>',s): evs.setdefault(name,rid)
    for name,rid in evs.items():
        if ', ' not in name: continue
        ev,sex=name.rsplit(', ',1)
        if not any(ev.startswith(k) for k in KEEP) or 'Relay' in ev or 'Wheelchair' in ev: continue
        r=open(f"oly/r{rid}.html").read()
        i=r.find('<table class="table table-striped">'); tb=r[i:r.find('</table>',i)]
        res=parse_table(tb)
        ok=res.get('1') and res['1']['mark'] and re.search(r'\d',res['1']['mark'])
        if not ok:
            # find final round heading
            heads=[(m.start(),html.unescape(re.sub('<[^>]+>','',m.group(1))).strip()) for m in re.finditer(r'<h[1-5][^>]*>(.*?)</h[1-5]>',r)]
            fin=[h for h in heads if re.match(r'^Final',h[1])]
            if fin:
                st=fin[-1][0]; j=r.find('<table class="table table-striped">',st); tb=r[j:r.find('</table>',j)]
                res2=parse_table(tb, mark_col=4)
                if res2.get('1'): res=res2
        for k in res:
            m=res[k]['mark']
            if m: res[k]['mark']=re.sub(r'\s*\(.*?\)','',m).strip()
        out.append({'year':y,'event':ev,'sex':sex,'rid':rid,'res':res})
json.dump(out,open('oly_ath.json','w'),indent=0)
bad=[(o['year'],o['sex'],o['event']) for o in out if not (o['res'].get('1') and o['res']['1']['mark'] and re.search(r'\d',o['res']['1']['mark']))]
print(len(out),'bad',bad)
print([ (o['year'],o['event'],o['sex'],{k:v['mark'] for k,v in o['res'].items()}) for o in out if o['event'].startswith('100 metres') and o['sex']=='Men'])
