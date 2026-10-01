import json, csv, math, collections, os
exec(open('build_data.py').read().split('# ---------------- 1.')[0])  # imports, NAMES, GEO, HOST, helpers
games=list(csv.DictReader(open(OUT+'/games.csv')))
mt=list(csv.DictReader(open(OUT+'/medal_tables.csv')))

# ---------- flows: Canberra -> host city, aggregated per city ----------
city=collections.OrderedDict()
for g in games:
    k=g['city']
    d=city.setdefault(k, dict(city=k, lat=float(g['lat']), lon=float(g['lon']), host=g['host'], trips=0, athletes=0, games=[], aus_medals=0, home=g['home']))
    d['trips']+=1; d['athletes']+=int(g['aus_team']); d['games'].append(g['year']); d['aus_medals']+=int(g['aus_total'])
flows=[]
for d in city.values():
    d['games_label']=', '.join(d['games']); d['km']=round(hav(CANBERRA[0],CANBERRA[1],d['lat'],d['lon']))
    d['o_lat'],d['o_lon']=CANBERRA
    d.pop('games'); flows.append(d)
wcsv('flows_city.csv', flows)

# ---------- distance rings (true distance from Canberra), GeoJSON ----------
def dest(lat,lon,brg,dkm):
    R=6371.0; d=dkm/R; lat1=math.radians(lat); lon1=math.radians(lon); b=math.radians(brg)
    lat2=math.asin(math.sin(lat1)*math.cos(d)+math.cos(lat1)*math.sin(d)*math.cos(b))
    lon2=lon1+math.atan2(math.sin(b)*math.sin(d)*math.cos(lat1), math.cos(d)-math.sin(lat1)*math.sin(lat2))
    return [round((math.degrees(lon2)+540)%360-180,4), round(math.degrees(lat2),4)]
feats=[]
for km in (5000,10000,15000):
    pts=[dest(CANBERRA[0],CANBERRA[1],b,km) for b in range(0,361,2)]
    feats.append(dict(type='Feature',properties=dict(km=km,label=f'{km:,} km'),geometry=dict(type='LineString',coordinates=pts)))
json.dump(dict(type='FeatureCollection',features=feats),open(OUT+'/geo/distance_rings.geojson','w'))
# ring label positions (bearing ~ 300 deg, up-left)
wcsv('ring_labels.csv',[dict(km=km,label=f'{km:,} km',lon=dest(CANBERRA[0],CANBERRA[1],250,km)[0],lat=dest(CANBERRA[0],CANBERRA[1],250,km)[1]) for km in (5000,10000,15000)])

# ---------- population ----------
wb=json.load(open('/home/claude/raw/wb_pop_2024.json'))[1]
wbpop={r['countryiso3code']:r['value'] for r in wb if r['value']}
ONS={'ENG':58620101,'SCT':5546900,'WLS':3186581,'NIR':1927855}
ne=json.load(open('/home/claude/raw/geo/ne_50m_admin_0_map_units.geojson'))
nepop={f['properties']['GU_A3']:f['properties']['POP_EST'] for f in ne['features']}
def pop(gu):
    if gu in ONS: return ONS[gu],'ONS mid-2024'
    iso={'PNX':'PNG','ACA':'ATG'}.get(gu,gu)
    if iso in wbpop: return wbpop[iso],'World Bank 2024'
    if gu in nepop and nepop[gu]: return nepop[gu],'Natural Earth estimate'
    return None,None
# ---------- choropleth data: 2022 and 2026 medals per million ----------
rows=[]
for y in ('2022','2026'):
    for r in mt:
        if r['year']!=y: continue
        gu=GEO.get(r['code'])
        p,src=pop(gu)
        rows.append(dict(year=int(y), code=r['code'], gu=gu, nation=r['nation'], gold=r['gold'], silver=r['silver'], bronze=r['bronze'], total=r['total'], rank=r['rank'],
                         population=p, pop_source=src, per_million=round(int(r['total'])/p*1e6,4) if p else None))
wcsv('medals_per_capita.csv', rows)
# nations that took part (for grey 'competed, no medal'): list of Commonwealth Games Associations 2026 (from participating nations section)
from wget import fetch
import re
t=fetch('2026 Commonwealth Games')
i=t.find('Participating'); seg=t[i:i+20000]
part=sorted(set(re.findall(r'\{\{(?:flagCGF|flagIOC2team|flagCGFteam)\|([A-Z]{3})',seg)))
print('participants 2026', len(part))
# centroid points for small nations (so tiny islands are visible)
cent=[]
for f in ne['features']:
    gu=f['properties']['GU_A3']
    if gu not in set(GEO.values()): continue
    geom=f['geometry']; polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
    # largest ring bbox area & centroid
    best=max(polys,key=lambda p: len(p[0])); xs=[c[0] for c in best[0]]; ys=[c[1] for c in best[0]]
    area=sum(abs((max([c[0] for c in p[0]])-min([c[0] for c in p[0]]))*(max([c[1] for c in p[0]])-min([c[1] for c in p[0]]))) for p in polys)
    cent.append(dict(gu=gu, name=f['properties']['NAME'], lon=round(sum(xs)/len(xs),3), lat=round(sum(ys)/len(ys),3), bbox_area=round(area,3)))
wcsv('unit_centroids.csv', cent)

# ---------- extra polygons for multi-part nations (Bougainville = PNG, Barbuda = Antigua and Barbuda) ----------
rows=list(csv.DictReader(open(OUT+'/medals_per_capita.csv')))
for r in rows: r['primary']=1
extra=[]
for r in rows:
    for a,b in (('PNX','PNB'),('ACA','ACB')):
        if r['gu']==a: e=dict(r); e['gu']=b; e['primary']=0; extra.append(e)
wcsv('medals_per_capita.csv', rows+extra)
# (waffle data is built by build_waffle.py)
