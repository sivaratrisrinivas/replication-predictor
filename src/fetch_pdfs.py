import pandas as pd, json, requests, os, subprocess, hashlib, concurrent.futures as cf
d=pd.read_csv('data/entries.csv')
papers=d.drop_duplicates('doi')[['doi','pdfs']]
def fn(doi): return hashlib.sha1(doi.encode()).hexdigest()[:12]
def go(row):
    doi,pdfs=row; p=f'data/pdf/{fn(doi)}.pdf'; t=f'data/txt/{fn(doi)}.txt'
    if os.path.exists(t): return doi,'cached'
    for url in json.loads(pdfs):
        try:
            r=requests.get(url,timeout=30,headers={'User-Agent':'Mozilla/5.0 (research; replication-predictor)'})
            if r.status_code==200 and r.content[:4]==b'%PDF':
                open(p,'wb').write(r.content)
                subprocess.run(['pdftotext','-layout',p,t],timeout=60)
                if os.path.exists(t) and os.path.getsize(t)>5000: return doi,'ok'
        except Exception as e: pass
    return doi,'fail'
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(go,zip(papers.doi,papers.pdfs)))
import collections; print(collections.Counter(s for _,s in res))
json.dump(dict(res),open('data/fetch_status.json','w'))
