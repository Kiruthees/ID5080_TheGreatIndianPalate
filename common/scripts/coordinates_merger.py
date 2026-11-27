import pandas as pd
from pathlib import Path

def find_root():
    p = Path.cwd().resolve()
    for d in [p, *p.parents]:
        if (d / "MANIFEST.md").exists():
            return d
    raise FileNotFoundError("Run this from inside the project folder")

BASE_DIR = find_root()
DATA_DIR = BASE_DIR / "common" / "data_processed"

df_main = pd.read_csv(DATA_DIR / "nodes_intermediate_colored.csv")
df_coords = pd.read_csv(DATA_DIR / 'coordinates.csv')

df_merged = pd.merge(df_main,df_coords, on='Cuisine', how='left')

df_merged.to_csv(DATA_DIR / 'nodes_lats_colored.csv', index=False)
