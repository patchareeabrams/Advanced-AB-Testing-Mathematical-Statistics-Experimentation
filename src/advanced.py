"""Reproducible advanced A/B inference; synthetic educational data."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import norm, beta
from scipy.optimize import brentq
from src.analyze import analyze, ROOT


def permutation_test(df, repetitions=5000, seed=42):
    """Two-sided randomization test conditional on observed outcomes and group sizes."""
    if repetitions < 1: raise ValueError("repetitions must be positive")
    analyze(df)  # validate
    y = df.converted.to_numpy(dtype=float)
    n_a = int((df.variant == "A").sum())
    observed = y[df.variant.to_numpy() == "B"].mean() - y[df.variant.to_numpy() == "A"].mean()
    rng = np.random.default_rng(seed)
    extreme = 0
    for _ in range(repetitions):
        shuffled = rng.permutation(y)
        delta = shuffled[n_a:].mean() - shuffled[:n_a].mean()
        extreme += abs(delta) >= abs(observed) - 1e-14
    return {"observed_difference": float(observed), "permutation_p_value": float((extreme+1)/(repetitions+1)), "repetitions": repetitions}


def bootstrap_interval(df, repetitions=5000, seed=42, alpha=.05):
    """Within-arm percentile bootstrap for absolute conversion lift."""
    analyze(df)
    if repetitions < 1 or not 0 < alpha < 1: raise ValueError("Invalid arguments")
    rng = np.random.default_rng(seed)
    a = df.loc[df.variant == "A", "converted"].to_numpy()
    b = df.loc[df.variant == "B", "converted"].to_numpy()
    # Binomial draws exactly reproduce nonparametric resampling of binary outcomes.
    differences = rng.binomial(len(b), b.mean(), size=repetitions)/len(b) - rng.binomial(len(a), a.mean(), size=repetitions)/len(a)
    lo, hi = np.quantile(differences, [alpha/2, 1-alpha/2])
    return {"bootstrap_ci_low": float(lo), "bootstrap_ci_high": float(hi), "repetitions": repetitions}


def bayesian_analysis(df, draws=50000, seed=42, prior_a=1, prior_b=1):
    """Independent Beta priors; report posterior P(p_B > p_A), not a p-value."""
    summary, _ = analyze(df)
    if min(draws, prior_a, prior_b) <= 0: raise ValueError("Positive draws and prior parameters required")
    rng = np.random.default_rng(seed)
    posterior = {}
    for arm in ["A", "B"]:
        successes = int(summary.loc[arm, "sum"])
        failures = int(summary.loc[arm, "count"] - successes)
        posterior[arm] = rng.beta(prior_a + successes, prior_b + failures, draws)
    delta = posterior["B"] - posterior["A"]
    return {"posterior_probability_b_better": float((delta > 0).mean()), "posterior_mean_lift": float(delta.mean()), "posterior_95pct_interval": [float(v) for v in np.quantile(delta,[.025,.975])], "prior": f"Beta({prior_a},{prior_b})", "draws": draws}


def approximate_sample_size(p_a=.10, p_b=.11, alpha=.05, power=.8):
    """Normal-approximation sample size per arm, equal allocation, two-sided."""
    if not (0 < p_a < 1 and 0 < p_b < 1 and p_a != p_b and 0 < alpha < 1 and 0 < power < 1): raise ValueError("Invalid probabilities")
    pooled=(p_a+p_b)/2
    z_alpha=norm.ppf(1-alpha/2)
    z_power=norm.ppf(power)
    n=((z_alpha*np.sqrt(2*pooled*(1-pooled)) + z_power*np.sqrt(p_a*(1-p_a)+p_b*(1-p_b)))**2)/(p_b-p_a)**2
    return int(np.ceil(n))


def monte_carlo(p_a=.10, p_b=.11, n_per_arm=10000, trials=3000, seed=42, alpha=.05):
    """Empirical rejection frequency for fixed-horizon two-sided pooled z-test."""
    if not (0 <= p_a <= 1 and 0 <= p_b <= 1 and n_per_arm > 0 and trials > 0 and 0 < alpha < 1): raise ValueError("Invalid arguments")
    rng=np.random.default_rng(seed)
    x_a=rng.binomial(n_per_arm,p_a,size=trials)
    x_b=rng.binomial(n_per_arm,p_b,size=trials)
    pooled=(x_a+x_b)/(2*n_per_arm)
    se=np.sqrt(pooled*(1-pooled)*2/n_per_arm)
    z=np.divide((x_b-x_a)/n_per_arm,se,out=np.zeros(trials),where=se>0)
    rejected=2*norm.sf(abs(z))<alpha
    return {"rejection_rate":float(rejected.mean()),"trials":trials,"n_per_arm":n_per_arm,"p_a":p_a,"p_b":p_b}


def main():
    df=pd.read_csv(ROOT/'data'/'experiment.csv')
    summary, baseline=analyze(df)
    results={"frequentist":baseline,"permutation":permutation_test(df),"bootstrap":bootstrap_interval(df),"bayesian":bayesian_analysis(df),"design":{"required_n_per_arm_for_10_to_11_percent":approximate_sample_size()},"simulation":{"null_false_positive_rate":monte_carlo(p_b=.10),"alternative_detection_rate":monte_carlo()}}
    out=ROOT/'results';out.mkdir(exist_ok=True)
    (out/'advanced_results.json').write_text(json.dumps(results,indent=2,allow_nan=False,default=lambda x: x.item() if hasattr(x,"item") else str(x)))
    p=results['permutation']; b=results['bootstrap']; bay=results['bayesian']; design=results['design']; sim=results['simulation']
    report=f"""# Advanced A/B Experiment Analysis

