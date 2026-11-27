import argparse, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pathlib import Path

def find_root():
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "MANIFEST.md").exists():
            return d
    raise FileNotFoundError("Run this from inside the project folder")

BASE_DIR = find_root()
DATA_FILE   = BASE_DIR / "members" / "sasanka mouli" / "cooccurrence_results.csv"
OUT_DIR = BASE_DIR / "members" / "sasanka mouli" / "figs"

PALETTE = {
    "ns": "#c8c8c8",
    "universal (both nulls)": "#1b9e77",
    "regional (pooled only)": "#e6820e",
    "masked (stratified only)": "#7b4fb3",
    "sign flip": "#d62728",
}
ORDER = list(PALETTE)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.dpi": 110, "savefig.dpi": 170, "savefig.bbox": "tight"})


def pair_label(r):
    return f"{r.a} + {r.b}"


def legend_handles(classes):
    from matplotlib.lines import Line2D
    return [Line2D([], [], marker="o", ls="", color=PALETTE[c], label=c, markersize=7)
            for c in ORDER if c in classes]


# --------------------------------------------------------------------------- 1
def fig_scatter(df, path, n_label=0):
    fig, ax = plt.subplots(figsize=(7.5, 7))
    for c in ORDER:
        s = df[df["class"] == c]
        if len(s):
            ax.scatter(s.z_pool, s.z_strat, s=10 if c == "ns" else 16, alpha=0.35 if c == "ns" else 0.7,
                       color=PALETTE[c], linewidths=0, zorder=1 if c == "ns" else 2)
    lim = np.ceil(max(df.z_pool.abs().max(), df.z_strat.abs().max()) / 5) * 5
    ax.plot([-lim, lim], [-lim, lim], "k--", lw=0.8, alpha=0.6)
    ax.axhline(0, color="k", lw=0.5, alpha=0.4); ax.axvline(0, color="k", lw=0.5, alpha=0.4)
    d = df[df["class"].isin(["regional (pooled only)", "masked (stratified only)"])].copy()
    d["gap"] = (d.z_pool - d.z_strat).abs()
    for _, r in d.nlargest(n_label, "gap").iterrows():
        ax.annotate(pair_label(r), (r.z_pool, r.z_strat), xytext=(5, 5), textcoords="offset points",
                    fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.4, color="gray"))
    ax.set_xlabel("z (pooled null)"); ax.set_ylabel("z (cuisine-stratified null)")
    ax.set_title("Does controlling for cuisine change the signal?\n(dashed = no change; labelled = largest shifts)")
    ax.legend(handles=legend_handles(df["class"].unique()), loc="upper left", frameon=False)
    fig.savefig(path); plt.close(fig)


# --------------------------------------------------------------------------- 2
def fig_obs_exp(df, path, n_label=0):
    fig, ax = plt.subplots(figsize=(7.5, 7))
    x = df.null_mean_pool + 0.5; y = df.obs + 0.5
    for c in ORDER:
        m = df["class"] == c
        if m.any():
            ax.scatter(x[m], y[m], s=10 if c == "ns" else 16, alpha=0.3 if c == "ns" else 0.7,
                       color=PALETTE[c], linewidths=0)
    lo, hi = min(x.min(), y.min()) * 0.8, max(x.max(), y.max()) * 1.3
    ax.plot([lo, hi], [lo, hi], "k--", lw=0.8)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    sig = df[df.q_pool < 0.05].copy()
    sig["lr"] = np.log2((sig.obs + 0.5) / (sig.null_mean_pool + 0.5))
    for _, r in pd.concat([sig.nlargest(n_label, "lr"), sig.nsmallest(n_label, "lr")]).iterrows():
        ax.annotate(pair_label(r), (r.null_mean_pool + 0.5, r.obs + 0.5), xytext=(4, 4),
                    textcoords="offset points", fontsize=7)
    ax.set_xlabel("expected co-occurrences under pooled null (+0.5)")
    ax.set_ylabel("observed co-occurrences (+0.5)")
    ax.set_title("Effect size: observed vs expected (log-log)\nabove line = pairing, below = avoidance")
    ax.legend(handles=legend_handles(df["class"].unique()), loc="upper left", frameon=False)
    fig.savefig(path); plt.close(fig)


# --------------------------------------------------------------------------- 3
def fig_top_pairs(df, path, top=15):
    fig, axes = plt.subplots(1, 2, figsize=(13, 0.34 * top + 2), sharex=False)
    for ax, (title, sub) in zip(axes, [("Most over-represented", df.nlargest(top, "z_pool")),
                                       ("Most avoided", df.nsmallest(top, "z_pool"))]):
        sub = sub.iloc[::-1]
        y = np.arange(len(sub))
        ax.barh(y, sub.z_pool, color=[PALETTE[c] for c in sub["class"]], alpha=0.9)
        ax.scatter(sub.z_strat, y, marker="D", color="k", s=22, zorder=3, label="z (stratified)")
        ax.set_yticks(y); ax.set_yticklabels([pair_label(r) for r in sub.itertuples()], fontsize=8)
        ax.set_title(title); ax.set_xlabel("z (pooled)  |  bar = pooled, diamond = stratified")
        ax.axvline(0, color="k", lw=0.6)
        for yi, r in zip(y, sub.itertuples()):
            ax.text(r.z_pool, yi, f" {r.obs} vs {r.null_mean_pool:.0f}", va="center",
                    ha="left" if r.z_pool > 0 else "right", fontsize=6.5, color="#444")
    # axes[0].legend(handles=legend_handles(df["class"].unique()) , loc="lower right", frameon=False, fontsize=8)
    fig.suptitle("Strongest departures from the degree-preserving null (text = observed vs expected)", y=1.0)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


