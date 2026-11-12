"""Two-sided A/B test for conversion rates, with confidence interval."""
from pathlib import Path
import math
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]

def analyze(df):
    required = {"user_id", "variant", "converted"}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns: {required - set(df.columns)}")
    if df.user_id.duplicated().any() or not df.variant.isin(["A", "B"]).all() or not df.converted.isin([0, 1]).all():
        raise ValueError("Invalid experiment data")
    summary = df.groupby("variant")["converted"].agg(["sum", "count", "mean"]).reindex(["A", "B"])
    if summary.isna().any().any() or (summary["count"] == 0).any():
        raise ValueError("Both variants must contain users")
    x_a, x_b = summary.loc["A", "sum"], summary.loc["B", "sum"]
    n_a, n_b = summary.loc["A", "count"], summary.loc["B", "count"]
    p_a, p_b = x_a/n_a, x_b/n_b
    pooled = (x_a+x_b)/(n_a+n_b)
    se_null = math.sqrt(pooled*(1-pooled)*(1/n_a+1/n_b))
    z = (p_b-p_a)/se_null if se_null else 0.0
    p_value = 2*norm.sf(abs(z)) if se_null else 1.0
    se_ci = math.sqrt(p_a*(1-p_a)/n_a + p_b*(1-p_b)/n_b)
    delta = p_b-p_a
    ci = (delta-1.96*se_ci, delta+1.96*se_ci)
    return summary, {"lift_absolute": delta, "lift_relative": delta/p_a if p_a else float("nan"), "z_score": z, "p_value": p_value, "ci_low": ci[0], "ci_high": ci[1], "significant_at_05": p_value < .05}

def main():
    df = pd.read_csv(ROOT / "data" / "experiment.csv")
    summary, stats = analyze(df)
    (ROOT / "results").mkdir(exist_ok=True)
    summary.to_csv(ROOT / "results" / "summary.csv")
    pd.Series(stats).to_json(ROOT / "results" / "statistics.json", indent=2)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(summary.index, summary["mean"]*100)
    ax.set(ylabel="Conversion rate (%)", xlabel="Variant", title="A/B test conversion rates")
    for i, v in enumerate(summary["mean"]*100):
        ax.text(i, v+.1, f"{v:.2f}%", ha="center")
    fig.tight_layout()
    fig.savefig(ROOT / "results" / "conversion_rates.png", dpi=160)
    plt.close(fig)
    print(summary.to_string())
    print("\nResults:")
    for k,v in stats.items(): print(f"{k}: {v}")
    print("\nInterpretation: " + ("Evidence of a difference at 5% significance." if stats["significant_at_05"] else "Insufficient evidence of a difference at 5% significance."))

if __name__ == "__main__": main()
