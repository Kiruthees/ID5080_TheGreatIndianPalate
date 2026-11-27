import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

de = pd.read_csv("edges.csv")

# ingredient counts and ranks
ic = de["Target"].value_counts()
r = np.arange(1, len(ic) + 1)
c = ic.values

# fit zipf-mandelbrot on log scale up to rank 300
m = r <= 300
lr, lc = r[m], np.log10(c[m])


def zm_log(x, logC, q, a):
  return logC - a * np.log10(x + q)


popt, _ = curve_fit(
    zm_log,
    lr,
    lc,
    p0=[5.5, 10.0, 1.8],
    bounds=([2.0, 0.0, 0.5], [8.0, 50.0, 3.0]),
)
logC, q, alpha = popt

print("=== ZIPF-MANDELBROT FIT RESULTS ===")
print(f"Saturation Shift (q): {q:.2f}")
print(f"Scaling Exponent (alpha): {alpha:.2f}")
print(f"Formula: Count(r) = 10^{logC:.2f} / (r + {q:.1f})^{alpha:.2f}")

# plot
plt.figure(figsize=(9, 6))
plt.scatter(r, c, color="#2c3e50", alpha=0.6, s=25, label="Observed Spices")

# fitted curve
rf = np.logspace(0, np.log10(len(r)), 200)
cf = 10 ** zm_log(rf, *popt)
plt.plot(
    rf,
    cf,
    color="#e74c3c",
    ls="--",
    lw=2,
    label=f"Zipf-Mandelbrot Fit\n$\\alpha = {alpha:.2f},\\ q = {q:.1f}$",
)

# annotations
ann = [1, 2, 3, 5, 10, 20]
for idx in ann:
  plt.annotate(
      f"#{idx} {ic.index[idx-1]}",
      xy=(idx, c[idx - 1]),
      xytext=(idx * 1.3, c[idx - 1] * 1.15),
      arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
      fontsize=8.5,
      fontweight="bold",
  )

plt.xscale("log")
plt.yscale("log")
plt.title(
    f"Zipf-Mandelbrot Law: Rank vs Frequency ($\\alpha \\approx {alpha:.2f},"
    f"\\ q \\approx {q:.1f}$)",
    fontsize=12,
    pad=12,
)
plt.xlabel("Ingredient Rank $r$ (Log Scale)", fontsize=10)
plt.ylabel("Recipe Occurrences (Log Scale)", fontsize=10)
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.legend(fontsize=10)

plt.tight_layout()
plt.savefig("masala_zipf_mandelbrot.png", dpi=300)
plt.show()