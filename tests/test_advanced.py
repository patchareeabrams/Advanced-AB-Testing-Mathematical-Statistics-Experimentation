import pandas as pd
import pytest
from src.advanced import permutation_test, bootstrap_interval, bayesian_analysis, approximate_sample_size, monte_carlo

@pytest.fixture
def sample():
    return pd.DataFrame({"user_id":range(1,21),"variant":["A"]*10+["B"]*10,"converted":[0]*9+[1]+[0]*7+[1]*3})

def test_permutation_deterministic(sample):
    assert permutation_test(sample, 100, 12)==permutation_test(sample,100,12)
    assert 0 <= permutation_test(sample,100,12)['permutation_p_value'] <= 1

def test_bootstrap(sample):
    r=bootstrap_interval(sample,1000)
    assert r['bootstrap_ci_low'] <= r['bootstrap_ci_high']

def test_bayesian(sample):
    r=bayesian_analysis(sample,1000)
    assert 0 <= r['posterior_probability_b_better'] <= 1

def test_power_sample_size():
    assert approximate_sample_size(.10,.11) > 10000
    with pytest.raises(ValueError): approximate_sample_size(.10,.10)

def test_null_simulation():
    r=monte_carlo(.1,.1,1000,1000)
    assert 0 <= r['rejection_rate'] <= 1
