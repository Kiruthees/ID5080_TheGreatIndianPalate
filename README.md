# ID5080 Term Project: Indian recipe-ingredient bipartite network

Team: **The Great Indian Palate** | Project number: **4**

We analyse Indian dishes as a recipe-ingredient bipartite network: a recipe node is linked to every ingredient it uses. This folder rebuilds every number and figure in the report. Start here, then see `MANIFEST.md` for every file.

## Folder layout

```
README.md          this file
MANIFEST.md        every file, one line each: what it is, which script made it
requirements.txt   Python packages
report/            report PDF
figure/            final network figure options (TGIP_1..4.svg)
common/
  data_raw/        raw_data.xlsx, exactly as collected, never edited
  data_processed/  what the scripts produce from data_raw (plus the hand-cleaned final tables)
  scripts/         shared pipeline: cvtr.py, cleaning.ipynb, colour_conv.py
members/           one folder per person: their notebooks, scripts and outputs
```

## 1. Install

Tested with Python 3.12.

```
pip install -r requirements.txt
```

This installs Jupyter, which the `.ipynb` notebooks need.

## 2. Running things

Scripts and notebooks find the project root by looking for `MANIFEST.md` in the current folder or any parent, so they can be started from anywhere inside the project. All paths in the code are relative to that root; there are no absolute paths. Do not delete or rename `MANIFEST.md`.

```
python "members/sasanka mouli/cooccurrence_test.py"
jupyter nbconvert --to notebook --execute --inplace members/raghav/percolation.ipynb
```

## 3. Build the data (run in this order)

| Step | Script | Reads | Writes | Time |
|---|---|---|---|---|
| 1 | `common/scripts/cvtr.py` | `common/data_raw/raw_data.xlsx` (sheet `Cleaned_Indian_Food_Dataset`) | `common/data_processed/ingredient_dish_edges.csv` | 3 s |
| 2 | `common/scripts/cleaning.ipynb` | `ingredient_dish_edges.csv` | `nodes_intermediate.csv`, `edges_intermediate.csv` | 3 s |
| 3 | **manual cleaning by Mizal** | the two intermediate files | `nodes_9.0.csv`, `edges_6.0.csv` | na |

Steps 1 and 2 were re-run on a fresh checkout and reproduce the committed files exactly (the CSV line endings may differ by operating system).

**Step 3 is not scripted.** `nodes_9.0.csv` and `edges_6.0.csv` are committed as the final source data and every analysis below starts from them. TODO: add the change log or a diff against the intermediate files so this step can be traced.

Raw data source: Indian Food Recipes Dataset (Cleaned Version) from Kaggle - https://www.kaggle.com/datasets/sooryaprakash12/cleaned-indian-recipes-dataset

## 4. Run the analyses

All of these read `nodes_9.0.csv` and `edges_6.0.csv` from `common/data_processed/` unless stated.

| Analysis | Script | Output | Time |
|---|---|---|---|
| Initial bipartite network and sample plot | `members/raghav/bipartite.py` (reads `ingredient_dish_edges.csv`) | `dish_ingredient_bipartite.gexf`, `dish_ingredient_sample.png` | 6 s |
| Ingredient co-occurrence null-model test | `members/sasanka mouli/cooccurrence_test.py` | `cooccurrence_results.csv` | about 90 s |
| Co-occurrence figures | `members/sasanka mouli/plot_cooccurrence.py` (run after the test) | `figs/ic_*.svg` (six figures) | 3 s |
| Bipartite model comparison (ER, WS, BA, HK, DP) | `members/nivetha/Bipartite_ModelComparisons.ipynb` | metric CSVs, PNGs and `*_butterfly_*.gexf` in the same folder | about 7 min  |
| Robustness and percolation | `members/raghav/percolation.ipynb` | one-mode projections, percolation CSVs, `.gexf` files | about 10 s |
| Correlation and assortativity | `members/mizal/correlation.ipynb` (reads `edges_6.0.csv`) | `save.png`, `save2.png`, `save3.png` | about 2.5 min  |
| Colouring ingredient nodes by average recipe colour | `common/scripts/colour_conv.py` | `common/data_processed/coloured_recipes_ingredients.gexf` | 1 s |
| Ingredient prevalence across cuisines | `members/raghav/analysis.ipynb` | plot inside the notebook. **Asks for an ingredient name at run time (`input()`), so it cannot run unattended.** | instant |
| Ingredient-family prevalence by region | `members/rohieth/analysis2.ipynb` | five family PNGs in `members/rohieth/` | 11 s |
| Louvain communities and their cuisine prevalence | `members/rohieth/communities.py` | `communities_and_cuisines.png` | 12 s |
| Ingredient communities (Jaccard backbone, Louvain) | `members/kiruthees/community_detec.py` | `masala_ingredient_communities.png` | 1 s |
| Cuisine specificity (lift) and regional signatures | `members/kiruthees/cuisine_specificity.py` | `masala_cuisine_lift_clean.png`, `masala_regional_signatures.png` | 3 s |
| Degree distributions and power-law fits | `members/kiruthees/degree_dist.py` (imports the local `members/kiruthees/powerlaw.py`; `SPLIT_FIGS = True`) | `masala_degrees_powerlaw.png`, `masala_recipe_complexity.png` | 2 s |
| Power-law validation (PDF, CCDF, Clauset MLE) | `members/kiruthees/power_law.py` | `masala_power_law_validation.png` | 1 s |
| Zipf-Mandelbrot fit of ingredient usage | `members/kiruthees/zipf.py` | `masala_zipf_mandelbrot.png` | 2 s |
| Power couples, effort meter, recipe complexity tiers | `members/kiruthees/last_metrics.py` | `masala_intuitive_metrics.png` | 1 s |

Times for the scripts above were measured on one machine.

## 5. Reproducibility

- Random seeds are fixed wherever randomness is used (co-occurrence test: 0 pooled, 1 stratified; the other analyses use 42 or 3). Re-running the co-occurrence test reproduces `cooccurrence_results.csv` exactly.
- The `.gexf` files are large (up to 16 MB). They are outputs and can be regenerated by the scripts above.

## 6. Known issues

- Step 3 above (manual cleaning) cannot be re-run.
- `analysis.ipynb` needs interactive input.
