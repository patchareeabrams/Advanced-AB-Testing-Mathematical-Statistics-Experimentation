# Advanced A/B Experiment Analysis

**Dataset:** 20,000 synthetic randomized users (10,000 per arm). Not real business data.

## Observed evidence

- Control conversion: 9.860%; treatment conversion: 10.910%.
- Absolute lift: 1.050% (percentage points: 1.05).
- Pooled two-sided z-test p-value: 0.0149.
- Permutation two-sided p-value (5,000 randomizations): 0.0152.
- Bootstrap 95% percentile interval: [0.210%, 1.910%].
- Bayesian posterior P(treatment > control), Beta(1,1) priors: 99.256%.
- Bayesian 95% credible interval for lift: [0.207%, 1.893%].

## Design and simulation

- Approximate sample size to detect 10% → 11% at two-sided alpha=0.05 and 80% power: **14,751 users per arm**.
- Monte Carlo null rejection frequency (3,000 runs): 5.000%.
- Monte Carlo detection frequency under 10% vs 11% (3,000 runs, 10,000 per arm): 62.267%.

## Interpretation and limitations

The z-test and randomization test answer frequentist questions about data under a null model. The Bayesian posterior probability conditions on data and a specified prior; it is **not** a frequentist p-value. The percentile bootstrap interval is an approximate uncertainty interval. Simulation frequencies have Monte Carlo error. The sample-size formula is a planning approximation, not a guarantee. All tests assume clean user-level randomization, independent observations, and no peeking; the dataset is synthetic. Do not claim a business impact without costs, guardrails, and real experiment data.
