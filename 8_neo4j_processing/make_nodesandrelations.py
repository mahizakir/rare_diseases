import os
import pandas as pd

# === CONFIGURATION === 
disease_name = "Zimmermann-Laband syndrome" #"Nelson syndrome" #"GNE myopathy"
#"Endocrine-cerebro-osteodysplasia syndrome" #"Bilateral adrenal hemorrhage" #"Adenine phosphoribosyltransferase deficiency" #"pachydermoperiostosis" 
#"Nelson syndrome"  #"Nance-Horan syndrome" #"Mabry syndrome" 


input_csv = "files_not_added_in_db/final_" + disease_name + ".csv"  # ← Change to the path of the new CSV


nodes_path = "final_nodes.csv"
relations_path = "final_relations.csv"
registry_path = "global_node_registry.csv"

# === LOAD OR CREATE GLOBAL NODE REGISTRY ===
if os.path.exists(registry_path):
    registry = pd.read_csv(registry_path)
    node_index = {(row['name'], row['label'], row['article_name']): row['id'] for _, row in registry.iterrows()}
    next_node_id = registry['id'].max() + 1
else:
    registry = pd.DataFrame(columns=['id', 'name', 'label', 'article_name', 'disease_name'])
    node_index = {}
    next_node_id = 1

# === LOAD AND CLEAN NEW DATA ===
df = pd.read_csv(input_csv)

df = df[df['Relationship'].notna() & df['Entity 1'].notna() & df['Entity 2'].notna()]
df = df[(df['Relationship'] != '') & (df['Entity 1'] != '') & (df['Entity 2'] != '')]

df['Entity 1'] = df['Entity 1'].str.strip().str.lower()
df['Entity 2'] = df['Entity 2'].str.strip().str.lower()

# === CREATE NEW NODES IF NOT IN REGISTRY ===
node_df = pd.concat([
    df[['Entity 1', 'Tag 1', 'MetaData']].rename(columns={'Entity 1': 'name', 'Tag 1': 'label', 'MetaData': 'article_name'}),
    df[['Entity 2', 'Tag 2', 'MetaData']].rename(columns={'Entity 2': 'name', 'Tag 2': 'label', 'MetaData': 'article_name'})
])
node_df = node_df.drop_duplicates().reset_index(drop=True)

new_nodes = []
for _, row in node_df.iterrows():
    key = (row['name'], row['label'], row['article_name'])
    if key not in node_index:
        node_index[key] = next_node_id
        new_nodes.append({
            'id': next_node_id,
            'name': row['name'],
            'label': row['label'],
            'article_name': row['article_name'],
            'disease_name': disease_name
        })
        next_node_id += 1

# Update registry
if new_nodes:
    new_nodes_df = pd.DataFrame(new_nodes)
    registry = pd.concat([registry, new_nodes_df], ignore_index=True)
    registry.to_csv(registry_path, index=False)

# === CREATE RELATIONSHIPS ===
relations = pd.DataFrame({
    'start_id': df.apply(lambda x: node_index.get((x['Entity 1'], x['Tag 1'], x['MetaData'])), axis=1),
    'end_id': df.apply(lambda x: node_index.get((x['Entity 2'], x['Tag 2'], x['MetaData'])), axis=1),
    'label': df['Relationship Tag'],
    'name': df['Relationship'].fillna('UNKNOWN'),
    'article_name': df['MetaData'],
    'relevant_text': df['Relevant Text'],
    'simple_sentences': df['Simple Sentences'],
    'disease_name': disease_name
})
relations = relations.dropna(subset=['start_id', 'end_id']).reset_index(drop=True)

# === SAVE TO NODES AND RELATIONS CSV ===
# Only add new nodes to final_nodes.csv
if new_nodes:
    new_nodes_df.to_csv(nodes_path, mode='a', index=False, header=not os.path.exists(nodes_path))

# Always append new relationships
# relations.to_csv(relations_path, mode='a', index=False, header=not os.path.exists(relations_path))
# === Deduplicate relationships before appending ===
if os.path.exists(relations_path):
    existing_rel = pd.read_csv(relations_path)

    # Combine and drop duplicates based on key columns
    relations = pd.concat([existing_rel, relations], ignore_index=True)
    relations = relations.drop_duplicates(
        subset=['start_id', 'end_id', 'label', 'name', 'article_name'],  # you can tweak these
        keep='first'
    )

# Save updated relationships
relations.to_csv(relations_path, index=False)

# === DONE ===
print(f"✅ Processed CSV: {input_csv}")
print(f"🧠 New nodes added: {len(new_nodes)}")
print(f"🔗 New relationships added: {len(relations)}")
print(f"🗂️ Registry now tracks {len(registry)} total nodes.")
