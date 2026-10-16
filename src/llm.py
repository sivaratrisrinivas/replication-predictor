import os, json, hashlib, time, requests
CACHE='cache'
def _key(model,prompt): return hashlib.sha256((model+'\n'+prompt).encode()).hexdigest()
def _cached(model,prompt):
    p=f'{CACHE}/{_key(model,prompt)}.json'
    return json.load(open(p)) if os.path.exists(p) else None
def _save(model,prompt,out): json.dump({'model':model,'out':out},open(f'{CACHE}/{_key(model,prompt)}.json','w'))
def call(model,prompt,system=None,temperature=0.0,max_tokens=2000,json_mode=True):
    c=_cached(model,(system or '')+'||'+prompt)
    if c: return c['out']
    for attempt in range(8):
        try:
            if model.startswith('gemini'):
                k=open('/workspace/.secrets/gemini_key').read().strip()
                body={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'temperature':temperature,'maxOutputTokens':max_tokens}}
                if json_mode: body['generationConfig']['responseMimeType']='application/json'
                if system: body['systemInstruction']={'parts':[{'text':system}]}
                r=requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':k},json=body,timeout=120)
                if r.status_code==200:
                    out=r.json()['candidates'][0]['content']['parts'][0]['text']; break
            else:
                msgs=([{'role':'system','content':system}] if system else [])+[{'role':'user','content':prompt}]
                body={'model':model,'messages':msgs,'temperature':temperature,'max_tokens':max_tokens}
                if json_mode: body['response_format']={'type':'json_object'}
                if 'gpt-oss' in model: body['reasoning_effort']='low'
                r=requests.post('https://api.groq.com/openai/v1/chat/completions',headers={'Authorization':'Bearer '+os.environ['GROQ_API_KEY']},json=body,timeout=120)
                if r.status_code==200:
                    out=r.json()['choices'][0]['message']['content']; break
            if r.status_code==429 and 'PerDay' in r.text: raise RuntimeError('DAILY_QUOTA '+model)
            wait=min(60,5*(attempt+1))
            if r.status_code==429:
                import re; m=re.search(r'try again in ([\d.]+)s',r.text); wait=float(m.group(1))+1 if m else wait
            time.sleep(wait)
        except RuntimeError: raise
        except Exception as e:
            time.sleep(5)
    else:
        raise RuntimeError(f'LLM failed {model} {r.status_code} {r.text[:200]}')
    _save(model,(system or '')+'||'+prompt,out); return out
