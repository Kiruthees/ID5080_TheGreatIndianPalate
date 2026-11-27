import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path

def find_root():
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "MANIFEST.md").exists():
            return d
    raise FileNotFoundError("Run this from inside the project folder")

BASE_DIR = find_root()
DATA_DIR = BASE_DIR / "common" / "data_processed"
OUT_DIR = BASE_DIR / "members" / "kiruthees"
dn = pd.read_csv(DATA_DIR / "nodes_9.0.csv")
de = pd.read_csv(DATA_DIR / "edges_6.0.csv")

# filter out generic "indian" to isolate distinct states/regions
dn_reg = dn.dropna(subset=["Cuisine"]).copy()
dn_reg = dn_reg[
    ~dn_reg["Cuisine"]
    .str.strip()
    .str.lower()
    .isin(["indian", "generic", "general"])
]

# merge recipes with regional metadata
m = de.merge(
    dn_reg[["Id", "Cuisine", "Color"]],
    left_on="Source",
    right_on="Id",
    how="inner",
)

# global baseline counts (across all dishes) & regional counts
nr_tot = de["Source"].nunique()
ni_tot = de.groupby("Target")["Source"].nunique()
nc = m.groupby("Cuisine")["Source"].nunique()
nic = (
    m.groupby(["Cuisine", "Target"])["Source"]
    .nunique()
    .reset_index(name="Nic")
)

# lift = P(i|c) / P(i)
nic["Nc"] = nic["Cuisine"].map(nc)
nic["Ni"] = nic["Target"].map(ni_tot)
nic["Lift"] = (nic["Nic"] / nic["Nc"]) / (nic["Ni"] / nr_tot)

# support filter: at least 5 recipes in that regional cuisine
sig = nic[nic["Nic"] >= 5].copy()
top_c = nc.sort_values(ascending=False).head(5).index

# ----------------------------------------------------
# figure 1: heatmap + top overall lift markers
# ----------------------------------------------------
top_sigs = []
for c in top_c:
    top_sigs.extend(
        sig[sig["Cuisine"] == c]
        .sort_values("Lift", ascending=False)
        .head(3)["Target"]
        .tolist()
    )
u_sigs = list(dict.fromkeys(top_sigs))

heat_df = sig[sig["Cuisine"].isin(top_c) & sig["Target"].isin(u_sigs)].pivot(
    index="Target", columns="Cuisine", values="Lift"
).fillna(0)

fig1, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(16, 7), gridspec_kw={"width_ratios": [1.2, 1]}
)

sns.heatmap(
    heat_df,
    cmap="YlOrRd",
    annot=True,
    fmt=".1f",
    linewidths=0.5,
    cbar_kws={"label": "Lift Score"},
    ax=ax1,
)
ax1.set_title("Regional Ingredient Specificity (Lift Matrix)", fontsize=11, pad=10)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=30, ha="right", fontsize=9)
ax1.set_ylabel("Marker Ingredients")

top_all = (
    sig[sig["Cuisine"].isin(top_c)]
    .sort_values("Lift", ascending=False)
    .drop_duplicates("Target")
    .head(12)
)
ax2.barh(
    top_all["Target"][::-1], top_all["Lift"][::-1], color="#d35400", alpha=0.85
)
ax2.set_title(
    "Highest Lift Markers Across Regional Cuisines", fontsize=11, pad=10
)
ax2.set_xlabel("Lift (Fold-Enrichment over Baseline)")
ax2.grid(axis="x", ls="--", alpha=0.4)

plt.tight_layout()
plt.savefig(OUT_DIR / "masala_cuisine_lift_clean.png", dpi=300)
plt.show()

# ----------------------------------------------------
# figure 2: 2x2 regional signatures for top 4 cuisines
# ----------------------------------------------------
cmap_dict = (
    dn_reg.drop_duplicates("Cuisine")
    .set_index("Cuisine")["Color"]
    .to_dict()
)
top4_c = top_c[:4]

fig2, axes2 = plt.subplots(2, 2, figsize=(14, 8))
axes2 = axes2.flatten()

for idx, c in enumerate(top4_c):
    sub = sig[sig["Cuisine"] == c].sort_values("Lift", ascending=False).head(8)
    col = cmap_dict.get(c, "#3498db")
    if pd.isna(col):
        col = "#3498db"
    axes2[idx].barh(sub["Target"][::-1], sub["Lift"][::-1], color=col, alpha=0.85)
    axes2[idx].axvline(1.0, color="black", ls="--", lw=1, alpha=0.7)
    axes2[idx].set_title(f"{c} (Top Regional Markers)")
    axes2[idx].set_xlabel("Lift (Fold-Enrichment over Baseline)")
    axes2[idx].grid(axis="x", ls=":", alpha=0.4)

plt.tight_layout()
plt.savefig(OUT_DIR / "masala_regional_signatures.png", dpi=300)
plt.show()
