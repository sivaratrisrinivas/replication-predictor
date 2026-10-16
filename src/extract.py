"""Stage 1: turn a full paper into a BLINDED methods card for one focal effect.
The extractor sees the full paper (it must, to find the methods) but is told to output design only.
A code eval (leak_check.py) then verifies the card has no statistics or result language."""
import sys, json, pandas as pd, re
sys.path.insert(0,'src'); import llm
MODELS=['gemini-3.1-flash-lite','gemini-flash-lite-latest','gemini-3-flash-preview','gemma-4-31b-it']
SYS="""You prepare blinded study descriptions for a replication forecasting experiment.
You are given a paper and one focal effect. Produce a JSON card describing ONLY what the researchers did and what they predicted BEFORE seeing data.
HARD RULES:
- Never include any result, statistic, p-value, effect size, confidence interval, mean, correlation, regression coefficient, 'significant', 'non-significant', 'supported', 'confirmed', 'consistent with', or any statement about what was found.
- Never include the discussion, conclusions, or limitations that depend on results.
- Sample size of the focal study (participants after exclusions as reported in the methods) IS allowed as a plain number. Planned exclusion rules are allowed.
- State the hypothesis as the pre-data prediction, in neutral form (e.g. 'Predicted that X would increase Y').
- If the paper is multi-study, describe only the study that contains the focal effect.
JSON fields: hypothesis (string), design (between/within/mixed/correlational/observational/other, plus conditions), manipulation_or_predictor (string), outcome_measure (string), population_and_setting (string), sample_size_total (integer or null), recruitment_and_incentive (string), analysis_plan (string: the test the authors said they would run), preregistered_or_confirmatory (string: say what the methods state, or 'not stated'), other_methods_notes (string, max 60 words)."""
def one(r):
    txt=open(f'data/txt/{r.pid}.txt',errors='ignore').read()[:150000]
    prompt=f"PAPER TEXT:\n{txt}\n\nFOCAL EFFECT (identifies which study/effect to describe; do NOT copy numbers or findings from it):\n{r.claim_text_o}\n\nReturn the JSON card."
    err=None
    for m in MODELS:
        try:
            card=json.loads(llm.call(m,prompt,system=SYS,max_tokens=1500)); card['_extractor']=m; return r.eid,card
        except Exception as ex: err={'error':str(ex)[:200]}
    return r.eid,err
def run(df,workers=5):
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(workers) as ex: return dict(ex.map(one,list(df.itertuples())))
if __name__=='__main__':
    split=sys.argv[1]; d=pd.read_csv('data/entries_text.csv'); d=d[d.split==split]
    res=run(d); json.dump(res,open(f'data/cards_{split}.json','w'),indent=1); print(split,len(res),sum('error' in v for v in res.values()))
