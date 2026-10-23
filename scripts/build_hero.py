"""Hero 'medal skyline': one row per Australian medal, stacked in 5-wide columns per Games (gold at the bottom)."""
import csv
g=list(csv.DictReader(open('/home/claude/site/data/games.csv')))
out=[]
for r in g:
    k=0
    for m in ('gold','silver','bronze'):
        for _ in range(int(r['aus_'+m])):
            out.append(dict(year=r['year'], label=r['label'], medal=m.capitalize(), k=k, col=k%5, row=k//5, games_total=r['aus_total'], games_gold=r['aus_gold']))
            k+=1
with open('/home/claude/site/data/aus_medal_units.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); [w.writerow(x) for x in out]
print(len(out), max(x['row'] for x in out))
# host cities with their Games years (for zoomed labels)
city={}
for r in g:
    c=city.setdefault(r['city'],dict(city=r['city'],lat=r['lat'],lon=r['lon'],years=[]))
    c['years'].append(r['year'])
rows=[dict(city=c['city'],lat=c['lat'],lon=c['lon'],years=' · '.join(c['years']),label=c['city']+' '+' · '.join(c['years'])) for c in city.values()]
with open('/home/claude/site/data/host_city_labels.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(x) for x in rows]
print(len(rows))
