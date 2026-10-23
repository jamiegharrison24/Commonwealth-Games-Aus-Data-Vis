import re, html, os, time, subprocess, json
UA="Mozilla/5.0 (FIT3179 student project)"
def get(url, fn):
    if os.path.exists(fn) and os.path.getsize(fn)>1000: return open(fn).read()
    for a in range(4):
        r=subprocess.run(["curl","-s","-m","40","-A",UA,url],capture_output=True,text=True)
        if len(r.stdout)>1000: open(fn,"w").write(r.stdout); time.sleep(1); return r.stdout
        time.sleep(5*(a+1))
    return ""
ED={1968:17,1972:18,1976:19,1980:20,1984:21,1988:22,1992:23,1996:24,2000:25,2004:26,2008:53,2012:54,2016:59,2020:61,2024:63}
KEEP=["100 metres","200 metres","400 metres","800 metres","1,500 metres","5,000 metres","10,000 metres","110 metres Hurdles","100 / 80 metres Hurdles","100 metres Hurdles","400 metres Hurdles","Steeplechase","High Jump","Pole Vault","Long Jump","Triple Jump","Shot Put","Discus Throw","Hammer Throw","Javelin Throw","Decathlon","Heptathlon","Pentathlon"]
def cells(tr):
    return [html.unescape(re.sub(r'<[^>]+>','',c)).strip() for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>',tr,re.S)]
if __name__=="__main__":
    out=[]
    for y,e in ED.items():
        s=get(f"https://www.olympedia.org/editions/{e}/sports/ATH",f"oly/e{e}_ath.html")
        evs=dict()
        for rid,name in re.findall(r'<a href="/results/(\d+)">([^<]+)</a>',s):
            evs.setdefault(name,rid)
        for name,rid in evs.items():
            if ', ' not in name: continue
            ev,sex=name.rsplit(', ',1)
            if not any(ev.startswith(k) for k in KEEP) or 'Relay' in ev: continue
            r=get(f"https://www.olympedia.org/results/{rid}",f"oly/r{rid}.html")
            i=r.find('<table class="table table-striped">'); tb=r[i:r.find('</table>',i)]
            rows=re.findall(r'<tr[^>]*>(.*?)</tr>',tb,re.S)
            hdr=cells(rows[0]) if rows else []
            res={}
            for tr in rows[1:]:
                c=cells(tr)
                if not c: continue
                pos=c[0]
                if pos in ('1','2','3','8','=8','=3','=1'):
                    p=pos.strip('=')
                    if p in res: continue
                    # final mark: find 'Final' column or last cell with digits
                    marks=[x for x in c[4:] if re.search(r'\d',x)]
                    fm=None
                    if 'Final' in hdr:
                        fi=hdr.index('Final'); 
                        if fi<len(c): fm=c[fi]
                    if not fm or not re.search(r'\d',fm): fm=marks[-1] if marks else None
                    res[p]={'name':c[2],'noc':c[3],'mark':fm}
            out.append({'year':y,'event':ev,'sex':sex,'rid':rid,'res':res})
            print(y,sex,ev,{k:v['mark'] for k,v in res.items()})
    json.dump(out,open('oly_ath.json','w'),indent=1)
    