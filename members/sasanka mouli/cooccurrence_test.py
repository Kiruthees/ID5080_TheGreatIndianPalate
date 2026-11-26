import argparse, random
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import norm, poisson

# # ----------------------------------------------------------------------------
# # 1. Loading + cleaning
# # ----------------------------------------------------------------------------
# # Confident spelling / plural variants only. Review before extending: merging
# # things like "slivered badam" -> "badam" or "pearl onion" -> "small onion" is a
# # modelling decision, not a typo fix.
# MERGE = {
#     "red chili powder": "red chilli powder",
#     "whole black pepper corns": "whole black peppercorns",
#     "black pepper corns": "black peppercorns",
#     "flax seed powder": "flaxseed powder",
#     "stone flowers": "stone flower",
#     "kabuli channa": "kabuli chana",
#     "soya chunks": "soy chunks",
#     "avocados": "avocado",
#     "peanut": "peanuts",
#     "kachris": "kachri",
#     "sweet potatoes": "sweet potato",
#     "goond": "gond",
#     "kasoori methi": "kasuri methi",
#     "dried red chillies": "dry red chillies",
#     "red yellow and green bell pepper": "red yellow or green bell pepper",
#     "ragi dosa battter": "ragi dosa batter",
# }


def load(nodes_path, edges_path):
    nodes = pd.read_csv(nodes_path, dtype=str, keep_default_na=False)
    edges = pd.read_csv(edges_path, dtype=str, keep_default_na=False)
    for c in ("Source", "Target"):
        edges[c] = edges[c].str.strip()
    edges["Target"] = edges["Target"].str.lower()#.replace(merge)
    edges = edges.drop_duplicates()          # also removes duplicates created by merging

    rec = nodes[nodes.Type == "Recipe"].copy()
    # rec["Cuisine"] = rec["Cuisine"].str.replace("\ufeff", "", regex=False).str.strip()
    cuisine = rec.set_index("Id")["Cuisine"]
    return edges, cuisine


def build_rows(edges, cuisine, drop_generic_cuisine=None, min_stratum=30):
    recipes = sorted(edges.Source.unique())
    ings = sorted(edges.Target.unique())
    ing_idx = {x: i for i, x in enumerate(ings)}
    grp = edges.groupby("Source")["Target"].apply(lambda s: [ing_idx[t] for t in s])
    rows = [list(grp[r]) for r in recipes]

    strata = cuisine.reindex(recipes).fillna("unknown").to_numpy()
    if drop_generic_cuisine:                       # e.g. "Indian" is a catch-all label
        strata = np.where(strata == drop_generic_cuisine, "unknown", strata)
    counts = pd.Series(strata).value_counts()
    small = set(counts[counts < min_stratum].index)
    strata = np.array(["other" if s in small else s for s in strata])
    return recipes, ings, rows, strata


# ----------------------------------------------------------------------------
# 2. Curveball
# ----------------------------------------------------------------------------
def make_groups(strata):
    groups = [np.flatnonzero(strata == s) for s in np.unique(strata)]
    return [g.tolist() for g in groups if len(g) >= 2]


def curveball(rows_sets, groups, n_trades, rnd):
    sizes = np.array([len(g) for g in groups], dtype=float)
    p = sizes / sizes.sum()
    gi = np.random.default_rng(rnd.randrange(2**32)).choice(len(groups), size=n_trades, p=p)
    for k in gi:
        g = groups[k]
        a, b = rnd.sample(g, 2)
        A, B = rows_sets[a], rows_sets[b]
        a_only = A - B
        b_only = B - A
        if not a_only or not b_only:
            continue
        pool = list(a_only | b_only)
        rnd.shuffle(pool)
        na = len(a_only)
        common = A & B
        rows_sets[a] = common | set(pool[:na])
        rows_sets[b] = common | set(pool[na:])


def cooc(rows_sets, col_map, n_test):
    lens = [0]
    flat = []
    for r in rows_sets:
        idx = [col_map[i] for i in r if col_map[i] >= 0]
        flat.extend(idx)
        lens.append(lens[-1] + len(idx))
    M = sparse.csr_matrix((np.ones(len(flat), dtype=np.float32), np.array(flat), np.array(lens)),
                          shape=(len(rows_sets), n_test))
    return (M.T @ M).toarray()


def null_distribution(rows, strata, col_map, n_test, B, burn_in, thin, seed):
    rnd = random.Random(seed)
    rows_sets = [set(r) for r in rows]
    groups = make_groups(strata)
    n_rows = sum(len(g) for g in groups)
    curveball(rows_sets, groups, burn_in * n_rows, rnd)           # burn-in

    s1 = np.zeros((n_test, n_test)); s2 = np.zeros_like(s1)
    obs = cooc([set(r) for r in rows], col_map, n_test)
    ge = np.zeros_like(s1); le = np.zeros_like(s1)
    for b in range(B):
        curveball(rows_sets, groups, thin * n_rows, rnd)
        C = cooc(rows_sets, col_map, n_test)
        s1 += C; s2 += C * C
        ge += (C >= obs); le += (C <= obs)
    mu = s1 / B
    sd = np.sqrt(np.maximum(s2 / B - mu ** 2, 1e-12))
    p_emp = np.minimum(1.0, 2 * np.minimum((1 + ge) / (B + 1), (1 + le) / (B + 1)))
    return obs, mu, sd, p_emp


