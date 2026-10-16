# Novelty and usefulness check: methods-only, LLM-based replication forecasting

Date: 2026-10-16. Searched: web, arXiv API, GitHub (gh search), Semantic Scholar (rate limited, so only partly usable), X API. Every claim below was read on the cited page or in search-result text. Where I could not open a source in full, it says so.

## Verdict (short)

Not fully done end to end, but the idea is mostly prior art. Nothing I found combines all of these in one public, reproducible tool: (1) input is a methods-only card made blind to results, p-values and effect sizes, (2) an LLM does the forecasting, (3) scoring is on held-out replication outcomes by paper, with calibration and simple baselines, (4) a memorization probe. That combination is a narrow, defensible gap. It is an incremental benchmark and ablation, not a new field. Proceeding to a small Phase 2 build was justified, with strong small-sample caveats. I cannot prove absence, only that I did not find it.

## What is NOT novel (already done)

| Claim | Prior work | Evidence |
|---|---|---|
| Humans can forecast replication from papers | Dreber et al. 2015 prediction markets on RPP (44 studies); markets and surveys also run on EERP, SSRP, MTRP and Many Labs 2 (named in the Dreber and Johannesson 2025 review chapter; I did not open the original Camerer papers) | Berkeley PDF of PNAS 2015 paper; https://doi.org/10.4324/9781003569954-7 (correlations about 0.5, markets somewhat better than surveys) |
| Human elicitation at scale | DARPA SCORE with repliCATS and Replication Markets: 76% and 78% best-metric accuracy | https://sciencesources.eurekalert.org/news-releases/1121267 ; Replication Markets: https://arxiv.org/abs/2005.04543 (73% on 104 studies per search summary) |
| Automated ML forecasting of replication | SCORE machine teams (Synthetic Markets, MACROSCORE, A+) were "not consistently effective" | same EurekAlert page |
| ML on paper text | Yang, Youyou, Uzzi 2020 PNAS (413 replications, out-of-sample accuracy 0.65 to 0.78, comparable to markets); Youyou, Yang, Uzzi 2023 PNAS applies a word2vec plus random forest/logistic text model to 14,126 psychology papers | https://www.pnas.org/doi/10.1073/pnas.1909046117 ; https://www.pnas.org/doi/10.1073/pnas.2208863120 |
| Text vs metadata comparison | Herzenstein et al. 2024, Psychological Science: metadata alone AUC .696, +study text .725, full text .716 (299 studies) | https://doi.org/10.1177/09567976241254037 (numbers from search-result text of the Columbia-hosted PDF; I could not open the PDF myself, fetch timed out) |
| Statistical-feature models | Numeric-feature models (p-values, sample size) are referenced in Wu et al. 2023 (refs 27, 28); Altmetric measures attention, scite measures citation stance, statcheck checks reporting consistency. None of the three forecasts replication directly | PNAS 2023 text; Altmetric/scite/statcheck descriptions in search results (https://pmc.ncbi.nlm.nih.gov/articles/PMC7540394/ for statcheck) |
| LLM forecasting of replication, simulated-participant route | Saynova et al. 2025, arXiv:2503.10671: 14 Many Labs 2 studies, F1 up to 77% (Mistral 7B), 67% (GPT-4o). Uses original-effect information and tiny N | https://arxiv.org/abs/2503.10671 |
| LLM forecasting of experiment results | Nature 2026 (70 preregistered US survey experiments, GPT-4 predicts effects, matches pooled human forecasts, overestimates effect sizes); Royal Society Open Science 2024 (GPT-4 vs 119 experts) | https://www.nature.com/articles/s41586-026-10742-x ; https://royalsocietypublishing.org/rsos/article/11/9/240682/92988 |
| Public automated-forecast competition with held-out replication outcomes, Brier scoring, LLMs allowed | COS Predicting Replicability Challenge 2025 to 2026, three rounds. R1: no team beat constant 0.5 (Brier .25). R2: all teams beat it (median AUC .66). R3 (41 health-behavior claims): 8 of 15 beat it | https://www.cos.io/blog/predicting-replicability-challenge-round-1-results-round-2-opportunity ; .../round-3-results ; https://osf.io/preprints/metaarxiv/kbva9_v1 |
| LLM agents running replications/reproductions | ReplicatorBench (19 SCORE claims, KDD 2026, code at github.com/CenterForOpenScience/llm-benchmarking); Kohler et al. 2026 (48 papers, methods-only reproduction with original data); Holtdirk et al. 2026 arXiv:2606.13670 (180 SCORE studies, reproducibility not replication) | https://arxiv.org/abs/2602.11354 ; https://arxiv.org/abs/2604.21965 ; https://arxiv.org/abs/2606.13670 |
| Related methods-only LLM test, not replication | "Experiments or Outcomes?" ACL 2026 short: feasibility judgments from hypothesis, experiments, outcomes; experiments without outcomes often hurt vs hypothesis only | https://doi.org/10.18653/v1/2026.acl-short.50 |
| Public database of replication outcomes | FORRT FReD (CC-BY 4.0, FReD.xlsx on OSF), SCORE outcomes in Nature 2026 (Tyner et al.: 274 claims, 164 papers, 55.1% replicated) | https://osf.io/9r62x ; https://doi.org/10.1038/s41586-025-10078-y |

Also noted: COS Challenge inputs included the claim text, effect value, and p-value for each claim (Round 1 blog table). Those entrants were not blinded to results by design. Yang 2020 and Wu 2023 use paper narrative text, which for a published paper includes result language.

## What I found no evidence of (the gap)

1. A methods-only, result-blind input. COS challenge gave p-values and effect sizes. Text models used whole-paper narratives. The Saynova route conditions on original effects. "Experiments or Outcomes?" tests blinding but on a different target (scientific feasibility, not replication outcome).
2. A public tool plus code eval that checks the blinding (regex leak check on the methods card), instead of trusting a prompt.
3. A built-in memorization probe: citation-only arm, to see how much of the score is fame or recall rather than design reading.

Searches that returned nothing relevant: arXiv title/abstract queries for replicability prediction with LLMs (only the papers above), GitHub repo searches "predict replication llm", "replicability prediction language model" (no results), X post search (no relevant posts, only noise). Semantic Scholar API returned HTTP 429 so it was not used.

## Usefulness, honestly

- Likely useful as: a cheap triage hint for which claims deserve a replication, and as a clean ablation showing how much signal sits in design alone.
- Ceiling from prior work: best humans and ML land near AUC 0.7 to 0.8 on mixed samples; COS Challenge medians were near .66 AUC in Round 2. A methods-only model should not be expected to beat that.
- Real limit for any build here: open full text of original papers. Only a minority of the replicated papers have open full text, so any public, legal evaluation set is small. That limits what can be claimed.

## Decision

Proceed to a small, clearly caveated Phase 2. Do not claim state of the art. See the repo README for the numbers.
