import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

de = pd.read_csv("edges.csv")
k_raw = de["Target"].value_counts().values.astype(float)
n = len(k_raw)

# 1. raw pdf log-log ols
cnts = pd.Series(k_raw).value_counts().sort_index()
k_pdf = cnts.index.values.astype(float)
p_pdf = cnts.values.astype(float)

m_pdf = (k_pdf >= 1) & (k_pdf <= 80)
x_pdf, y_pdf = np.log10(k_pdf[m_pdf]), np.log10(p_pdf[m_pdf])
slope_pdf, c_pdf = np.polyfit(x_pdf, y_pdf, 1)
gamma_pdf = -slope_pdf

# 2. ccdf ols (cumulative fit)
k_sorted = np.sort(k_raw)
ccdf = 1.0 - np.arange(n) / n

m_ccdf = (k_sorted >= 2) & (k_sorted <= 200)
x_ccdf, y_ccdf = np.log10(k_sorted[m_ccdf]), np.log10(ccdf[m_ccdf])
slope_ccdf, c_ccdf = np.polyfit(x_ccdf, y_ccdf, 1)
gamma_ccdf = 1.0 - slope_ccdf

# 3. clauset discrete mle fit
k_min = 2.0
tail = k_raw[k_raw >= k_min]
gamma_mle = 1.0 + len(tail) / np.sum(np.log(tail / (k_min - 0.5)))

print("=== POWER LAW RECOMPUTATION & COMPARISON ===")
print(f"Total Ingredients: {n}")
print(f"1. Raw PDF Log-Log OLS:  gamma = {gamma_pdf:.3f}")
print(f"2. Cumulative CCDF OLS:  gamma = {gamma_ccdf:.3f}")
print(f"3. Discrete Clauset MLE: gamma = {gamma_mle:.3f} (k_min={int(k_min)})")

# 4. plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# raw pdf
ax1.scatter(k_pdf, p_pdf, color="#8e44ad", alpha=0.6, s=25, label="Observed $P(k)$")
k_g1 = np.logspace(np.log10(1), np.log10(80), 50)
ax1.plot(k_g1, (10**c_pdf) * (k_g1**slope_pdf), color="#e74c3c", ls="--", lw=2,
         label=f"PDF Fit: $\\gamma={gamma_pdf:.2f}$")
ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_title("Method 1: Raw Frequency $P(k)$")
ax1.set_xlabel("Degree $k$")
ax1.set_ylabel("Count $P(k)$")
ax1.grid(True, which="both", ls="--", alpha=0.3)
ax1.legend()

# ccdf (fixed \geq parser issue)
ax2.scatter(k_sorted, ccdf, color="#2980b9", alpha=0.6, s=15, label="Observed CCDF")
k_g2 = np.logspace(np.log10(2), np.log10(200), 50)
ax2.plot(k_g2, (10**c_ccdf) * (k_g2**slope_ccdf), color="#d35400", ls="--", lw=2,
         label=f"CCDF Fit: $\\gamma={gamma_ccdf:.2f}$")
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_title(r"Method 2: Cumulative Distribution $P(K \geq k)$")
ax2.set_xlabel("Degree $k$")
ax2.set_ylabel(r"Probability $P(K \geq k)$")
ax2.grid(True, which="both", ls="--", alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig("masala_power_law_validation.png", dpi=300)
plt.show()