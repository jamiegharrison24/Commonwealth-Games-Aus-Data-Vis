"""Build the tidy data files used by the Vega-Lite specs.
Sources: Wikipedia medal tables (which cite Commonwealth Sport / CGF), Wikipedia 'Australia at the ... Games' pages,
Olympedia (Olympic athletics results), World Bank WDI (population 2024), ONS mid-2024 (UK nations), Natural Earth."""
import json, csv, math, collections, re, os
from games import GAMES
from wget import fetch
from parse_mt import medals_template

OUT = "/home/claude/site/data"

NAMES = {
 'AUS':'Australia','BAH':'Bahamas','BAN':'Bangladesh','BAR':'Barbados','BER':'Bermuda','BGU':'British Guiana','BHK':'British Honduras',
 'BOT':'Botswana','CAN':'Canada','CAY':'Cayman Islands','CEY':'Ceylon','CMR':'Cameroon','COK':'Cook Islands','CYP':'Cyprus','DMA':'Dominica',
 'ENG':'England','FIJ':'Fiji','FRN':'Rhodesia & Nyasaland','GAB':'Gabon','GAM':'The Gambia','GGY':'Guernsey','GUE':'Guernsey','GHA':'Ghana',
 'GRN':'Grenada','GUY':'Guyana','HKG':'Hong Kong','IND':'India','IOM':'Isle of Man','IRE':'Ireland','IVB':'British Virgin Islands','JAM':'Jamaica',
 'JEY':'Jersey','KEN':'Kenya','KIR':'Kiribati','LCA':'Saint Lucia','LES':'Lesotho','MAL':'Malaya','MAS':'Malaysia','MAW':'Malawi','MLT':'Malta',
 'MOZ':'Mozambique','MRI':'Mauritius','NAM':'Namibia','NFI':'Norfolk Island','NFK':'Norfolk Island','NGR':'Nigeria','NIR':'Northern Ireland',
 'NIU':'Niue','NRH':'Northern Rhodesia','NRU':'Nauru','NZL':'New Zealand','PAK':'Pakistan','PNG':'Papua New Guinea','RSA':'South Africa',
 'RWA':'Rwanda','SAF':'South Africa','SAM':'Samoa','WSM':'Samoa','SCO':'Scotland','SEY':'Seychelles','SGP':'Singapore','SIN':'Singapore',
 'SKN':'Saint Kitts and Nevis','SOL':'Solomon Islands','SRH':'Southern Rhodesia','SRI':'Sri Lanka','SVG':'Saint Vincent','VIN':'Saint Vincent',
 'SWZ':'Eswatini','TAN':'Tanzania','TGA':'Tonga','TON':'Tonga','TRI':'Trinidad and Tobago','TTO':'Trinidad and Tobago','TUV':'Tuvalu',
 'UGA':'Uganda','VAN':'Vanuatu','WAL':'Wales','ZAM':'Zambia','ZIM':'Zimbabwe','TOG':'Togo','ATG':'Antigua and Barbuda','BIZ':'Belize',
 'BRU':'Brunei','GIB':'Gibraltar','MDV':'Maldives','SLE':'Sierra Leone','SHN':'Saint Helena','FLK':'Falkland Islands','TCA':'Turks and Caicos',
 'AIA':'Anguilla','MSR':'Montserrat','NGA':'Nigeria'}
