import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import powerlaw

# ============================================================
# CONFIGURATION TOGGLE
# True  -> 2 separate image files (2 plots each)
# False -> 1 single combined file (2x2 grid)
# ============================================================
SPLIT_FIGS = False

# 1. LOAD DATA
dn = pd.read_csv("nodes.csv")
de = pd.read_csv("edges.csv")

ing_deg = de["Target"].value_counts()
rec_deg = de["Source"].value_counts()

# 2. POWER-LAW FITTING: LOG-BINNING REGRESSION + CONSTRAINED MLE
# ------------------------------------------------------------
# Method A: Logarithmic Binning (Physics & Complex Networks standard)
max_k = ing_deg.max()
bins = np.logspace(0, np.log10(max_k + 1), num=22)
counts, bin_edges = np.histogram(ing_deg.values, bins=bins)
bin_widths = np.diff(bin_edges)
bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])  # geometric center

# Probability density: p(k) = count / (N_total * bin_width)
mask = counts > 0
k_bin = bin_centers[mask]
p_bin = counts[mask] / (len(ing_deg) * bin_widths[mask])

log_k = np.log10(k_bin)
log_p = np.log10(p_bin)
slope_logbin, intercept_logbin = np.polyfit(log_k, log_p, 1)
gamma_logbin = -slope_logbin

# Method B: Clauset Discrete MLE with constrained xmin=2 (retains full tail)
fit_mle = powerlaw.Fit(ing_deg.values, discrete=True, xmin=2.0, verbose=False)
gamma_mle = fit_mle.power_law.alpha

print("=== INGREDIENT DEGREE STATS ===")
print(f"Unique ingredients: {len(ing_deg)}")
print(f"Mean usage: {ing_deg.mean():.2f}")
print(f"Median usage: {ing_deg.median():.1f}")
print(f"Max usage: {ing_deg.max()} ({ing_deg.index[0]})")
print(f"Ingredients used in only 1 dish: {(ing_deg == 1).sum()}")

print("\n=== RECALCULATED POWER LAW RESULTS ===")
print(f"1. Log-Binned Linear Regression: gamma = {gamma_logbin:.3f}")
print(f"2. Clauset Discrete MLE (xmin=2): gamma = {gamma_mle:.3f}")
print(f"Empirical scaling formula: P(k) ~ k^(-{gamma_logbin:.2f})")

print("\n=== RECIPE COMPLEXITY STATS ===")
print(f"Unique recipes: {len(rec_deg)}")
print(f"Mean ingredients per dish: {rec_deg.mean():.2f}")
print(f"Median ingredients per dish: {rec_deg.median():.1f}")

# 3. FIGURE SETUP
if SPLIT_FIGS:
    f1, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))
    f2, (ax3, ax4) = plt.subplots(1, 2, figsize=(15, 5.5))
else:
    f_all, ax_grid = plt.subplots(2, 2, figsize=(15, 11))
    ax1, ax2, ax3, ax4 = (
        ax_grid[0, 0],
        ax_grid[0, 1],
        ax_grid[1, 0],
        ax_grid[1, 1],
    )

# ------------------------------------------------------------
# PLOT 1: TOP 20 INGREDIENTS
# ------------------------------------------------------------
top20 = ing_deg.head(20)
ax1.barh(top20.index[::-1], top20.values[::-1], color="#e74c3c")
ax1.set_title("Top 20 Most Frequent Ingredients")
ax1.set_xlabel("Recipe Count")
ax1.set_ylabel("Ingredient")

# ------------------------------------------------------------
# PLOT 2: INGREDIENT DEGREE DISTRIBUTION (CORRECTED FIT)
# ------------------------------------------------------------
# Plot log-binned empirical points
ax2.scatter(
    k_bin,
    p_bin,
    color="#8e44ad",
    s=40,
    alpha=0.85,
    edgecolor="black",
    linewidth=0.5,
    label="Observed $P(k)$ (Log-Binned)",
)

