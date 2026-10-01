import sys, os, time, re, urllib.parse, subprocess
UA="FIT3179-student-dataviz/1.0 (Monash University coursework; jhar0038@student.monash.edu)"
def fetch(title, depth=0):
    fn="/home/claude/raw/wiki/"+re.sub(r'[^A-Za-z0-9_-]','_',title)+".txt"
    if os.path.exists(fn) and os.path.getsize(fn)>0:
        t=open(fn).read()
    else:
        for attempt in range(5):
            url="https://en.wikipedia.org/w/index.php?title="+urllib.parse.quote(title.replace(' ','_'))+"&action=raw"
            r=subprocess.run(["curl","-sL","-A",UA,"-w","\n%{http_code}",url],capture_output=True,text=True)
            body,code=r.stdout.rsplit("\n",1)
            if code=="200": t=body; open(fn,"w").write(t); break
            if code=="404": return None
            time.sleep(10*(attempt+1))
        else: return None
        time.sleep(2)
    m=re.match(r'#REDIRECT\s*\[\[([^\]#]+)',t,re.I)
    if m and depth<3: return fetch(m.group(1),depth+1)
    return t
if __name__=="__main__":
    for t in sys.argv[1:]:
        r=fetch(t); print(t, None if r is None else len(r))
