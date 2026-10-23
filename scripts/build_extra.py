import csv, os, random, hashlib
OUT="/home/claude/site/data"
g=list(csv.DictReader(open(OUT+'/games.csv')))
ys=[int(r['year']) for r in g]; by={int(r['year']):r for r in g}
rows=[]
for r in g:
    if r['home']!='Home': continue
    y=int(r['year']); i=ys.index(y); lab=f"{r['city']} {y}"
    for kind,yy in (('Games before (away)',ys[i-1]),('Home Games',y),('Games after (away)',ys[i+1] if i+1<len(ys) else None)):
        if yy is None: continue
        rr=by[yy]
        rows.append(dict(home_games=lab, home_year=y, kind=kind, games=f"{rr['city']} {yy}", share=rr['aus_share'], gold_share=rr['aus_gold_share'], team=rr['aus_team']))
with open(OUT+'/home_advantage.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); [w.writerow(x) for x in rows]
# deterministic jitter for strip plot
a=list(csv.DictReader(open(OUT+'/athletics_vs_olympics.csv')))
for r in a:
    h=int(hashlib.md5((r['event']+r['sex']+r['cg_year']).encode()).hexdigest(),16)
    r['jitter']=round(((h%1000)/1000-0.5)*0.8,3)
    if r['standard'].startswith('Below Olympic medal standard'): r['standard']='Below Olympic final standard'
with open(OUT+'/athletics_vs_olympics.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(a[0].keys())); w.writeheader(); [w.writerow(x) for x in a]
print(len(rows), len(a))
