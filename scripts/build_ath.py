import json, re, csv, collections, os
OUT="/home/claude/site/data"
def wcsv(name, rows, fields=None):
    fields=fields or list(rows[0].keys())
    with open(os.path.join(OUT,name),'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); [w.writerow(r) for r in rows]
    print('wrote',name,len(rows))
def val(m):
    if m is None: return None
    m=m.strip().rstrip('w').strip()
    mm=re.match(r'^(\d+):(\d+):(\d+(?:\.\d+)?)$',m)
    if mm and int(mm.group(1))<10 and len(mm.group(3))==2: return int(mm.group(1))*60+int(mm.group(2))+int(mm.group(3))/100  # typo m:ss:hh
    if mm: return int(mm.group(1))*3600+int(mm.group(2))*60+float(mm.group(3))
    mm=re.match(r'^(\d+):(\d+(?:\.\d+)?)$',m)
    if mm: return int(mm.group(1))*60+float(mm.group(2))
    mm=re.match(r'^(\d+(?:\.\d+)?)',m)
    return float(mm.group(1)) if mm else None
cg=json.load(open('cg_ath.json')); oly=json.load(open('oly_ath.json'))
# event map CG -> Olympedia
EV={'100 metres':'100 metres','200 metres':'200 metres','400 metres':'400 metres','800 metres':'800 metres','1500 metres':'1,500 metres',
    '5000 metres':'5,000 metres','10,000 metres':'10,000 metres','110 metres hurdles':'110 metres Hurdles','100 metres hurdles':'100 / 80 metres Hurdles',
    '400 metres hurdles':'400 metres Hurdles','3000 metres steeplechase':'Steeplechase','High jump':'High Jump','Pole vault':'Pole Vault',
    'Long jump':'Long Jump','Triple jump':'Triple Jump','Shot put':'Shot Put','Discus throw':'Discus Throw','Hammer throw':'Hammer Throw','Javelin throw':'Javelin Throw'}
TRACK={'100 metres','200 metres','400 metres','800 metres','1500 metres','5000 metres','10,000 metres','110 metres hurdles','100 metres hurdles','400 metres hurdles','3000 metres steeplechase'}
NICE={'1500 metres':'1500 m','5000 metres':'5000 m','10,000 metres':'10,000 m','100 metres':'100 m','200 metres':'200 m','400 metres':'400 m','800 metres':'800 m',
      '110 metres hurdles':'110 m hurdles','100 metres hurdles':'100 m hurdles','400 metres hurdles':'400 m hurdles','3000 metres steeplechase':'Steeplechase'}
olyidx={}
for o in oly:
    key=o['event']
    for k,v in EV.items():
        if key==v or key.startswith(v+' ('): olyidx[(o['year'],o['sex'],v)]=o
rows=[]; skipped=[]
for r in cg:
    if r['place']!=1 or r['year']<1970: continue
    ev=r['event'] if r['event'] in EV else (r['event'][0].upper()+r['event'][1:] if r['event'][0].upper()+r['event'][1:] in EV else None)
    if ev is None:
        e2=r['event'].lower()
        ev=next((k for k in EV if k.lower()==e2),None)
    if ev is None: continue
    oy=r['year']-2
    o=olyidx.get((oy,r['sex'],EV[ev]))
    if not o or '1' not in o['res']: skipped.append((r['year'],r['sex'],ev,'no oly')); continue
    if r['sex']=='Women' and ev=='100 metres hurdles' and oy==1968: skipped.append((r['year'],r['sex'],ev,'80mH')); continue
    if r['sex']=='Men' and ev=='Javelin throw' and r['year']==1986: skipped.append((r['year'],r['sex'],ev,'new javelin')); continue
    cgv=val(r['mark_raw']); og=val(o['res']['1']['mark'])
    if ev in ('1500 metres','5000 metres','10,000 metres','3000 metres steeplechase') and cgv and cgv<60:  # typo mm.ss -> seconds
        mnt=int(cgv); cgv=mnt*60+round((cgv-mnt)*100,2)
    if og is not None and not re.search(r'[.:]', o['res']['1']['mark'] or ''): skipped.append((r['year'],r['sex'],ev,'bad oly mark')); continue
    ob=val(o['res'].get('3',{}).get('mark')); o8=val(o['res'].get('8',{}).get('mark'))
    if not o8:
        for pp in ('7','6'):
            if pp in o['res'] and val(o['res'][pp]['mark']): o8=val(o['res'][pp]['mark']); break
    if not cgv or not og: skipped.append((r['year'],r['sex'],ev,'no mark')); continue
    track=ev in TRACK
    def pct(ref):
        if not ref: return None
        return round((ref/cgv if track else cgv/ref)*100,2)
    better=lambda ref: ref is not None and ((cgv<=ref) if track else (cgv>=ref))
    if better(og): cat='Olympic gold standard'
    elif better(ob): cat='Olympic medal standard'
    elif o8 and better(o8): cat='Olympic final standard'
    elif o8: cat='Below Olympic final standard'
    else: cat='Below Olympic medal standard (no 8th-place mark)'
    rows.append(dict(cg_year=r['year'], oly_year=oy, sex=r['sex'], event=NICE.get(ev,ev), discipline='Track' if track else 'Field',
        cg_winner=r['athlete'], cg_country=r['country'], cg_mark=r['mark_raw'], wind_aided=r['wind'],
        oly_gold=o['res']['1']['name'], oly_gold_noc=o['res']['1']['noc'], oly_gold_mark=o['res']['1']['mark'],
        oly_bronze_mark=o['res'].get('3',{}).get('mark'), oly_8th_mark=o['res'].get('8',{}).get('mark') or (o['res'].get('7') or o['res'].get('6') or {}).get('mark'),
        pct_of_oly_gold=pct(og), pct_of_oly_bronze=pct(ob), standard=cat))
wcsv('athletics_vs_olympics.csv', rows)
print('skipped',skipped)
# medians
by=collections.defaultdict(list)
for r in rows: by[r['cg_year']].append(r['pct_of_oly_gold'])
import statistics
for y in sorted(by): print(y, len(by[y]), round(statistics.median(by[y]),2), collections.Counter(r['standard'] for r in rows if r['cg_year']==y))