# Commonwealth Games code -> Natural Earth map-unit code (GU_A3) and World Bank ISO3
GEO = {'AUS':'AUS','BAH':'BHS','BAN':'BGD','BAR':'BRB','BER':'BMU','BOT':'BWA','CAN':'CAN','CAY':'CYM','CMR':'CMR','COK':'COK','CYP':'CYP',
 'DMA':'DMA','ENG':'ENG','FIJ':'FJI','GAB':'GAB','GAM':'GMB','GGY':'GGY','GUE':'GGY','GHA':'GHA','GRN':'GRD','GUY':'GUY','IND':'IND','IOM':'IMN',
 'IVB':'VGB','JAM':'JAM','JEY':'JEY','KEN':'KEN','KIR':'KIR','LCA':'LCA','LES':'LSO','MAS':'MYS','MAW':'MWI','MLT':'MLT','MOZ':'MOZ','MRI':'MUS',
 'NAM':'NAM','NFI':'NFK','NFK':'NFK','NGR':'NGA','NIR':'NIR','NIU':'NIU','NRU':'NRU','NZL':'NZL','PAK':'PAK','PNG':'PNX','RSA':'ZAF','RWA':'RWA',
 'SAM':'WSM','WSM':'WSM','SCO':'SCT','SEY':'SYC','SGP':'SGP','SIN':'SGP','SKN':'KNA','SOL':'SLB','SRI':'LKA','SVG':'VCT','VIN':'VCT','SWZ':'SWZ',
 'TAN':'TZA','TGA':'TON','TON':'TON','TRI':'TTO','TTO':'TTO','TUV':'TUV','UGA':'UGA','VAN':'VUT','WAL':'WLS','ZAM':'ZMB','TOG':'TGO','ATG':'ACA',
 'BIZ':'BLZ','BRU':'BRN','GIB':'GIB','MDV':'MDV','SLE':'SLE','SHN':'SHN','FLK':'FLK','TCA':'TCA','AIA':'AIA','MSR':'MSR'}
WB_ISO = {'ENG':None,'SCT':None,'WLS':None,'NIR':None,'JEY':None,'GGY':None,'NFK':None,'NIU':None,'COK':None,'SHN':None,'FLK':None,'AIA':None,'MSR':None}

HOST = {1930:('Hamilton','CAN',43.2557,-79.8711),1934:('London','ENG',51.5074,-0.1278),1938:('Sydney','AUS',-33.8688,151.2093),
 1950:('Auckland','NZL',-36.8485,174.7633),1954:('Vancouver','CAN',49.2827,-123.1207),1958:('Cardiff','WAL',51.4816,-3.1791),
 1962:('Perth','AUS',-31.9523,115.8613),1966:('Kingston','JAM',17.9714,-76.7931),1970:('Edinburgh','SCO',55.9533,-3.1883),
 1974:('Christchurch','NZL',-43.5321,172.6362),1978:('Edmonton','CAN',53.5461,-113.4938),1982:('Brisbane','AUS',-27.4698,153.0251),
 1986:('Edinburgh','SCO',55.9533,-3.1883),1990:('Auckland','NZL',-36.8485,174.7633),1994:('Victoria','CAN',48.4284,-123.3656),
 1998:('Kuala Lumpur','MAS',3.1390,101.6869),2002:('Manchester','ENG',53.4808,-2.2426),2006:('Melbourne','AUS',-37.8136,144.9631),
 2010:('Delhi','IND',28.6139,77.2090),2014:('Glasgow','SCO',55.8642,-4.2518),2018:('Gold Coast','AUS',-28.0167,153.4000),
 2022:('Birmingham','ENG',52.4862,-1.8904),2026:('Glasgow','SCO',55.8642,-4.2518)}
CANBERRA = (-35.2809, 149.1300)

def hav(lat1, lon1, lat2, lon2):
    R=6371.0; p1,p2=math.radians(lat1),math.radians(lat2); dp=p2-p1; dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def wcsv(name, rows, fields=None):
    fields = fields or list(rows[0].keys())
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); [w.writerow(r) for r in rows]
    print('wrote', name, len(rows))

# ---------------- 1. medal tables for every Games ----------------
mt = []
for y, c, n in GAMES:
    for title in [f"{y} {n} medal table", f"{y} {n}"]:
        t = fetch(title)
        if not t: continue
        r = medals_template(t)
        if r and r[0]:
            for code, v in r[0].items():
                g,s,b = v.get('gold',0), v.get('silver',0), v.get('bronze',0)
                mt.append(dict(year=y, code=code, nation=NAMES.get(code, code), gold=g, silver=s, bronze=b, total=g+s+b))
            break
# ranks (gold, then silver, then bronze; ties share rank)
by_year = collections.defaultdict(list)
for r in mt: by_year[r['year']].append(r)
for y, rows in by_year.items():
    rows.sort(key=lambda r: (-r['gold'], -r['silver'], -r['bronze']))
    prev=None; rank=0
    for i, r in enumerate(rows, 1):
        key=(r['gold'],r['silver'],r['bronze'])
        if key!=prev: rank=i; prev=key
        r['rank']=rank
wcsv('medal_tables.csv', sorted(mt, key=lambda r:(r['year'], r['rank'])))

