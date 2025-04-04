import pandas as pd, sys

# Load CSV files
# disease_name = 'pachydermoperiostosis'
disease_name = sys.argv[1]

publication_info_file_path = '../data/' + disease_name + '/publication_info_' + disease_name + '.csv'
tagged_triple_file_path = '../data/' + disease_name + '/tagged_triples_from_triple_and_relevant_sentence_with_' + disease_name + '.csv' 


pub_info_df = pd.read_csv(publication_info_file_path)
tagged_triple_df = pd.read_csv(tagged_triple_file_path)


# Convert a specific column to a list
article_name_list = tagged_triple_df["MetaData"].tolist()

csv_filename_list_pub_info = [filename + ".csv" for filename in pub_info_df["CSV Filename"].tolist()]
Formatted_String_list_pub_info = pub_info_df["full_metadata"].tolist()


not_found_list = []
count = 0
for index in range(len(article_name_list)):
    found_match = False
    for kindex in range(len(csv_filename_list_pub_info)):
        if article_name_list[index][:20] == csv_filename_list_pub_info[kindex][:20]:
            found_match = True
            article_name_list[index] = Formatted_String_list_pub_info[kindex]
        

    if not found_match:
        count += 1
        not_found_list.append(article_name_list[index])
        print(f"No match found for article name: {article_name_list[index]}")

print(set(not_found_list))
print(f"Total unmatched article names: {count}")

# for i in range(len(article_name_list_nodes)):
#     if article_name_list_nodes[i] == "GNE myopathy from clinics.csv":
#         article_name_list_nodes[i] = "GNE myopathy: from clinics and genetics to pathology and research strategies, Orphanet Journal of Rare Diseases (https://doi.org/10.1186/s13023-018-0802-x)"

#     if article_name_list_nodes[i] == "myopathy- a personal trip from bedside observation to therapeutic trials.csv":
#         article_name_list_nodes[i] = "GNE myopathy: a personal trip from bedside observation to therapeutic trials, Acta myologica : myopathies and cardiomyopathies : official journal of the Mediterranean Society of Myology (https://pubmed.ncbi.nlm.nih.gov/25709382/)"




# Create a new DataFrame with updated article names
tagged_triple_df["MetaData"] = article_name_list

output_file_path = '../data/' + disease_name + '/updated_metadata_tagged_triple_' + disease_name + '.csv'
# Save the updated DataFrame to a new CSV file
tagged_triple_df.to_csv(output_file_path, index=False)
