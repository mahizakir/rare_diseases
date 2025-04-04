import pandas as pd
import csv
import warnings, sys
# Suppress specific FutureWarning from transformers
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.tokenization_utils_base")

# disease_name = 'pachydermoperiostosis'
disease_name = sys.argv[1]
file_path = '../data/' + disease_name + '/generated_triples_from_simple_sentences_' + disease_name + '.csv' 
# file_path = 'generated_triples_from_simple_sentences.csv'  # Replace with your CSV file path
df = pd.read_csv(file_path, usecols=[0, 1, 2, 3], header=0) # Read the CSV file, skipping the header
list_of_unformatted_relevant_sentences = df.iloc[:, 0].tolist() # Convert the first column values to a list, skipping the header
list_of_unformatted_simple_sentences =  df.iloc[:, 1].tolist()
list_of_unformatted_triples = df.iloc[:, 2].tolist()
list_of_unformatted_meta_data =  df.iloc[:, 3].tolist()

list_of_formatted_relevant_sentences = []
list_of_formatted_simple_sentences = []
list_of_formatted_triples = []
list_of_formatted_meta_data = []

for i in range(0,len(list_of_unformatted_triples)):
    lines = list_of_unformatted_triples[i].splitlines()
    cleaned_triples = []
    for line in lines:
        sentence = line.strip() # Remove leading and trailing whitespace
        if sentence.startswith('(') and sentence.endswith(')'): # Strip parentheses if they are present at the beginning and end
            sentence = sentence[1:-1].strip()
        if sentence.startswith('"') and sentence.endswith('"'): # Strip quotes if they are present at the beginning and end
            sentence = sentence[1:-1].strip()
        if sentence:  # Only add non-empty sentences
            cleaned_triples.append(sentence)
    if len(cleaned_triples) > 0:
        clean_length = len(cleaned_triples)
        list_of_formatted_relevant_sentences.extend([list_of_unformatted_relevant_sentences[i]] * clean_length)       
        list_of_formatted_simple_sentences.extend([list_of_unformatted_simple_sentences[i]] * clean_length)
        list_of_formatted_triples.extend(cleaned_triples)
        list_of_formatted_meta_data.extend([list_of_unformatted_meta_data[i]] * clean_length)

print("Number of triples in the whole dataset that was generate by llm from simple sentences:")
print(len(list_of_formatted_relevant_sentences), len(list_of_formatted_simple_sentences), len(list_of_formatted_triples), len(list_of_formatted_meta_data))

list_of_entity_1 = []
list_of_entity_2 = []
list_of_relations = []

for triple in list_of_formatted_triples:
    parts = [part.strip() for part in triple.split(",")]
    if len(parts)==3:
        list_of_entity_1.append(parts[0])
        list_of_entity_2.append(parts[2])
        list_of_relations.append(parts[1])
    else:
        list_of_entity_1.append("NULL")
        list_of_entity_2.append("NULL")
        list_of_relations.append("NULL")

print(len(list_of_entity_1), len(list_of_entity_2), len(list_of_relations))







# def find_unique_sentences(list_of_sentences_here):
#     # Get sentence embeddings
#     embeddings_to_find_unique_sentences = model_to_find_unique_sentences.encode(list_of_sentences_here, convert_to_tensor=True)
#     unique_sentences = []
#     cosine_scores = util.pytorch_cos_sim(embeddings_to_find_unique_sentences, embeddings_to_find_unique_sentences)
#     added = set()
#     threshold = 0.95  # Similarity threshold

#     for i in range(len(list_of_sentences_here)):
#         if i in added:
#             continue
#         unique_sentences.append(list_of_sentences_here[i])
#         for j in range(i + 1, len(list_of_sentences_here)):
#             if cosine_scores[i][j] > threshold:
#                 added.add(j)
#     return unique_sentences

# from collections import defaultdict
# # Remove the redundant simple sentences with the same meaning generated from the relevant text
# from sentence_transformers import SentenceTransformer, util
# # Load a sentence-transformer model optimized for paraphrase detection
# model_to_find_unique_sentences = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# # Step 1: Group indices by duplicate values in `list_of_formatted_meta_data`
# duplicate_indices = defaultdict(list)
# for i, meta in enumerate(list_of_formatted_meta_data):
#     duplicate_indices[meta].append(i)

