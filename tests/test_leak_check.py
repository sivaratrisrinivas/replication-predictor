import sys; sys.path.insert(0,'src')
from leak_check import check
CLEAN={'hypothesis':'Predicted that priming increases helping.','design':'between, 2 conditions','sample_size_total':120,'analysis_plan':'independent samples t-test'}
def test_clean_passes(): assert check(CLEAN)[0]
def test_p_value_caught(): assert not check({**CLEAN,'other':'p < .05'})[0]
def test_tstat_caught(): assert not check({**CLEAN,'other':'t(118) = 2.31'})[0]
def test_effect_caught(): assert not check({**CLEAN,'other':'d = 0.45'})[0]
def test_word_caught(): assert not check({**CLEAN,'other':'The effect was significant'})[0]
def test_replication_word_caught(): assert not check({**CLEAN,'other':'This failed to replicate'})[0]
def test_sample_size_field_allowed(): assert check({**CLEAN,'sample_size_total':2986})[0]
def test_borderline_n_in_text_ok(): assert check({**CLEAN,'recruitment_and_incentive':'N = 120 undergraduates for course credit'})[0]

def test_chisquare_name_ok(): assert check({**CLEAN,'analysis_plan':'chi-square test of independence'})[0]
def test_chisquare_value_caught(): assert not check({**CLEAN,'other':'chi-square(2) = 5.1'})[0]
