import pandas as pd

# PART ONE: Removing Incorrect Nodes
"""
nodes_df = pd.read_csv('nodes_9.0.csv')
edges_df = pd.read_csv('edges_6.0.csv')

correct_nodes = set(edges_df['Source']).union(set(edges_df['Target']))
cleaned_nodes = nodes_df[nodes_df['Id'].isin(correct_nodes)]

cleaned_nodes.to_csv('nodes_9.0.csv', index=False)
 """

# PART TWO: Adding Missing nodes


nodes_df = pd.read_csv('nodes_9.0.csv')
edges_df = pd.read_csv('edges_6.0.csv')

all_nodes = pd.concat([edges_df['Source'], edges_df['Target']]).unique()
existing_nodes = nodes_df['Id'].unique()

missing_nodes = [node for node in all_nodes if node not in existing_nodes]

if len(missing_nodes) > 0:

    print('Missing nodes: ',sorted(missing_nodes))
    print(f"Adding {len(missing_nodes)} to the nodes file...")

    missing_df = pd.DataFrame({
        'Id': missing_nodes,
        'Label': missing_nodes,
        'Cuisine': None,
        'Type': 'Ingredient',
        'Color': '#CCCCCC',
        'Latitude': None,
        'Longitude': None
    })

    complete_nodes = pd.concat([nodes_df, missing_df], ignore_index=True)
    complete_nodes.to_csv('nodes_9.0.csv', index=False)

    print('Done')


# PART THREE: Removing Specific Nodes
"""
nodes_df = pd.read_csv('nodes_8.0.csv')
edges_df = pd.read_csv('edges_5.0.csv')

filtered_nodes = nodes_df[nodes_df['Cuisine'].isin(['Indian', 'North Indian Recipes', 'South Indian Recipes '])]
remaining_edges = edges_df[~edges_df['Source'].isin(filtered_nodes['Id'])]

remaining_edges.to_csv('edges_5.2_(without_i_ni_si).csv')
 """

# PART FOUR: Troubleshoot
"""
nodes_df = pd.read_csv('nodes_8.0.csv')
edges_df = pd.read_csv('edges_6.0.csv')

correct_nodes = set(edges_df['Source']).union(set(edges_df['Target']))
cleaned_nodes = nodes_df[nodes_df['Id'].isin(correct_nodes)]
all_nodes = pd.concat([edges_df['Source'], edges_df['Target']]).unique()
existing_nodes = nodes_df['Id'].unique()
missing_nodes = [node for node in all_nodes if node not in existing_nodes]

print(sorted(missing_nodes))
 """
