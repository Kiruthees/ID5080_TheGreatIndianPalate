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


