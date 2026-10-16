"""Stage 2: forecast replication from the blinded card. Arms:
  card     = methods-only card (main)
  citation = title/authors/journal/year only (memorization / fame probe)
Model: Groq openai/gpt-oss-120b (free tier). 3 samples at T=0.7 averaged for arm 'card'; 1 sample for 'citation'."""
import sys, json, re, pandas as pd, numpy as np
sys.path.insert(0,'src'); import llm
MODEL='openai/gpt-oss-120b'
DEF="""A replication 'succeeds' if an independent team runs a new, well-powered, close replication and finds the focal effect in the same direction as the original and the replicators judge it successful. 'Fails' otherwise. In large published replication projects roughly 40 to 60 percent of attempts succeed."""
SYS_CARD=f"""You are a careful forecaster of scientific replication. You see only a description of a study's design and the pre-data hypothesis. You do not see any results.
{DEF}
Think about: statistical power for the sample size and design, whether the manipulation is subtle or strong, whether the outcome is a noisy self-report, how many analyses or conditions give flexibility, how surprising or counterintuitive the claim is, whether the design is between- or within-subjects, and the field's typical replicability.
Give a calibrated probability in [0.02, 0.98]. Avoid sticking to 0.5 when the design clearly points one way, but do not be overconfident.
Return JSON: {{"p_replicate": number, "key_reason": "one sentence"}}"""
SYS_CIT=f"""You forecast scientific replication from a bibliographic citation only. You see no methods and no results.
{DEF}
If you recognise the paper, use what you know about whether its finding has held up; otherwise use the field and year as weak priors.
Return JSON: {{"p_replicate": number, "recognised": true or false, "key_reason": "one sentence"}}"""
def card_text(c): return '\n'.join(f'{k}: {v}' for k,v in c.items() if not k.startswith('_'))
def parse(o):
    try: return float(np.clip(json.loads(o)['p_replicate'],0.02,0.98))
    except Exception:
        m=re.search(r'"p_replicate"\s*:\s*([\d.]+)',o); return float(np.clip(float(m.group(1)),0.02,0.98)) if m else np.nan
def run(df,cards,arms=('card','citation')):
    rows=[]
    for r in df.itertuples():
        row={'eid':r.eid}
        c=cards.get(r.eid,{})
        if 'card' in arms and 'error' not in c and c:
            ps=[parse(llm.call(MODEL,f'STUDY DESCRIPTION (sample {i}):\n{card_text(c)}',system=SYS_CARD,temperature=0.7,max_tokens=800)) for i in range(3)]
            row['p_card']=float(np.nanmean(ps))
        if 'citation' in arms:
            cit=f'Title: {r.title_o}\nJournal: {r.journal_o}\nYear: {r.year_o}'
            o=llm.call(MODEL,cit,system=SYS_CIT,temperature=0.0,max_tokens=800)
            row['p_citation']=parse(o)
            try: row['recognised']=bool(json.loads(o).get('recognised'))
            except Exception: row['recognised']=False
        rows.append(row)
    return pd.DataFrame(rows)
if __name__=='__main__':
    split=sys.argv[1]; d=pd.read_csv('data/entries_text.csv'); d=d[d.split==split]
    cards=json.load(open(f'data/cards_{split}.json'))
    run(d,cards).to_csv(f'data/preds_{split}.csv',index=False)