# Plot linear regression through log-binned data
k_fit_line = np.logspace(0, np.log10(max_k), 100)
p_fit_line = (10**intercept_logbin) * (k_fit_line**slope_logbin)
ax2.plot(
    k_fit_line,
    p_fit_line,
    color="#e74c3c",
    ls="--",
    lw=2,
    label=f"Power-Law Fit ($\\gamma = {gamma_logbin:.2f}$)",
)

ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_title(
    f"Ingredient Degree Distribution ($\\gamma \\approx {gamma_logbin:.2f}$)"
)
ax2.set_xlabel("Degree $k$ (Recipe Occurrences)")
ax2.set_ylabel("Probability Density $P(k)$")
ax2.grid(True, which="both", linestyle="--", alpha=0.3)
ax2.legend()

# ------------------------------------------------------------
# PLOT 3: RECIPE COMPLEXITY HISTOGRAM
# ------------------------------------------------------------
ax3.hist(
    rec_deg.values,
    bins=np.arange(rec_deg.min(), rec_deg.max() + 2),
    color="#2980b9",
    edgecolor="black",
    align="left",
)
ax3.axvline(
    rec_deg.mean(),
    color="red",
    linestyle="--",
    linewidth=1.5,
    label=f"Mean: {rec_deg.mean():.1f}",
)
ax3.axvline(
    rec_deg.median(),
    color="green",
    linestyle=":",
    linewidth=1.5,
    label=f"Median: {rec_deg.median():.1f}",
)
ax3.set_title("Recipe Complexity (# Ingredients)")
ax3.set_xlabel("Number of Ingredients")
ax3.set_ylabel("Frequency")
ax3.legend()

# ------------------------------------------------------------
# PLOT 4: RECIPE COMPLEXITY BY CUISINE (BOXPLOT)
# ------------------------------------------------------------
if "Cuisine" in dn.columns:
    cols = ["Id", "Cuisine"] + (["Color"] if "Color" in dn.columns else [])
    df_rec = pd.DataFrame({"Id": rec_deg.index, "k": rec_deg.values}).merge(
        dn[cols].dropna(subset=["Cuisine"]), on="Id", how="inner"
    )
    top_c = df_rec["Cuisine"].value_counts().head(10).index
    df_sub = df_rec[df_rec["Cuisine"].isin(top_c)]
    ord_c = df_sub.groupby("Cuisine")["k"].median().sort_values().index
    bdata = [df_sub[df_sub["Cuisine"] == c]["k"].values for c in ord_c]

    bp = ax4.boxplot(bdata, tick_labels=ord_c, vert=False, patch_artist=True)
    if "Color" in df_sub.columns:
        cmap = (
            df_sub.drop_duplicates("Cuisine")
            .set_index("Cuisine")["Color"]
            .to_dict()
        )
        for patch, c in zip(bp["boxes"], ord_c):
            col = cmap.get(c, "#3498db")
            patch.set_facecolor("#3498db" if pd.isna(col) else col)
            patch.set_alpha(0.7)
    else:
        for patch in bp["boxes"]:
            patch.set_facecolor("#3498db")
            patch.set_alpha(0.7)

    ax4.set_title("Recipe Complexity by Top Cuisines")
    ax4.set_xlabel("Ingredients per Dish")
    ax4.set_ylabel("Cuisine")
else:
    ax4.axis("off")

# 4. SAVE AND SHOW
if SPLIT_FIGS:
    f1.tight_layout()
    f1.savefig("masala_degrees_powerlaw.png", dpi=300, bbox_inches="tight")
    f2.tight_layout()
    f2.savefig("masala_recipe_complexity.png", dpi=300, bbox_inches="tight")
else:
    f_all.tight_layout()
    f_all.savefig(
        "masala_degree_distributions.png", dpi=300, bbox_inches="tight"
    )

plt.show()