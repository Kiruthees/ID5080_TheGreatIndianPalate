import pandas as pd
import networkx as nx
import numpy as np
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

regional_map = pd.merge(edges, nodes[['Id', 'Cuisine']], left_on='Source', right_on='Id', how='inner')
regional_map = regional_map.rename(columns={"Target": "Ingredient"})

merged_map = regional_map.copy()
mergers = {
    'Awadhi': 'Uttar Pradesh',
    'Lucknowi': 'Uttar Pradesh',
    'Chettinad': 'Tamil Nadu',
    'Coorg': 'Karnataka',
    'Kongunadu': 'Tamil Nadu',
    'Konkan': 'Maharashtrian Recipes',
    'Malabar': 'Kerala Recipes',
    'Malvani': 'Maharashtrian Recipes',
    'Mangalorean': 'Karnataka',
    'North Karnataka': 'Karnataka',
    'South Karnataka': 'Karnataka',
    'Udupi': 'Karnataka',
    'Sindhi': 'Gujarati Recipes',
        }

merged_map['Cuisine'] = merged_map['Cuisine'].replace(mergers)

M = nx.Graph()
new_cuisines = set(regional_map['Cuisine'])
n_ingreds = set(regional_map['Ingredient'])

M.add_nodes_from(new_cuisines, bipartite=0)
M.add_nodes_from(n_ingreds, bipartite=1)

new_cic = (merged_map.groupby(["Cuisine", "Ingredient"]).size().reset_index(name="weight"))
for _, row in new_cic.iterrows():
    M.add_edge(row["Cuisine"], row["Ingredient"], weight=row["weight"])

n_cuisines = merged_map['Cuisine'].nunique()
n_cpi_counts = new_cic.groupby('Ingredient')['Cuisine'].nunique() # cuisines per ingredient
n_cpi_fraction = n_cpi_counts / n_cuisines

t = 0.16
new_ci = n_cpi_fraction[n_cpi_fraction >= t].index.tolist()

new_cie = [(u,v)
    for u,v in M.edges()
    if v in new_ci]

M.remove_edges_from(new_cie)
merged_proj = bipartite.weighted_projected_graph(M, new_cuisines)
mergedmap_df = pd.DataFrame([(u,v,w.get('weight',1)) for u,v,w in merged_proj.edges(data=True)])

mergedmap_df.to_csv(DATA_DIR / 'edges_6.5_merger_map.csv', index=False, header=['Source', 'Target', 'Weight'])