# ----------------------------------------------------------------------------
# 3. Inference
# ----------------------------------------------------------------------------
def bh(p):
    p = np.asarray(p); m = len(p)
    order = np.argsort(p); ranked = p[order] * m / (np.arange(m) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m); out[order] = np.minimum(q, 1.0)
    return out


def pair_table(names, obs, mu, sd, p_emp, min_expected):
    iu = np.triu_indices(len(names), k=1)
    df = pd.DataFrame({
        "a": np.array(names)[iu[0]], "b": np.array(names)[iu[1]],
        "obs": obs[iu].astype(int), "null_mean": mu[iu], "null_sd": sd[iu],
        "p_emp": p_emp[iu],
    })
    df["z"] = (df.obs - df.null_mean) / df.null_sd
    # Normal approximation where the null mean is large enough; otherwise a Poisson
    # tail (the true null is under-dispersed relative to Poisson, so this is conservative).
    mu = np.maximum(df.null_mean.to_numpy(), 1e-3)
    p_norm = 2 * norm.sf(np.abs(df.z))
    p_pois = np.minimum(1.0, 2 * np.minimum(poisson.sf(df.obs.to_numpy() - 1, mu),
                                            poisson.cdf(df.obs.to_numpy(), mu)))
    df["p"] = np.where(df.null_mean >= min_expected, p_norm, p_pois)
    df["q"] = bh(df.p.to_numpy())                      # BH over all pairs tested
    return df

BASE_DIR = Path.cwd().resolve().parent.parent
DATA_DIR   = BASE_DIR / "common" / "data_processed"
NODES_FILE = DATA_DIR / "nodes_9.0.csv"
EDGES_FILE = DATA_DIR / "edges_6.0.csv"
OUT_DIR = BASE_DIR / "members" / "sasanka mouli"

min_deg = 30
samples = 500
burn_in = 5
thin = 2
min_expected = 5.0
min_stratum = 30
drop_generic = "Indian"
exclude = ["salt", "water"]
seed = 0
out = OUT_DIR / "cooccurrence_results.csv"

edges, cuisine = load(NODES_FILE, EDGES_FILE)
recipes, ings, rows, strata = build_rows(edges, cuisine, drop_generic or None, min_stratum)
deg = np.bincount(np.concatenate(rows), minlength=len(ings))
keep = [i for i in range(len(ings)) if deg[i] >= min_deg and ings[i] not in set(exclude)]
col_map = -np.ones(len(ings), dtype=int); col_map[keep] = np.arange(len(keep))
names = [ings[i] for i in keep]

pooled = null_distribution(rows, np.zeros(len(rows), dtype=int), col_map, len(keep),
                            samples, burn_in, thin, seed)
strat = null_distribution(rows, strata, col_map, len(keep),
                            samples, burn_in, thin, seed + 1)

P = pair_table(names, *pooled, min_expected).add_suffix("_pool")
S = pair_table(names, *strat, min_expected).add_suffix("_strat")
df = pd.concat([P[["a_pool", "b_pool", "obs_pool", "null_mean_pool", "z_pool", "q_pool", "p_emp_pool"]],
                S[["null_mean_strat", "z_strat", "q_strat", "p_emp_strat"]]], axis=1)
df = df.rename(columns={"a_pool": "a", "b_pool": "b", "obs_pool": "obs"})

sig_p = df.q_pool < 0.05; sig_s = df.q_strat < 0.05
same = np.sign(df.z_pool) == np.sign(df.z_strat)
df["class"] = "ns"
df.loc[sig_p & sig_s & same, "class"] = "universal (both nulls)"
df.loc[sig_p & ~sig_s, "class"] = "regional (pooled only)"
df.loc[~sig_p & sig_s, "class"] = "masked (stratified only)"
df.loc[sig_p & sig_s & ~same, "class"] = "sign flip"
df = df.sort_values("z_pool", key=np.abs, ascending=False)
df.to_csv(out, index=False)
print(df["class"].value_counts().to_string())
print("\nTop over-represented (pooled):")
print(df[df.q_pool < 0.05].sort_values("z_pool", ascending=False).head(10)[
    ["a", "b", "obs", "null_mean_pool", "z_pool", "z_strat", "class"]].to_string(index=False))
print("\nTop avoided (pooled):")
print(df[df.q_pool < 0.05].sort_values("z_pool").head(10)[
    ["a", "b", "obs", "null_mean_pool", "z_pool", "z_strat", "class"]].to_string(index=False))


