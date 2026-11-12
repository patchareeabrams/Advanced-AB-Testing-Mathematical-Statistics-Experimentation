# Mathematical methods and derivations

## 1. Estimand and identification
Random assignment defines potential outcomes Y_i(0), Y_i(1). The average treatment effect is E[Y(1)-Y(0)]. The difference in observed sample proportions is unbiased under proper random assignment and no interference, with independent Bernoulli outcomes as a working model.

## 2. Two-sample z-test
For arm g, X_g ~ Binomial(n_g,p_g), and p_hat_g=X_g/n_g. Under H0: p_A=p_B=p, the pooled MLE is p_hat=(X_A+X_B)/(n_A+n_B). The null standard error is sqrt(p_hat(1-p_hat)(1/n_A+1/n_B)), and Z=(p_hat_B-p_hat_A)/SE_0 is asymptotically standard normal. A two-sided p-value is 2 Phi(-|Z|). The unpooled Wald interval uses SE=sqrt(p_hat_A(1-p_hat_A)/n_A+p_hat_B(1-p_hat_B)/n_B). Wald coverage may be poor for rare outcomes or small n.

## 3. Permutation/randomization test
Under the sharp null of no individual treatment effect and a randomized assignment mechanism, outcome labels are exchangeable across arms. Reassign observed binary outcomes while keeping n_A fixed. Approximate two-sided p-value = (1 + count(|Delta_star| >= |Delta_obs|))/(1+R). This is Monte Carlo randomization inference; interpretation under a weaker null requires additional assumptions.

## 4. Bootstrap uncertainty
Resample users with replacement within each arm. For binary outcomes, a bootstrap count conditional on observed data is Binomial(n_g,p_hat_g). Compute Delta_star for each resample, then the 2.5% and 97.5% percentiles. The percentile interval is approximate, and it is not a posterior credible interval.

## 5. Bayesian conjugacy
Independent priors p_A,p_B ~ Beta(a,b). With x_g successes in n_g trials, posterior p_g | data ~ Beta(a+x_g,b+n_g-x_g). Independent posterior draws yield P(p_B>p_A | data) and a credible interval for p_B-p_A. Prior sensitivity matters especially for small samples.

## 6. Sample size and power
For equal allocation, the normal-approximation per-arm sample size for a two-sided test is

n ≈ [z_(1-alpha/2) sqrt(2 p_bar (1-p_bar)) + z_power sqrt(p_A(1-p_A)+p_B(1-p_B))]^2/(p_B-p_A)^2.

Round up. Compare simulated rejection rates under null and alternative to check calibration and operating power. The formula assumes fixed-horizon testing and independent users.

## 7. Research cautions
Pre-register the primary metric, minimum detectable effect, alpha, sample size and stopping rule. Monitor sample-ratio mismatch, missingness, exposure logging, interference, and multiple comparisons. Do not peek at conventional p-values repeatedly without sequential correction. Use business guardrails and expected utility before shipping.