**Dataset:** 20,000 synthetic randomized users (10,000 per arm). Not real business data.

## Observed evidence

- Control conversion: {summary.loc['A','mean']:.3%}; treatment conversion: {summary.loc['B','mean']:.3%}.
- Absolute lift: {baseline['lift_absolute']:.3%} (percentage points: {100*baseline['lift_absolute']:.2f}).
- Pooled two-sided z-test p-value: {baseline['p_value']:.4f}.
- Permutation two-sided p-value ({p['repetitions']:,} randomizations): {p['permutation_p_value']:.4f}.
- Bootstrap 95% percentile interval: [{b['bootstrap_ci_low']:.3%}, {b['bootstrap_ci_high']:.3%}].
- Bayesian posterior P(treatment > control), Beta(1,1) priors: {bay['posterior_probability_b_better']:.3%}.
- Bayesian 95% credible interval for lift: [{bay['posterior_95pct_interval'][0]:.3%}, {bay['posterior_95pct_interval'][1]:.3%}].

## Design and simulation

- Approximate sample size to detect 10% → 11% at two-sided alpha=0.05 and 80% power: **{design['required_n_per_arm_for_10_to_11_percent']:,} users per arm**.
- Monte Carlo null rejection frequency (3,000 runs): {sim['null_false_positive_rate']['rejection_rate']:.3%}.
- Monte Carlo detection frequency under 10% vs 11% (3,000 runs, 10,000 per arm): {sim['alternative_detection_rate']['rejection_rate']:.3%}.

## Interpretation and limitations

The z-test and randomization test answer frequentist questions about data under a null model. The Bayesian posterior probability conditions on data and a specified prior; it is **not** a frequentist p-value. The percentile bootstrap interval is an approximate uncertainty interval. Simulation frequencies have Monte Carlo error. The sample-size formula is a planning approximation, not a guarantee. All tests assume clean user-level randomization, independent observations, and no peeking; the dataset is synthetic. Do not claim a business impact without costs, guardrails, and real experiment data.
"""
    (out/'research_report.md').write_text(report)
    print(report)

if __name__=='__main__': main()
