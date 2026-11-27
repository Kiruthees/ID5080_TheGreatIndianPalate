# MANIFEST

Every file, one line each: what it is and which script made it. Filename patterns such as `{ER,WS}_x.gexf` stand for the several files they expand to. Run order is in `README.md`.

## Top level

| File | What it is | Made by |
|---|---|---|
| `README.md` | How to install and run everything | written by hand |
| `MANIFEST.md` | This file. Also the marker the scripts use to find the project root, so do not rename it | written by hand |
| `requirements.txt` | Python packages | written by hand |
| `report/` | Holds the report PDF | written by hand |

## figure/

| File | What it is | Made by |
|---|---|---|
| `TGIP_1.svg`, `TGIP_2.svg`, `TGIP_3.svg`, `TGIP_4.svg` | Four vector options for the final network figure (2 to 5 MB each) | Gephi, Canva |

## common/data_raw/

| File | What it is | Made by |
|---|---|---|
| `raw_data.xlsx` | Raw recipe dataset, sheet `Cleaned_Indian_Food_Dataset`, exactly as collected | collected externally [CONFIRM: source, access date] |

## common/data_processed/

| File | What it is | Made by |
|---|---|---|
| `ingredient_dish_edges.csv` | One row per recipe-ingredient pair (71,981 rows), from the raw sheet | `common/scripts/cvtr.py` |
| `nodes_intermediate.csv` | Recipe and ingredient nodes after scripted cleaning | `common/scripts/cleaning.ipynb` |
| `edges_intermediate.csv` | Recipe-ingredient edges after scripted cleaning | `common/scripts/cleaning.ipynb` |
| `nodes_9.0.csv` | **Final node table** (Type, Cuisine, ...) used by every analysis | manual cleaning of `nodes_intermediate.csv` by Mizal (no script) |
| `edges_6.0.csv` | **Final edge table** (Source = recipe, Target = ingredient, 47,376 rows, 3,933 recipes) used by every analysis | manual cleaning of `edges_intermediate.csv` by Mizal (no script) |
| `coloured_recipes_ingredients.gexf` | Bipartite graph with ingredient nodes coloured by the average colour of their recipes | `common/scripts/colour_conv.py` |
| `.gitkeep` | Keeps the folder in git | n/a |

## common/scripts/

| File | What it is | Made by |
|---|---|---|
| `cvtr.py` | Converts `raw_data.xlsx` into `ingredient_dish_edges.csv` | written by team |
| `cleaning.ipynb` | Scripted cleaning and name merging, produces the intermediate node and edge files | written by team |
| `colour_conv.py` | Builds the coloured bipartite graph | written by team |
| `.gitkeep` | Keeps the folder in git | n/a |

## members/kiruthees/

All scripts read `nodes_9.0.csv` and/or `edges_6.0.csv`.

| File | What it is | Made by |
|---|---|---|
| `community_detec.py` | Ingredient communities: Jaccard backbone (support >= 15 recipes, Jaccard >= 0.08), Louvain, hub profile bar chart | Kiruthees |
| `masala_ingredient_communities.png` | Community figure | `community_detec.py` |
| `cuisine_specificity.py` | Cuisine specificity (lift = P(i given cuisine) / P(i)) and regional signatures, generic "indian" label excluded | Kiruthees |
| `masala_cuisine_lift_clean.png`, `masala_regional_signatures.png` | Lift heatmap and 2x2 regional signature panels | `cuisine_specificity.py` |
| `degree_dist.py` | Ingredient degree distribution and power-law fits (log-binned regression and Clauset MLE), recipe complexity; imports the local `powerlaw.py`; `SPLIT_FIGS = True` writes two files | Kiruthees |
| `powerlaw.py` | Our own power-law fitting module, imported by `degree_dist.py`. Must stay in this folder, because Python finds it next to the script | Kiruthees  |
| `masala_degrees_powerlaw.png`, `masala_recipe_complexity.png` | Degree and complexity figures | `degree_dist.py` |
| `power_law.py` | Power-law recomputation: raw PDF OLS, CCDF OLS, Clauset MLE | Kiruthees |
| `masala_power_law_validation.png` | Power-law validation figure | `power_law.py` |
| `zipf.py` | Zipf-Mandelbrot fit of ingredient usage by rank | Kiruthees |
| `masala_zipf_mandelbrot.png` | Zipf-Mandelbrot figure | `zipf.py` |
| `last_metrics.py` | Culinary power couples, cuisine effort meter, recipe complexity tiers; also prints summary statistics | Kiruthees |
| `masala_intuitive_metrics.png` | Metrics figure.  | `last_metrics.py`  |
| `.gitkeep` | Keeps the folder in git | n/a |

## members/mizal/

| File | What it is | Made by |
|---|---|---|
| `correlation.ipynb` | Correlation and assortativity analysis | Mizal  |
| `save.png`, `save2.png`, `save3.png` | Plots from the correlation analysis | `correlation.ipynb` |
| `.gitkeep` | Keeps the folder in git | n/a |

