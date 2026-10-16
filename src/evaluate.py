"""Evaluate forecasts vs published replication outcomes. Paper-clustered bootstrap CIs.
Baselines (all fit on TRAIN only): base rate; log-n logistic; log-n + year logistic."""
import sys, json, numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
rng=np.random.default_rng(0)
def feats(d): 
    return pd.DataFrame({'logn':np.log10(pd.to_numeric(d.n_o,errors='coerce').clip(lower=5)).fillna(np.log10(100)),'year':(d.year_o-2010)/10})
def logit(p): p=np.clip(p,.02,.98); return np.log(p/(1-p))
def metrics(y,p):
    return {'auc':roc_auc_score(y,p) if len(set(y))>1 else np.nan,'brier':brier_score_loss(y,p)}
def boot(d,cols,B=2000):
    papers=d.doi.unique(); g={k:v for k,v in d.groupby('doi')}
    res={c:{'auc':[],'brier':[]} for c in cols}; diffs={}
    for _ in range(B):
        s=pd.concat([g[p] for p in rng.choice(papers,len(papers))])
        if s.y.nunique()<2: continue
        for c in cols:
            m=metrics(s.y.values,s[c].values); res[c]['auc'].append(m['auc']); res[c]['brier'].append(m['brier'])
    return res
def ci(a): a=np.array(a); return np.nanpercentile(a,[2.5,97.5])
def main(preds_tr,preds_te,out):
    tr=pd.read_csv('data/entries_text.csv'); 
    tr_d=tr[tr.split=='train'].merge(pd.read_csv(preds_tr),on='eid'); te=tr[tr.split=='test'].merge(pd.read_csv(preds_te),on='eid')
    Xtr,Xte=feats(tr_d),feats(te)
    br=tr_d.y.mean(); te['p_base']=br
    m1=LogisticRegression(C=1.0).fit(Xtr[['logn']],tr_d.y); te['p_logn']=m1.predict_proba(Xte[['logn']])[:,1]
    m2=LogisticRegression(C=1.0).fit(Xtr[['logn','year']],tr_d.y); te['p_logn_year']=m2.predict_proba(Xte[['logn','year']])[:,1]
    # LLM raw and LLM recalibrated (Platt on train, applied to test)
    ok=tr_d.p_card.notna(); cal=LogisticRegression(C=1.0).fit(logit(tr_d.p_card[ok]).values.reshape(-1,1),tr_d.y[ok])
    te['p_card_cal']=cal.predict_proba(logit(te.p_card.fillna(br)).values.reshape(-1,1))[:,1]
    # LLM + n stack, fit on train
    Ztr=np.c_[logit(tr_d.p_card.fillna(br)),Xtr.logn]; Zte=np.c_[logit(te.p_card.fillna(br)),Xte.logn]
    st=LogisticRegression(C=1.0).fit(Ztr,tr_d.y); te['p_card_n']=st.predict_proba(Zte)[:,1]
    te['p_const50']=0.5
    cols=['p_const50','p_base','p_logn','p_logn_year','p_card','p_card_cal','p_card_n','p_citation']
    B=boot(te,cols); rows=[]
    for c in cols:
        m=metrics(te.y.values,te[c].values); a=ci(B[c]['auc']); b=ci(B[c]['brier'])
        rows.append({'model':c,'auc':m['auc'],'auc_lo':a[0],'auc_hi':a[1],'brier':m['brier'],'brier_lo':b[0],'brier_hi':b[1]})
    R=pd.DataFrame(rows); R.to_csv(out+'_results.csv',index=False); print(R.round(3).to_string())
    print('test n',len(te),'papers',te.doi.nunique(),'base rate test',te.y.mean().round(3),'train',round(br,3))
    # paired bootstrap: AUC(card) - AUC(logn)
    papers=te.doi.unique(); g={k:v for k,v in te.groupby('doi')}; dd=[];db=[]
    for _ in range(2000):
        s=pd.concat([g[p] for p in rng.choice(papers,len(papers))])
        if s.y.nunique()<2: continue
        dd.append(roc_auc_score(s.y,s.p_card)-roc_auc_score(s.y,s.p_logn)); db.append(brier_score_loss(s.y,s.p_card_cal)-brier_score_loss(s.y,s.p_base))
    print('AUC card - logn: %.3f [%.3f, %.3f]'%(np.mean(dd),*ci(dd)))
    print('Brier card_cal - base: %.3f [%.3f, %.3f]'%(np.mean(db),*ci(db)))
    # calibration by tertile of p_card
    te['bin']=pd.qcut(te.p_card.rank(method='first'),3,labels=['low','mid','high']); print(te.groupby('bin',observed=True).agg(n=('y','size'),mean_pred=('p_card','mean'),obs=('y','mean')).round(3))
    # memorization probe: recognised vs not
    print(te.groupby('recognised').agg(n=('y','size'),obs=('y','mean'),auc_card=('p_card',lambda s:np.nan)).round(3))
    te.to_csv(out+'_test_preds.csv',index=False)
if __name__=='__main__': main(*sys.argv[1:4])
