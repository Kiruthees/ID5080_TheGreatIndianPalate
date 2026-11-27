# Masala-Matrix
## ID5080 Complex Networks course Project
The project consists of a complex network analysis of Indian dishes analyzed as Recipe-Ingredient Bipartite graph.
### Description of the codebase
Analysis : This contains the code files to several metrics computed such as correlation and robustness.
Data_and_Preprocessing : This contains the datasets used processed and some of the code used to process them.
Visualizations : These contain the visual aides and results obtained from analyzing the complex network.


1. Install the dependencies. In your terminal, enter:
```
pip install -r requirements.txt
```

a. (whatever it takes to get nodes_9.0.csv and edges_6.0.csv)
a1. raw_data.xlsx from (TODO)
a2. common/scripts/cvtr.py - to get common/data_raw/ingredient_dish_edges.csv
a3. common/scripts/cleaning.ipynb - to get intermediate nodes and edges csv
a4 - mizal manually cleaned to get nodes_9.0.csv and edges_6.0.csv - use these as final source data
to get initial draft bipartite network
members/raghav/bipartite.py

to get ingredient co-occurrence analysis-
b1. members/sasanka mouli/cooccurrence_test.py
b2. members/sasanka mouli/plot_cooccurrence.py
to get bipartite model comparison
c1. members/nivetha/Bipartite_ModelComparisons.ipynb
for robustness and percolation analysis
d. members/raghav/percolation.ipynb
for correlation and assortativity analysis
e. members/mizal/correlation.ipynb
for colouring ingredient nodes based on average colour of connected recipe nodes
f. common/scripts/colour_conv.py
to get prevalence of an ingredient across cuisines
g. members/raghav/analysis.ipynb
to plot regional prevalence of different ingredient families and to get prevalence of an ingredient across cuisines
h. members/rohieth/analysis2.ipynb
to plot louvain communities and show prevalance of these communities in different cuisines
i. members/rohieth/communities.py

Bipartite_ModelComparisons.ipynb:
7 min
takes - common/data_processed/edges_6.0.csv, common/data_processed/nodes_9.0.csv
gives - ...


cooccurrence_test.py
3 min
takes - common/data_processed/edges_6.0.csv, common/data_processed/nodes_9.0.csv
gives - members/sasanka mouli/cooccurrence_results.csv

plot_cooccurrence_test.py
10 seconds
takes - members/sasanka mouli/cooccurrence_results.csv
gives - members/sasanka mouli/figs/

percolation.ipynb
10 seconds
takes - common/data_processed/edges_6.0.csv, common/data_processed/nodes_9.0.csv
gives - raghav

correlation.ipynb
2.5 min
takes - common/data_processed/edges_6.0.csv
gives - mizal

colour_conv.py
instant
takes - common/data_processed/edges_6.0.csv, common/data_processed/nodes_9.0.csv
gives - common/data_processed/coloured_recipes_ingredients.gexf

cvtr.py
instant
takes - common/data_raw/raw_data.xlsx
gives - common/data_processed/ingredient_dish_edges.csv

cleaning.ipynb
instant
takes - common/data_processed/ingredient_dish_edges.csv
gives - common/data_processed/nodes_intermediate.csv & common/data_processed/edges_intermediate.csv

MIZAL
days
takes - common/data_processed/nodes_intermediate.csv & common/data_processed/edges_intermediate.csv
gives - common/data_processed/nodes_9.0.csv & common/data_processed/edges_6.0.csv

bipartite.py
10 sec
takes - common/data_processed/ingredient_dish_edges.csv
gives - dish_ingredient_bipartite.gexf and dish_ingredient_sample.png

analysis.ipynb
instant
takes - common/data_processed/nodes_9.0.csv & common/data_processed/edges_6.0.csv, user input
gives - ingredient prevalence plot within the notebook

analysis2.ipynb
10 sec
takes - common/data_processed/nodes_9.0.csv & common/data_processed/edges_6.0.csv
gives - heatmaps within members/rohieth

communities.py
30 sec
takes - common/data_processed/nodes_9.0.csv & common/data_processed/edges_6.0.csv
gives - members/rohieth/communities_and_cuisines.png