## members/nivetha/

| File | What it is | Made by |
|---|---|---|
| `Bipartite_ModelComparisons.ipynb` | Compares the real network with ER, WS, BA, HK and DP random models | Nivetha |
| `all_runs.csv` | Metrics for every model run | `Bipartite_ModelComparisons.ipynb` |
| `metric_means.csv`, `metric_sds.csv`, `metric_summary_mean_pm_sd.csv` | Mean, standard deviation and mean +/- sd of each metric per model | `Bipartite_ModelComparisons.ipynb` |
| `original_network.png`, `butterfly_panels.png`, `clustering.png`, `degree_cdf.png`, `degree_distribution.png`, `shared_neighbours.png` | Comparison figures | `Bipartite_ModelComparisons.ipynb`  |
| `{Original,ER,WS,BA,HK,DP}_butterfly_allnodes.gexf` | Full graph of each model for Gephi (six files, about 8.6 MB each) | `Bipartite_ModelComparisons.ipynb` |
| `{Original,ER,WS,BA,HK,DP}_butterfly_coord3.gexf` | Reduced graph of each model for Gephi (six files) | `Bipartite_ModelComparisons.ipynb` |
| `.gitkeep` | Keeps the folder in git | n/a |

## members/raghav/

| File | What it is | Made by |
|---|---|---|
| `bipartite.py` | Draft bipartite network from `ingredient_dish_edges.csv` | Raghav |
| `dish_ingredient_bipartite.gexf` | The draft bipartite graph (16 MB) | `bipartite.py` |
| `dish_ingredient_sample.png` | Sample plot of the draft graph | `bipartite.py` |
| `percolation.ipynb` | Robustness and percolation analysis | Raghav |
| `recipes_ingredients.gexf` | Bipartite graph from the final tables | `percolation.ipynb` |
| `recipes_one_mode.gexf`, `ingredients_one_mode.gexf` | Recipe and ingredient one-mode projections | `percolation.ipynb` |
| `projection_basic_stats.csv` | Basic statistics of the projections | `percolation.ipynb` |
| `percolation_ingredient.csv` | Percolation curve data | `percolation.ipynb` |
| `cuisine_robustness_results.csv`, `cuisine_ingredient_failure_results.csv` | Robustness results per cuisine | `percolation.ipynb`  |
| `fig8_cuisine_robustness.png`, `ingredient_failure_recipe_availability.png` | Robustness figures | `percolation.ipynb`  |
| `analysis.ipynb` | Node and edge disparity checks and an ingredient-prevalence viewer (asks for an ingredient name) | Raghav  |
| `.gitkeep` | Keeps the folder in git | n/a |

## members/rohieth/

| File | What it is | Made by |
|---|---|---|
| `analysis2.ipynb` | Regional prevalence of ingredient families | Rohieth Raj S |
| `1_Millets.png`, `2_Dals_Lentils_and_Grams.png`, `3_Regional_and_Specialty_Masalas.png`, `4_Leafy_Greens_and_Culinary_Leaves.png`, `5_Whole_and_Ground_Spices.png`, `6_Oils_and_Fats.png`, `7_Rice_Varieties.png` | Regional prevalence heatmaps for each ingredient family | `analysis2.ipynb` |
| `Macro_Regions_15_Staples.png`, `Regional_Cuisines_15_Staples.png` | Regional prevalence heatmaps for 15 staple ingredients across macro-regions and regional cuisines | `analysis2.ipynb` |
| `communities.py` | Louvain communities of ingredients and their prevalence across cuisines | Rohieth Raj S |
| `communities_and_cuisines.png` | Community figure | `communities.py` |
| `.gitkeep` | Keeps the folder in git | n/a |

## members/sasanka mouli/

| File | What it is | Made by |
|---|---|---|
| `cooccurrence_test.py` | Degree-preserving null-model test of ingredient co-occurrence (pooled and cuisine-stratified curveball nulls, BH-FDR) | Sasanka Mouli |
| `cooccurrence_results.csv` | One row per tested ingredient pair (8,911 pairs from 134 ingredients): observed count, null mean, z, q, class | `cooccurrence_test.py` |
| `plot_cooccurrence.py` | Draws the six co-occurrence figures | Sasanka Mouli |
| `figs/ic_pooled_vs_stratified.svg`, `figs/ic_obs_vs_expected.svg`, `figs/ic_top_pairs.svg`, `figs/ic_heatmap.svg`, `figs/ic_strongest_pairings_modularity.svg`, `figs/ic_regional_vs_masked.svg` | The six co-occurrence figures (vector) | `plot_cooccurrence.py` |
| `indiaindia.gephi` | Gephi project file | Sasanka Mouli |
| `.gitkeep` | Keeps the folder in git | n/a |
