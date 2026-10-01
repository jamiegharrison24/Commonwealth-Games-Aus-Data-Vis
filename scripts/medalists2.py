import re, collections, sys
from wget import fetch
def count(title):
    t=fetch(title)
    i=re.search(r'^==\s*Medal(?:l)?ists\s*==',t,re.M|re.I).start()
    j=t.find('\n==',i+5)
    sec=t[i:j]
    c=collections.Counter(); n=0
    for r in re.split(r'\n\|-[^\n]*',sec):
        mm=re.search(r'\{\{\s*(gold|silver|bronze)\s*medal\s*\}\}',r,re.I)
        if not mm: continue
        sp=re.search(r'\|\|\s*\[\[[^|\]]*\|([^\]]+)\]\]',r) or re.search(r'\|\|\s*([A-Za-z ]+?)\s*\|\|',r)
        c[(sp.group(1).strip() if sp else '?',mm.group(1).lower())]+=1
    return c
if __name__=="__main__":
    c=count(sys.argv[1]); T=[0,0,0]
    for s in sorted(set(k[0] for k in c)):
        v=[c[(s,m)] for m in ('gold','silver','bronze')]; T=[a+b for a,b in zip(T,v)]; print(s,v)
    print('TOTAL',T)