# --------------------------------------------------------------------------- 4
def fig_heatmap(df, path, n=50, clip=15):
    tot = pd.concat([df.groupby("a").obs.sum(), df.groupby("b").obs.sum()]).groupby(level=0).sum()
    keep = tot.nlargest(n).index
    sub = df[df.a.isin(keep) & df.b.isin(keep)]
    M = pd.DataFrame(0.0, index=keep, columns=keep)
    for r in sub.itertuples():
        M.loc[r.a, r.b] = M.loc[r.b, r.a] = r.z_pool
    M = M.clip(-clip, clip)
    g = sns.clustermap(M, cmap="RdBu_r", center=0, vmin=-clip, vmax=clip, figsize=(12, 11),
                       xticklabels=True, yticklabels=True, linewidths=0.2, linecolor="white",
                       cbar_kws={"label": f"z (pooled), clipped at ±{clip}"}, method="average",
                       dendrogram_ratio=0.1)
    g.ax_heatmap.tick_params(labelsize=7)
    g.fig.suptitle(f"Ingredient co-occurrence z-scores (top {n} ingredients by total co-occurrence)\n"
                   "red = over-represented, blue = avoided", y=1.02)
    g.savefig(path); plt.close(g.fig)


# --------------------------------------------------------------------------- 5
def fig_network(df, path, min_z=12, max_edges=150):
    e = df[(df["class"] == "universal (both nulls)") & (df.z_strat >= min_z) & (df.z_pool >= min_z)]
    e = e.nlargest(max_edges, "z_strat")
    G = nx.Graph()
    for r in e.itertuples():
        G.add_edge(r.a, r.b, w=r.z_strat, obs=r.obs)
        
    comms = list(nx.algorithms.community.greedy_modularity_communities(G, weight="w"))
    cmap = {n: i for i, c in enumerate(comms) for n in c}
    colors = sns.color_palette("tab10", max(len(comms), 1))
    
    pos = {}
    components = [G.subgraph(c).copy() for c in sorted(nx.connected_components(G), key=len, reverse=True)]
    
    spacing = 1.8 
    cols = int(np.ceil(np.sqrt(len(components))))
    
    for idx, comp in enumerate(components):
        comp_k = 10.0 / np.sqrt(max(len(comp), 1))
        pos_comp = nx.spring_layout(comp, weight="w", k=comp_k, seed=3, iterations=200)
        
        col = idx % cols
        row = idx // cols
        center_x = col * spacing
        center_y = -row * spacing
        
        for node in pos_comp:
            pos[node] = pos_comp[node] + [center_x, center_y]
    # ----------------------------------------------------

    fig, ax = plt.subplots(figsize=(12, 10))
    w = np.array([G[u][v]["w"] for u, v in G.edges])
    
    nx.draw_networkx_edges(G, pos, ax=ax, width=0.4 + 3.0 * (w - w.min()) / max(np.ptp(w), 1e-9),
                           alpha=0.4, edge_color="#666")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=[colors[cmap[n]] for n in G],
                           node_size=[60 + 40 * G.degree(n) for n in G], alpha=0.92,
                           edgecolors="white", linewidths=0.8)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=7)
    
    ax.set_axis_off()
    ax.set_title(f"Strongest cuisine-independent pairings ({G.number_of_edges()} pairs with z ≥ {min_z} "
                 f"under both nulls)\nnode size = #partners, color = greedy-modularity community "
                 f"({len(comms)} groups)")
    fig.savefig(path)
    plt.close(fig)

# --------------------------------------------------------------------------- 6
def fig_dumbbell(df, path, top=12):
    reg = df[df["class"] == "regional (pooled only)"].copy()
    reg = reg.reindex(reg.z_pool.abs().sort_values(ascending=False).index).head(top)
    msk = df[df["class"] == "masked (stratified only)"].copy()
    msk = msk.reindex(msk.z_strat.abs().sort_values(ascending=False).index).head(top)
    fig, axes = plt.subplots(1, 2, figsize=(13, 0.36 * top + 2))
    for ax, (title, sub, col) in zip(axes, [("Regional: signal shrinks once cuisine is controlled", reg, "regional (pooled only)"),
                                            ("Masked: signal only visible within cuisines", msk, "masked (stratified only)")]):
        sub = sub.iloc[::-1]; y = np.arange(len(sub))
        ax.hlines(y, sub.z_pool, sub.z_strat, color=PALETTE[col], lw=2, alpha=0.7)
        ax.scatter(sub.z_pool, y, color="white", edgecolor="k", s=45, zorder=3, label="pooled")
        ax.scatter(sub.z_strat, y, color=PALETTE[col], edgecolor="k", s=45, zorder=3, label="stratified")
        ax.axvline(0, color="k", lw=0.6)
        for lim in (-3, 3):
            ax.axvline(lim, color="gray", lw=0.5, ls=":")
        ax.set_yticks(y); ax.set_yticklabels([pair_label(r) for r in sub.itertuples()], fontsize=8)
        ax.set_title(title, fontsize=10); ax.set_xlabel("z"); ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


os.makedirs(OUT_DIR, exist_ok=True)
df = pd.read_csv(DATA_FILE)
out = lambda f: os.path.join(OUT_DIR, f)
fig_scatter(df, out("ic_pooled_vs_stratified.svg"))
fig_obs_exp(df, out("ic_obs_vs_expected.svg"))
fig_top_pairs(df, out("ic_top_pairs.svg"))
fig_heatmap(df, out("ic_heatmap.svg"))
fig_network(df, out("ic_strongest_pairings_modularity.svg"))
fig_dumbbell(df, out("ic_regional_vs_masked.svg"))
