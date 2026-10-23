"""Build a single self-contained preview HTML (libraries, CSS, specs and data inlined)."""
import json, csv, re, glob, os
SITE='/home/claude/site'; T='/home/claude/test/node_modules'
def load_csv(path, parse):
    rows=list(csv.DictReader(open(os.path.join(SITE,path))))
    for r in rows:
        for k,t in (parse or {}).items():
            if r.get(k) not in (None,''): r[k]=float(r[k]) if '.' in r[k] else int(r[k])
            elif k in r: r[k]=None
    return rows
def inline(o):
    if isinstance(o,dict):
        if 'url' in o and isinstance(o['url'],str) and o['url'].startswith('data/'):
            url=o.pop('url'); fmt=o.get('format',{})
            if url.endswith('.csv'):
                o['values']=load_csv(url, fmt.get('parse')); o.pop('format',None)
            elif url.endswith('.topojson'):
                o['values']=json.load(open(os.path.join(SITE,url)))
            elif url.endswith('.geojson'):
                d=json.load(open(os.path.join(SITE,url))); o['values']=d[fmt.get('property','features')]; o.pop('format',None)
        for v in list(o.values()): inline(v)
    elif isinstance(o,list):
        for v in o: inline(v)
    return o
specs={os.path.basename(f)[:-8]: inline(json.load(open(f))) for f in sorted(glob.glob(SITE+'/js/specs/*.vg.json'))}
html=open(SITE+'/index.html').read()
css=open(SITE+'/css/style.css').read()
html=html.replace('<link rel="stylesheet" href="css/style.css">','<style>\n'+css+'\n</style>')
for lib,path in [('vega@5.33.1','vega/build/vega.min.js'),('vega-lite@5.23.0','vega-lite/build/vega-lite.min.js'),('vega-embed@6.29.0','vega-embed/build/vega-embed.min.js')]:
    code=open(os.path.join(T,path)).read().replace('</script>','<\\/script>')
    html=html.replace(f'<script src="https://cdn.jsdelivr.net/npm/{lib}"></script>','<script>'+code+'</script>')
main=open(SITE+'/js/main.js').read()
main="window.INLINE_SPECS = "+json.dumps(specs,separators=(',',':'))+";\n"+main
html=html.replace('<script src="js/main.js"></script>','<script>'+main.replace('</script>','<\\/script>')+'</script>')
html=html.replace('<p class="kicker">','<p class="kicker" style="color:#b0561a">Offline preview build · the GitHub Pages version loads the same charts from js/specs/ and data/</p><p class="kicker">',1)
open('/home/claude/preview/top_of_the_table_preview.html','w').write(html)
print(len(html)/1e6,'MB')