# # Step 2: Filter unique triples for each duplicate group
# indices_to_keep = set()
# for meta, indices in duplicate_indices.items():
#     if len(indices) > 1:
#         # Get the triples with the same metadata
#         triples_for_meta = [list_of_formatted_triples[i] for i in indices]
        
#         # Find unique triples based on your function
#         unique_triples = find_unique_sentences(triples_for_meta)
        
#         # Keep only indices of unique triples
#         unique_indices = [indices[i] for i, triple in enumerate(triples_for_meta) if triple in unique_triples]
#         indices_to_keep.update(unique_indices)
#     else:
#         indices_to_keep.add(indices[0])

# # Step 3: Retain only unique indices across all lists
# indices_to_keep = sorted(indices_to_keep)
# list_of_formatted_meta_data = [list_of_formatted_meta_data[i] for i in indices_to_keep]
# list_of_formatted_triples = [list_of_formatted_triples[i] for i in indices_to_keep]
# list_of_formatted_relevant_sentences = [list_of_formatted_relevant_sentences[i] for i in indices_to_keep]
# list_of_formatted_simple_sentences = [list_of_formatted_simple_sentences[i] for i in indices_to_keep]
# list_of_entity_1 = [list_of_entity_1[i] for i in indices_to_keep]
# list_of_relations = [list_of_relations[i] for i in indices_to_keep]
# list_of_entity_2 = [list_of_entity_2[i] for i in indices_to_keep]

# Now, all lists are updated and aligned with unique values.
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util

# Load a sentence-transformer model optimized for paraphrase detection
model_to_find_unique_sentences = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# def find_unique_sentences(list_of_sentences_here):
#     # Get sentence embeddings
#     embeddings_to_find_unique_sentences = model_to_find_unique_sentences.encode(list_of_sentences_here, convert_to_tensor=True)
#     unique_sentences = []
#     cosine_scores = util.pytorch_cos_sim(embeddings_to_find_unique_sentences, embeddings_to_find_unique_sentences)
#     added = set()
#     threshold = 0.85  # Similarity threshold

#     for i in range(len(list_of_sentences_here)):
#         if i in added:
#             continue
#         unique_sentences.append(list_of_sentences_here[i])
#         for j in range(i + 1, len(list_of_sentences_here)):
#             if cosine_scores[i][j] > threshold:
#                 added.add(j)
#     return unique_sentences

# # Step 1: Group indices by duplicate values in `list_of_formatted_meta_data`
# duplicate_indices = defaultdict(list)
# for i, meta in enumerate(list_of_formatted_meta_data):
#     duplicate_indices[meta].append(i)

# # Step 2: Filter unique triples for each duplicate group
# indices_to_keep = set()
# triple_counts = {}  # Dictionary to store the original and unique counts for each metadata

# for meta, indices in duplicate_indices.items():
#     original_count = len(indices)  # Count of triples with the same metadata
#     if original_count > 1:
#         # Get the triples with the same metadata
#         triples_for_meta = [list_of_formatted_triples[i] for i in indices]
        
#         # Find unique triples based on the function
#         unique_triples = find_unique_sentences(triples_for_meta)
#         print(unique_triples)
#         unique_count = len(unique_triples)  # Count of unique triples found
        
#         # Store the counts for this metadata
#         triple_counts[meta] = {'original': original_count, 'unique': unique_count}
        
#         # Keep only indices of unique triples
#         unique_indices = [indices[i] for i, triple in enumerate(triples_for_meta) if triple in unique_triples]
#         indices_to_keep.update(unique_indices)
#     else:
#         # For non-duplicates, store the count as 1 for both original and unique
#         triple_counts[meta] = {'original': 1, 'unique': 1}
#         indices_to_keep.add(indices[0])

