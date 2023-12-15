import os
import pandas as pd

# Path to the main folder
main_folder_path = '../155'
num_items = len(os.listdir(main_folder_path))

# Initialize empty DataFrames for nodes and links
merged_nodes = pd.DataFrame()
merged_links = pd.DataFrame()

# Iterate through each subfolder and merge the CSV files
for i in range(num_items):
    subfolder_path = os.path.join(main_folder_path, str(i))

    # Paths to the node.csv and link.csv in the current subfolder
    node_csv_path = os.path.join(subfolder_path, 'node.csv')
    link_csv_path = os.path.join(subfolder_path, 'link.csv')

    # Check if both files exist, then append their contents
    if os.path.exists(node_csv_path) and os.path.exists(link_csv_path):
        # Read and append node.csv
        node_data = pd.read_csv(node_csv_path)
        node_data['index'] = i
        merged_nodes = pd.concat([merged_nodes, node_data], ignore_index=True)

        # Read and append link.csv
        link_data = pd.read_csv(link_csv_path)
        link_data['index'] = i
        merged_links = pd.concat([merged_links, link_data], ignore_index=True)

# Save the merged data to CSV files
merged_nodes.to_csv('../merge_node.csv', index=False)
merged_links.to_csv('../merge_link.csv', index=False)