# ---------------- 2. Australia per Games ----------------
aus_page = fetch("Australia at the Commonwealth Games")
team = {}
for m in re.finditer(r"\[\[(?:19|20)\d\d[^|\]]*\|(\d{4}) [^\]]+\]\]\s*\|\|([^\n]+)", aus_page):
    y=int(m.group(1)); cells=[c.strip() for c in m.group(2).split('||')]
    nums=[re.sub(r'.*\|\s*','',c) for c in cells]
    try: team[y]=int(re.sub(r'\D','',nums[5]))
    except: pass
team[2026]=255
games=[]
for y, c, n in GAMES:
    rows=by_year[y]; aus=[r for r in rows if r['code']=='AUS'][0]
    tot=sum(r['total'] for r in rows); gold=sum(r['gold'] for r in rows)
    top=rows[0]
    city, hc, lat, lon = HOST[y]
    games.append(dict(year=y, city=city, host_code=hc, host=NAMES[hc], lat=lat, lon=lon, label=f"{city} {y}",
        edition=n.replace('Games','Games'), events=gold, medals_awarded=tot, nations_medalled=len(rows), top_nation=top['nation'], top_code=top['code'],
        aus_gold=aus['gold'], aus_silver=aus['silver'], aus_bronze=aus['bronze'], aus_total=aus['total'], aus_rank=aus['rank'],
        aus_share=round(aus['total']/tot,4), aus_gold_share=round(aus['gold']/gold,4), aus_team=team.get(y),
        medals_per_athlete=round(aus['total']/team[y],3) if team.get(y) else None,
        home='Home' if hc=='AUS' else 'Away', km_from_canberra=round(hav(CANBERRA[0],CANBERRA[1],lat,lon))))
wcsv('games.csv', games)

# ---------------- 3. Australia medals by sport and Games ----------------
exec(open('/home/claude/raw/parse_sport.py').read().split('if __name__')[0])
GROUP = {'swimming':'Aquatics','aquatics':'Aquatics','diving':'Aquatics','synchronised swimming':'Aquatics','synchronized swimming':'Aquatics','water polo':'Aquatics',
 'athletics':'Athletics','cycling':'Cycling','track cycling':'Cycling','shooting':'Shooting','weightlifting':'Weightlifting','para powerlifting':'Weightlifting',
 'powerlifting':'Weightlifting','gymnastics':'Gymnastics','artistic gymnastics':'Gymnastics','rhythmic gymnastics':'Gymnastics','boxing':'Boxing',
 'wrestling':'Wrestling','lawn bowls':'Lawn bowls','bowls':'Lawn bowls','rowing':'Rowing','fencing':'Fencing','squash':'Squash','hockey':'Hockey',
 'field hockey':'Hockey','netball':'Netball','judo':'Judo','badminton':'Badminton','table tennis':'Table tennis','tennis':'Tennis','triathlon':'Triathlon',
 'basketball':'Basketball','3x3 basketball':'Basketball','rugby sevens':'Rugby sevens','cricket':'Cricket','archery':'Archery','tenpin bowling':'Ten-pin bowling',
 'ten-pin bowling':'Ten-pin bowling','beach volleyball':'Beach volleyball'}
sport_rows=[]
def add(y, sport, g, s, b, note=''):
    grp=GROUP.get(sport.lower().strip())
    if not grp: raise SystemExit(f'unmapped sport {sport} {y}')
    sport_rows.append(dict(year=y, sport=grp, gold=g, silver=s, bronze=b, note=note))
early = {1930:[('Athletics',0,3,1),('Boxing',0,1,0),('Rowing',1,0,0),('Aquatics',2,0,0)],
         1934:[('Athletics',1,1,2),('Boxing',1,0,0),('Aquatics',3,2,0),('Wrestling',2,0,0),('Cycling',1,1,0)],
         1938:[('Athletics',6,11,12),('Boxing',1,1,2),('Lawn bowls',0,1,2),('Rowing',3,1,0),('Aquatics',7,3,6),('Wrestling',6,0,0),('Cycling',2,2,0)]}
