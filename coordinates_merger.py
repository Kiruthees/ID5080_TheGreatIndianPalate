import pandas as pd

df_main = pd.read_csv('cleaned_nodes_2.csv')
df_coords = pd.read_csv('Coordinates.csv')

df_merged = pd.merge(df_main,df_coords, on='Cuisine', how='left')

df_merged.to_csv('cleaned_nodes_coloured_and_located.csv', index=False)
