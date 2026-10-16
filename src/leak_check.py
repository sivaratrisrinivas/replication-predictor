"""Code eval: does a blinded card contain result information? Returns (pass, reasons). Unit-tested in tests/."""
import re
PATTERNS={
 'p_value':r'\b[pP]\s*[<=>≤≥]\s*[.\d]',
 'test_stat':r'\b(?:t|F|z|r|U|W|Z)\s*\(\s*\d+(?:\.\d+)?(?:\s*,\s*\d+)?\s*\)\s*=',
 'chi2':r'(?:χ|chi)\s*-?\s*(?:2|²|square[d]?)\s*\(',
 'effect_eq':r'\b(?:d|g|r|R2|R²|η2|η²|β|b|B|OR|HR|RR|M|SD|SE)\s*=\s*[-−]?\.?\d',
 'ci':r'\b9[05]\s*%\s*(?:CI|confidence)',
 'result_words':r'\b(?:significant(?:ly)?|non-?significant|marginally|statistically|confirmed|supported (?:the|our)|consistent with (?:the|our) hypothes|found that|results? (?:showed|revealed|indicated|suggest)|effect size|was higher|was lower|increased significantly|failed to)\b',
 'replication_leak':r'\b(?:replicat\w+|failed to replicate|many labs|reproducibility project)\b',
}
def check(card):
    text=' '.join(str(v) for k,v in card.items() if k!='sample_size_total')
    hits={k:re.findall(p,text,flags=re.I if k in('result_words','replication_leak','ci','chi2') else 0) for k,p in PATTERNS.items()}
    hits={k:v for k,v in hits.items() if v}
    return (not hits), hits
