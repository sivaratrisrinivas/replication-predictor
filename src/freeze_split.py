"""Freeze the held-out split BEFORE any LLM output is generated or looked at.
Rule: sha256(original DOI) mod 100 < 30 -> test. Split is by paper, so no paper straddles train/test."""
import pandas as pd, hashlib, os, json
d=pd.read_excel('data/FReD.xlsx'); d['doi']=d.doi_o.str.strip().str.lower()
d=d[d.reported_success.isin(['successful','failed'])].copy()
fn=lambda x: hashlib.sha1(x.encode()).hexdigest()[:12]
d['pid']=d.doi.map(fn)
d=d[d.pid.map(lambda p: os.path.exists(f'data/txt/{p}.txt'))].copy()
d['y']=(d.reported_success=='successful').astype(int)
d['project']=d.fred_id.str.extract(r'^([A-Za-z]+)')[0]
d['split']=d.doi.map(lambda x:'test' if int(hashlib.sha256(x.encode()).hexdigest(),16)%100<30 else 'train')
d['eid']=d.entry_id.astype(str)+'_'+d.effect_id.astype(str)
keep=['eid','doi','pid','title_o','author_o','journal_o','year_o','discipline','project','claim_text_o','n_o','y','split']
d[keep].to_csv('data/entries_text.csv',index=False)
print(len(d),d.doi.nunique(),d.groupby('split').y.agg(['size','mean']))
