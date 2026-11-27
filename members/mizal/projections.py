import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite


nodes = pd.read_csv('nodes_9.0.csv')
edges = pd.read_csv('edges_6.0.csv')

regional_map = pd.merge(
    edges, nodes[['Id', 'Cuisine']], left_on='Source', right_on='Id', how='inner'
)
regional_map = regional_map.rename(columns={"Target": "Ingredient"})
"""
B = nx.Graph()
cuisines = set(regional_map['Cuisine'])
ingreds = set(regional_map['Ingredient'])

B.add_nodes_from(cuisines, bipartite=0)
B.add_nodes_from(ingreds, bipartite=1)

cuisine_ingred_counts = (regional_map.groupby(["Cuisine", "Ingredient"]).size().reset_index(name="weight"))
for _, row in cuisine_ingred_counts.iterrows():
    B.add_edge(row["Cuisine"], row["Ingredient"], weight=row["weight"])


# Filtering the Common Ingredients

no_cuisines = regional_map['Cuisine'].nunique()
cpi_counts = cuisine_ingred_counts.groupby('Ingredient')['Cuisine'].nunique() # cuisines per ingredient
cpi_fraction = cpi_counts / no_cuisines

t = 0.16
common_ingredients = cpi_fraction[cpi_fraction >= t].index.tolist()
B_ = B.copy()
common_ingred_edges = [(u,v)
    for u,v in B_.edges()
    if v in common_ingredients]

B_.remove_edges_from(common_ingred_edges)
cuis_proj = bipartite.weighted_projected_graph(B_, cuisines)

Bdf = pd.DataFrame([(u,v,w.get('weight',1)) for u,v,w in B.edges(data=True)])
B_df = pd.DataFrame([(u,v,w.get('weight',1)) for u,v,w in B_.edges(data=True)])
map_df = pd.DataFrame([(u,v,w.get('weight',1)) for u,v,w in cuis_proj.edges(data=True)])
#Bdf.to_csv('edges_6.5_region&ingreds.csv', index=False)

#print(B_df)
#print(Bdf)
#print(t_values, densities)
#print(map_df)

#print('Converting')
#map_df.to_csv('edges_6.4_regional_map.csv', index=False)
#print('Done')
 """
# PLOTTING DENSITY VS THRESHOLD
"""
x = np.array(t_values)
y = np.array(densities)

slopes = np.gradient(y,x)
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
 """
# PROJECTION MERGERS:

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

mergedmap_df.to_csv('edges_6.5_merger_map.csv', index=False)