# # Step 3: Retain only unique indices across all lists
# indices_to_keep = sorted(indices_to_keep)
# list_of_formatted_meta_data = [list_of_formatted_meta_data[i] for i in indices_to_keep]
# list_of_formatted_triples = [list_of_formatted_triples[i] for i in indices_to_keep]
# list_of_formatted_relevant_sentences = [list_of_formatted_relevant_sentences[i] for i in indices_to_keep]
# list_of_formatted_simple_sentences = [list_of_formatted_simple_sentences[i] for i in indices_to_keep]
# list_of_entity_1 = [list_of_entity_1[i] for i in indices_to_keep]
# list_of_relations = [list_of_relations[i] for i in indices_to_keep]
# list_of_entity_2 = [list_of_entity_2[i] for i in indices_to_keep]






from collections import defaultdict

def find_unique_triples_with_context(list_of_triples, threshold=0.85):
    # Get embeddings for the triples
    embeddings = model_to_find_unique_sentences.encode(list_of_triples, convert_to_tensor=True)
    unique_triples = []
    unique_indices = []
    added = set()
    cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)
    
    for i in range(len(list_of_triples)):
        if i in added:
            continue
        unique_triples.append(list_of_triples[i])
        unique_indices.append(i)
        for j in range(i + 1, len(list_of_triples)):
            if cosine_scores[i][j] > threshold:
                added.add(j)
    return unique_triples, unique_indices

# Step 1: Identify duplicate indices based on metadata
duplicate_indices = defaultdict(list)
for i, meta in enumerate(list_of_formatted_meta_data):
    duplicate_indices[meta].append(i)

# Step 2: Process each metadata group for unique triples
indices_to_keep = set()
triple_counts = {}

for meta, indices in duplicate_indices.items():
    triples_for_meta = [list_of_formatted_triples[i] for i in indices]
    unique_triples, unique_indices = find_unique_triples_with_context(triples_for_meta)
    
    # Track original and unique counts
    triple_counts[meta] = {'original': len(indices), 'unique': len(unique_triples)}
    
    # Map back to original indices
    for idx in unique_indices:
        indices_to_keep.add(indices[idx])

# Step 3: Filter lists based on unique indices
indices_to_keep = sorted(indices_to_keep)
list_of_formatted_meta_data = [list_of_formatted_meta_data[i] for i in indices_to_keep]
list_of_formatted_triples = [list_of_formatted_triples[i] for i in indices_to_keep]
list_of_formatted_relevant_sentences = [list_of_formatted_relevant_sentences[i] for i in indices_to_keep]
list_of_formatted_simple_sentences = [list_of_formatted_simple_sentences[i] for i in indices_to_keep]
list_of_entity_1 = [list_of_entity_1[i] for i in indices_to_keep]
list_of_relations = [list_of_relations[i] for i in indices_to_keep]
list_of_entity_2 = [list_of_entity_2[i] for i in indices_to_keep]











# Now, triple_counts contains the original and unique counts for each metadata
# Print the original and unique counts for each metadata entry in a readable format
print("Metadata Triple Counts:")
for meta, counts in triple_counts.items():
    print(f"Metadata: {meta}")
    print(f"  Original Triple Count: {counts['original']}")
    print(f"  Unique Triple Count: {counts['unique']}")
    print("-" * 40)
print("Number of triples in the whole dataset where the triples are unique per paper:")
print(len(list_of_formatted_relevant_sentences), len(list_of_formatted_simple_sentences), len(list_of_formatted_triples), len(list_of_formatted_meta_data))
print(len(list_of_entity_1), len(list_of_entity_2), len(list_of_relations))






output_file = '../data/' + disease_name + '/formatted_triples_' + disease_name + '.csv' 

if (len(list_of_entity_1) == len(list_of_entity_2) == len(list_of_relations) == len(list_of_formatted_relevant_sentences) == len(list_of_formatted_simple_sentences) == len(list_of_formatted_triples) == len(list_of_formatted_meta_data)):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Relevant Text', 'Simple Sentences', 'Triple', 'Entity 1', 'Relationship', 'Entity 2', 'MetaData'])
        for item1, item2, item3, item4, item5, item6, item7 in zip(list_of_formatted_relevant_sentences, list_of_formatted_simple_sentences, list_of_formatted_triples, list_of_entity_1, list_of_relations, list_of_entity_2, list_of_formatted_meta_data):
            writer.writerow([item1, item2, item3, item4, item5, item6, item7])