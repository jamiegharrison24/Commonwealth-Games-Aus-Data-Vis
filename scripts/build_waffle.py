"""Waffle data: one row per medal at Birmingham 2022 and Glasgow 2026."""
import csv
mt=list(csv.DictReader(open('/home/claude/site/data/medal_tables.csv')))
grp=lambda c: {'AUS':'Australia','ENG':'England','CAN':'Canada'}.get(c,'Rest of the Commonwealth')
order={'Australia':0,'England':1,'Canada':2,'Rest of the Commonwealth':3}
out=[]
for y in ('2022','2026'):
    cells=[]
    for r in sorted([r for r in mt if r['year']==y], key=lambda r:int(r['rank'])):
        for m in ('gold','silver','bronze'):
            for _ in range(int(r[m])): cells.append((order[grp(r['code'])],['gold','silver','bronze'].index(m),int(r['rank']),grp(r['code']),r['nation'],m))
    cells.sort(key=lambda x:(x[0],x[1],x[2]))
    for k,c in enumerate(cells):
        out.append(dict(games='Birmingham 2022' if y=='2022' else 'Glasgow 2026', i=k, col=k%25, row=k//25, group=c[3], nation=c[4], medal=c[5]))
with open('/home/claude/site/data/waffle_2022_2026.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys())); w.writeheader(); [w.writerow(x) for x in out]