for y, c, n in GAMES:
    if y in early:
        for sp,g,s,b in early[y]: add(y,sp,g,s,b,'from per-sport pages')
        continue
    if y==2010:
        import importlib.util, sys
        sys.argv=['x']
        from medalists2 import count
        cc=count(f"Australia at the {y} {n}")
        for sp in sorted(set(k[0] for k in cc)):
            add(y, sp, cc[(sp,'gold')], cc[(sp,'silver')], cc[(sp,'bronze')], 'from medallist list')
        continue
    r = by_sport(fetch(f"Australia at the {y} {n}"))
    for x in r:
        sp=x['sport']
        if y==2006 and sp=='Athletics':  # Australia page table is incomplete; use Athletics at the 2006 CG medal table
            add(y,sp,16,12,13,'athletics from event medal table'); continue
        add(y, sp, x['gold'], x['silver'], x['bronze'])
# aggregate duplicates within group
agg=collections.OrderedDict()
for r in sport_rows:
    k=(r['year'],r['sport'])
    if k not in agg: agg[k]=dict(year=r['year'],sport=r['sport'],gold=0,silver=0,bronze=0,note=r['note'])
    for m in ('gold','silver','bronze'): agg[k][m]+=r[m]
sport_rows=list(agg.values())
for r in sport_rows: r['total']=r['gold']+r['silver']+r['bronze']
wcsv('aus_sport_games.csv', sport_rows, ['year','sport','gold','silver','bronze','total','note'])
# check
for g in games:
    s=[r for r in sport_rows if r['year']==g['year']]
    tt=(sum(r['gold'] for r in s),sum(r['silver'] for r in s),sum(r['bronze'] for r in s))
    if tt!=(g['aus_gold'],g['aus_silver'],g['aus_bronze']): print('  sport sum mismatch',g['year'],tt,(g['aus_gold'],g['aus_silver'],g['aus_bronze']))

# all-time by sport (for the marimekko)
at=collections.defaultdict(lambda: dict(gold=0,silver=0,bronze=0))
for r in sport_rows:
    for m in ('gold','silver','bronze'): at[r['sport']][m]+=r[m]
alltime=[dict(sport=k, **v, total=sum(v.values())) for k,v in at.items()]
alltime.sort(key=lambda r:-r['total'])
wcsv('aus_sport_alltime.csv', alltime)

json.dump(dict(games=games), open('/home/claude/raw/_games.json','w'))

# ---------------- 4. Most decorated Australians ----------------
R=[r for r in json.load(open('/home/claude/raw/aus_medalists_raw.json')) if r['people']]
per=collections.defaultdict(lambda: collections.defaultdict(collections.Counter)); spc=collections.defaultdict(collections.Counter)
def sport_of(r):
    m=re.search(r'\[\[(?:[^|\]]*\|)?(Swimming|Aquatics|Shooting|Athletics|Cycling|Gymnastics|Artistic gymnastics|Diving|Squash|Weightlifting|Lawn bowls|Boxing|Wrestling|Rowing|Fencing|Hockey|Netball|Judo|Triathlon|Badminton|Table tennis|Tennis|Archery)\]\]',r['row'])
    m=m or re.search(r'\|\|\s*(Swimming|Aquatics|Shooting|Athletics|Cycling|Gymnastics|Diving|Squash|Weightlifting)\s*\|\|',r['row'])
    return m.group(1) if m else None
for r in R:
    for p in r['people']:
        per[p][r['year']][r['medal']]+=1
        s=sport_of(r)
        if s: spc[p][s]+=1
tot={p:sum(sum(c.values()) for c in d.values()) for p,d in per.items()}
gold={p:sum(c['gold'] for c in d.values()) for p,d in per.items()}
top=sorted(tot, key=lambda p:(-tot[p],-gold[p]))[:16]
SPN={'Aquatics':'Swimming','Artistic gymnastics':'Gymnastics'}
greats=[]
for rank,p in enumerate(top,1):
    sp=spc[p].most_common(1)[0][0] if spc[p] else ''
    sp=SPN.get(sp,sp)
    if p.startswith('Ivan Lund'): sp='Fencing'
    name=re.sub(r'\s*\(.*\)$','',p)
    for y,c in sorted(per[p].items()):
        greats.append(dict(athlete=name, sport=sp, year=y, gold=c['gold'], silver=c['silver'], bronze=c['bronze'], medals=sum(c.values()),
                           career_total=tot[p], career_gold=gold[p], first=min(per[p]), last=max(per[p]), rank=rank))
wcsv('aus_greats.csv', greats)
for p in top: print(p, tot[p], gold[p], spc[p].most_common(2))
