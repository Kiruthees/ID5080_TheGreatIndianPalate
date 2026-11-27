import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite
from pathlib import Path

def find_root():
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "MANIFEST.md").exists():
            return d
    raise FileNotFoundError("Run this from inside the project folder")

BASE_DIR = find_root()
DATA_DIR = BASE_DIR / "common" / "data_processed"

nodes = pd.read_csv(DATA_DIR / 'nodes_9.0.csv')
edges = pd.read_csv(DATA_DIR / 'edges_6.0.csv')

regional_map = pd.merge(
    edges, nodes[['Id', 'Cuisine']], left_on='Source', right_on='Id', how='inner'
)
regional_map = regional_map.rename(columns={"Target": "Ingredient"})

# ---------- Build the cuisine-ingredient bipartite graph ----------
B = nx.Graph()
cuisines = set(regional_map['Cuisine'])
ingreds = set(regional_map['Ingredient'])

B.add_nodes_from(cuisines, bipartite=0)
B.add_nodes_from(ingreds, bipartite=1)

cuisine_ingred_counts = (
    regional_map.groupby(["Cuisine", "Ingredient"]).size().reset_index(name="weight")
)
for _, row in cuisine_ingred_counts.iterrows():
    B.add_edge(row["Cuisine"], row["Ingredient"], weight=row["weight"])

no_cuisines = regional_map['Cuisine'].nunique()
cpi_counts = cuisine_ingred_counts.groupby('Ingredient')['Cuisine'].nunique()  # cuisines per ingredient
cpi_fraction = cpi_counts / no_cuisines

step = 0.02
t_values = np.round(np.arange(step, 1.0 + step / 2, step), 2)   # 0.02, 0.04, ..., 1.00
densities = []

for tv in t_values:
    common = cpi_fraction[cpi_fraction >= tv].index
    B_t = B.copy()
    B_t.remove_nodes_from(common)                                # drop the common ingredients
    if not any(B_t.nodes[n]['bipartite'] == 1 for n in B_t):   # all ingredients removed
        densities.append(0.0); continue
    proj = bipartite.weighted_projected_graph(B_t, cuisines)
    densities.append(nx.density(proj))

# Plotting
x = np.array(t_values)
y = np.array(densities)

slopes = np.gradient(y, x)
idx_crit = np.argmax(np.abs(slopes))
t_crit = x[idx_crit]
dens_crit = y[idx_crit]

step_size = x[1] - x[0]
margin = step_size / 2

plt.figure()
plt.plot(t_values, densities, color='purple')
plt.plot(t_crit, dens_crit, 'bo', markersize=8, label=f'Critical Point (t={t_crit:.2f})')
plt.fill_betweenx(y, x - margin, x + margin, color='purple', alpha=0.3, label='Resolution Margin')
plt.axvspan(0.16, 0.18, color='teal', alpha=0.1, label='Critical Region')
plt.annotate(f'Optimal Threshold: {t_crit:.2f}',
             xy=(t_crit, dens_crit),
             xytext=(t_crit + 0.1, dens_crit + 0.05),
             arrowprops=dict(arrowstyle='->', color='black'))
plt.xlabel('Threshold value for deletion of common ingredients')
plt.ylabel('Density of Regional Projection Graph')
plt.title('Regional Differences')
plt.legend()
plt.show()
