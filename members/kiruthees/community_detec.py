import matplotlib.cm as cm
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

dn = pd.read_csv("nodes.csv")
de = pd.read_csv("edges.csv")

# 1. build bi-adjacency & project to ingredient space
ru, ri = np.unique(de["Source"], return_inverse=True)
iu, ii = np.unique(de["Target"], return_inverse=True)
nr, ni = len(ru), len(iu)

b = csr_matrix((np.ones(len(de), dtype=np.int32), (ri, ii)), shape=(nr, ni))
c = (b.T @ b).toarray()
deg = np.diag(c)

# 2. compute jaccard similarity edges
up = np.triu_indices(ni, k=1)
w = c[up] / (deg[up[0]] + deg[up[1]] - c[up])

# filter backbone: support >= 15 recipes, jaccard >= 0.08 to isolate cohesive clusters
mask = (deg[up[0]] >= 15) & (deg[up[1]] >= 15) & (w >= 0.08)
e_df = pd.DataFrame(
    {"u": iu[up[0]][mask], "v": iu[up[1]][mask], "w": w[mask]}
)

g = nx.Graph()
for _, r in e_df.iterrows():
    g.add_edge(r["u"], r["v"], weight=r["w"])

# keep largest connected component for stable modularity
lcc = max(nx.connected_components(g), key=len)
g_sub = g.subgraph(lcc).copy()

# 3. louvain community detection
comms = nx.community.louvain_communities(g_sub, weight="w", seed=42)
q = nx.community.modularity(g_sub, comms, weight="w")

# sort communities by size (drop small noise clusters < 5 nodes)
comms = [c for c in sorted(comms, key=len, reverse=True) if len(c) >= 5]
node_comm = {n: i for i, c in enumerate(comms) for n in c}

print(f"=== INGREDIENT MODULARITY & CLUSTERING ===")
print(f"analyzed backbone nodes: {g_sub.number_of_nodes()}")
print(f"analyzed backbone edges: {g_sub.number_of_edges()}")
print(f"modularity Q: {q:.4f}")
print(f"detected major functional communities: {len(comms)}\n")

# identify top central hubs per community
cmap_pts = cm.get_cmap("tab10", len(comms))
comm_info = []
for i, c in enumerate(comms):
    sub = g_sub.subgraph(c)
    deg_c = dict(sub.degree(weight="w"))
    top_hubs = sorted(deg_c.items(), key=lambda x: x[1], reverse=True)[:5]
    names = [h[0] for h in top_hubs]
    print(f"[Community {i+1}] (Nodes: {len(c)}):")
    print(f"  Core Hubs: {', '.join(names)}")
    comm_info.append((i, len(c), names))

# 4. visualization
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(18, 8), gridspec_kw={"width_ratios": [1.4, 1]}
)

# layout
pos = nx.spring_layout(g_sub, k=0.35, seed=42)
node_cols = [
    cmap_pts(node_comm.get(n, 0)) if n in node_comm else (0.7, 0.7, 0.7, 0.3)
    for n in g_sub.nodes()
]
node_sz = [g_sub.degree(n, weight="w") * 45 for n in g_sub.nodes()]

# draw network
nx.draw_networkx_edges(
    g_sub, pos, ax=ax1, alpha=0.15, edge_color="gray", width=0.8
)
nx.draw_networkx_nodes(
    g_sub, pos, ax=ax1, node_color=node_cols, node_size=node_sz, alpha=0.9
)

# label top 3 hubs per community
labels = {}
for i, c in enumerate(comms):
    sub = g_sub.subgraph(c)
    deg_c = dict(sub.degree(weight="w"))
    for h, _ in sorted(deg_c.items(), key=lambda x: x[1], reverse=True)[:3]:
        labels[h] = h
nx.draw_networkx_labels(
    g_sub, pos, labels, ax=ax1, font_size=8, font_weight="bold"
)

ax1.set_title(
    f"Ingredient Functional Modules (Louvain Modularity Q = {q:.3f})",
    fontsize=12,
)
ax1.axis("off")

# community size & hub profile bar chart
c_ids = [f"C{x[0]+1}" for x in comm_info]
c_lens = [x[1] for x in comm_info]
bars = ax2.bar(
    c_ids, c_lens, color=[cmap_pts(i) for i in range(len(comms))], alpha=0.85
)
ax2.set_title("Community Sizes & Dominant Culinary Pillars", fontsize=12)
ax2.set_xlabel("Community")
ax2.set_ylabel("Ingredient Count")
ax2.grid(axis="y", ls="--", alpha=0.4)

# annotate bar charts with core ingredients
for bar, info in zip(bars, comm_info):
    y = bar.get_height()
    hubs_txt = "\n".join(info[2][:3])
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        y / 2,
        hubs_txt,
        ha="center",
        va="center",
        fontsize=8,
        color="black",
        fontweight="bold",
    )

plt.tight_layout()
plt.savefig("masala_ingredient_communities.png", dpi=300)
plt.show()