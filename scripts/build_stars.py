import json, re, csv, unicodedata, collections, os
OUT="/home/claude/site/data"
oly=json.load(open('oly_ath.json')); cg=json.load(open('cg_ath.json'))
def norm(n):
    n=unicodedata.normalize('NFKD',n or '').encode('ascii','ignore').decode().lower()
    n=re.sub(r'\(.*?\)','',n); n=re.sub(r'[^a-z ]',' ',n); p=n.split()
    return p
def key(n):
    p=norm(n); return (p[-1], p[0][0]) if p else None
CW={'AUS','CAN','GBR','NZL','JAM','KEN','NGR','IND','TTO','TRI','BAH','BAR','BER','UGA','TAN','ZAM','BOT','GHA','MAS','SGP','SRI','CYP','GRN','SKN','LCA','FIJ','MRI','SEY','LES','SWZ','MAW','PNG','SAM','TGA','VAN','SOL','NRU','BAN','GUY','DMA','ANT','VIN','IVB','CAY','BIZ','MLT','GAM','SLE','BRU','MDV','COK','PLW'}
def is_cw(noc, year):
    if noc=='RSA': return year>=1994
    if noc=='NAM': return year>=1994
    if noc=='CMR': return year>=1998
    if noc=='MOZ': return year>=1998
    if noc=='RWA': return year>=2010
    if noc in ('GAB','TOG'): return year>=2026
    if noc=='ZIM': return 1982<=year<=2002
    if noc=='PAK': return year<=1970 or year>=1990
    if noc=='FIJ': return not (1990<=year<=1998)
    return noc in CW
# CG athletics medallists by year (individual events, all places), names keyed
cgk=collections.defaultdict(set)
for r in cg:
    if r['athlete'] and r['place']<=3: cgk[r['year']].add(key(r['athlete']))
EVOK=['100 metres','200 metres','400 metres','800 metres','1,500 metres','5,000 metres','10,000 metres','110 metres Hurdles','100 / 80 metres Hurdles','400 metres Hurdles','Steeplechase','High Jump','Pole Vault','Long Jump','Triple Jump','Shot Put','Discus Throw','Hammer Throw','Javelin Throw','Decathlon','Heptathlon']
rows=[]
for o in oly:
    if not any(o['event'].startswith(e) for e in EVOK): continue
    cgy=o['year']+2
    if cgy<1970 or cgy>2026: continue
    for p in ('1','2','3'):
        x=o['res'].get(p)
        if not x: continue
        if not is_cw(x['noc'], cgy): continue
        k=key(x['name'])
        medalled = k in cgk[cgy]
        rows.append(dict(cg_year=cgy, oly_year=o['year'], athlete=x['name'], noc=x['noc'], event=o['event'].replace(' (100 m)',''), sex=o['sex'], oly_medal={'1':'gold','2':'silver','3':'bronze'}[p], cg_medal='Won a Commonwealth medal' if medalled else 'No Commonwealth medal'))
# de-duplicate athletes per CG year (someone with 2 Olympic medals counts once, with their best)
seen={}; uniq=[]
for r in sorted(rows,key=lambda r:(r['cg_year'],['gold','silver','bronze'].index(r['oly_medal']))):
    k=(r['cg_year'],key(r['athlete']))
    if k in seen: continue
    seen[k]=1; uniq.append(r)
for y in sorted(set(r['cg_year'] for r in uniq)):
    s=[r for r in uniq if r['cg_year']==y]; m=sum(r['cg_medal'].startswith('Won') for r in s)
    print(y,len(s),m,round(m/len(s)*100))
# order within year for unit chart
out=[]
for y in sorted(set(r['cg_year'] for r in uniq)):
    s=sorted([r for r in uniq if r['cg_year']==y], key=lambda r:(0 if r['cg_medal'].startswith('Won') else 1, r['athlete']))
    for i,r in enumerate(s): r['i']=i; out.append(r)
with open(OUT+'/olympians_at_cg.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); [w.writerow(r) for r in out]
print(len(out))
