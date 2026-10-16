"""Build the labelled entry table from FReD (CC-BY 4.0) + Unpaywall OA locations.
Label: reported_success in {successful, failed}. Mixed/other dropped (stated in README)."""
import pandas as pd, json, hashlib, re
d=pd.read_excel('data/FReD.xlsx'); u=json.load(open('data/unpaywall.json'))
d['doi']=d.doi_o.str.strip().str.lower()
d=d[d.reported_success.isin(['successful','failed'])].copy()
d['y']=(d.reported_success=='successful').astype(int)
def locs(doi):
    v=u.get(doi)
    if not isinstance(v,dict) or not v.get('is_oa'): return []
    out=[]
    for l in v.get('oa_locations') or []:
        if l.get('url_for_pdf'): out.append(l['url_for_pdf'])
    return out
d['pdfs']=d.doi.map(locs)
d=d[d.pdfs.map(len)>0]
d['project']=d.fred_id.str.extract(r'^([A-Za-z]+)')[0]
def h(x): return int(hashlib.sha256(x.encode()).hexdigest(),16)%100
d['hash']=d.doi.map(h)
d['split']=(d.hash<30).map({True:'test',False:'train'})
d['pdfs']=d.pdfs.map(json.dumps)
d.drop(columns=['bibtex_o','bibtex_r']).to_csv('data/entries.csv',index=False)
print(len(d),d.doi.nunique(),d.split.value_counts().to_dict())
