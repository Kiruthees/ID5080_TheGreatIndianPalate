import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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

m = de.merge(
    dn[["Id", "Cuisine", "Color"]].dropna(subset=["Cuisine"]),
    left_on="Source",
    right_on="Id",
    how="inner",
)

fig, ax = plt.subplots(1, 3, figsize=(18, 5))

# ----------------------------------------------------
# metric 1: culinary power couples (if X, how often Y?)
# ----------------------------------------------------
# pick top 25 popular ingredients
top_ing = de["Target"].value_counts().head(25).index.tolist()
sub_e = de[de["Target"].isin(top_ing)]
r_groups = sub_e.groupby("Source")["Target"].apply(set)

couples = []
for a in top_ing[:15]:
    for b in top_ing:
        if a == b:
            continue
        has_a = sum(1 for s in r_groups if a in s)
        has_both = sum(1 for s in r_groups if a in s and b in s)
        if has_a >= 50:
            couples.append({"A": a, "B": b, "Pct": (has_both / has_a) * 100})

df_c = (
    pd.DataFrame(couples)
    .sort_values("Pct", ascending=False)
    .drop_duplicates("Pct")
    .head(8)
)
df_c["Label"] = df_c["A"] + " -> " + df_c["B"]

ax[0].barh(df_c["Label"][::-1], df_c["Pct"][::-1], color="#e67e22", alpha=0.9)
ax[0].set_title(
    "Metric 1: Culinary Power Couples\n(If dish has A, % chance it also has B)",
    fontsize=11,
)
ax[0].set_xlabel("% Co-occurrence")
ax[0].set_xlim(0, 100)
for i, v in enumerate(df_c["Pct"][::-1]):
    ax[0].text(v + 1, i, f"{v:.1f}%", va="center", fontsize=9, fontweight="bold")
ax[0].grid(axis="x", ls=":", alpha=0.5)

# ----------------------------------------------------
# metric 2: the effort meter (avg ingredients per cuisine)
# ----------------------------------------------------
rec_lens = m.groupby(["Cuisine", "Source"])["Target"].count().reset_index()
avg_c = (
    rec_lens.groupby("Cuisine")["Target"]
    .agg(["mean", "count"])
    .query("count >= 30")
    .sort_values("mean")
)

# match regional hex colors if present
cmap = (
    dn.dropna(subset=["Cuisine"])
    .drop_duplicates("Cuisine")
    .set_index("Cuisine")["Color"]
    .to_dict()
)
bar_cols = [cmap.get(c, "#2980b9") for c in avg_c.index]

ax[1].barh(avg_c.index, avg_c["mean"], color=bar_cols, alpha=0.85)
ax[1].axvline(
    rec_lens["Target"].mean(),
    color="red",
    ls="--",
    lw=1,
    label=f"All-India Avg ({rec_lens['Target'].mean():.1f})",
)
ax[1].set_title(
    "Metric 2: The Effort Meter\n(Avg Ingredients per Dish by Cuisine)",
    fontsize=11,
)
ax[1].set_xlabel("Average Number of Ingredients")
ax[1].legend(loc="lower right", fontsize=8)
ax[1].grid(axis="x", ls=":", alpha=0.5)

# ----------------------------------------------------
# metric 3: recipe complexity tiers (everyday vs royal)
# ----------------------------------------------------
all_rec_len = de.groupby("Source")["Target"].count()


def tier(k):
    if k <= 7:
        return "Quick / Simple (3-7)"
    elif k <= 14:
        return "Everyday Cooking (8-14)"
    return "Royal / Festive (15+)"


tiers = all_rec_len.map(tier).value_counts()[
    ["Quick / Simple (3-7)", "Everyday Cooking (8-14)", "Royal / Festive (15+)"]
]

wedges, texts, autotexts = ax[2].pie(
    tiers.values,
    labels=tiers.index,
    autopct="%1.1f%%",
    colors=["#2ecc71", "#3498db", "#9b59b6"],
    startangle=140,
    explode=(0.04, 0.04, 0.06),
    textprops=dict(fontsize=9),
)
for at in autotexts:
    at.set_color("white")
    at.set_weight("bold")
ax[2].set_title(
    "Metric 3: Cooking Effort Distribution\n(All 3,900+ Dishes Categorized)",
    fontsize=11,
)

plt.tight_layout()
plt.savefig(OUT_DIR / "masala_intuitive_metrics.png", dpi=300)
plt.show()

print("=== STATS FOR PPT ===")
print(
    f"Simplest cuisine on average: {avg_c.index[0]} ({avg_c['mean'].iloc[0]:.1f} ingredients)"
)
print(
    f"Most elaborate cuisine: {avg_c.index[-1]} ({avg_c['mean'].iloc[-1]:.1f} ingredients)"
)
print(f"Top power couple: {df_c.iloc[0]['Label']} ({df_c.iloc[0]['Pct']:.1f}%)")
