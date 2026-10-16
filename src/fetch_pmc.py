import pandas as pd, requests, os, hashlib, re, json, concurrent.futures as cf
from xml.etree import ElementTree as ET
d=pd.read_excel('data/FReD.xlsx'); d['doi']=d.doi_o.str.strip().str.lower()
dois=sorted(set(d.doi))
def fn(doi): return hashlib.sha1(doi.encode()).hexdigest()[:12]
def go(doi):
    t=f'data/txt/{fn(doi)}.txt'
    if os.path.exists(t): return doi,'cached'
    try:
        r=requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',params={'query':f'DOI:"{doi}"','format':'json','resultType':'lite'},timeout=30).json()
        for x in r.get('resultList',{}).get('result',[]):
            if x.get('pmcid') and x.get('isOpenAccess')=='Y':
                xml=requests.get(f"https://www.ebi.ac.uk/europepmc/webservices/rest/{x['pmcid']}/fullTextXML",timeout=60)
                if xml.status_code!=200: continue
                root=ET.fromstring(xml.content)
                body=root.find('.//body')
                if body is None: continue
                parts=[]
                for sec in body.iter('sec'):
                    ti=sec.find('title'); 
                    if ti is not None: parts.append('\n## '+''.join(ti.itertext()))
                    for p in sec.findall('p'): parts.append(''.join(p.itertext()))
                txt='\n'.join(parts)
                if len(txt)>5000:
                    open(t,'w').write(txt); return doi,'pmc'
    except Exception as e: return doi,'err'
    return doi,'none'
with cf.ThreadPoolExecutor(6) as ex: res=list(ex.map(go,dois))
import collections; print(collections.Counter(s for _,s in res))
