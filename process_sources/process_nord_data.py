import pandas as pd

# Load the CSV file
file_path = "nord_data/nord_rare_disease_database_export.csv"  
df = pd.read_csv(file_path)

# Create separate lists for each column
source_list = df['Source'].tolist()
disease_name_list = df['Disease Name'].tolist()
report_url_list = df['Report URL'].tolist()
description_list = df['Description'].tolist()
synonyms_list = df['Synonyms'].tolist()

# Display the first few elements of each list for verification
print("Source List:", source_list[:5])
print("Synonyms List:", synonyms_list[:5])


# Step 1: Create a final formatted synonyms-only CSV file
relevant_text_list = []
simple_sentences_list = []
triple_list = []
tagged_triple_list = []

entity_1_list = []
tag_1_list = []
relationship_list = []
relationship_tag_list = []
entity_2_list = []
tag_2_list = []

metadata_list = []

# # Loop through each row and extract disease name and synonyms
# for i in range(len(df)):
#     disease = str(df['Disease Name'].iloc[i]).strip()
#     synonyms = df['Synonyms'].iloc[i]

#     if pd.notna(synonyms):
#         for synonym in str(synonyms).split('|'):
#             synonym = synonym.strip()

#             # Populate the lists
#             entity_1_list.append(disease)
#             tag_1_list.append("disease")

#             entity_2_list.append(synonym)
#             tag_2_list.append("disease_synonym")

#             relationship_list.append("ALSO_KNOWN_AS")
#             relationship_tag_list.append("Classification/Type")

#             triple_list.append(f"{disease}, ALSO_KNOWN_AS, {synonym}")
#             tagged_triple_list.append(f"({disease} (disease), ALSO_KNOWN_AS, {synonym} (disease_synonym))")

#             relevant_text_list.append("")  # Empty for now
#             simple_sentences_list.append(f"{disease} is also known as {synonym}.")
#             metadata_list.append(report_url_list[i])

# df = pd.DataFrame({
#     "Relevant Text": relevant_text_list,
#     "Simple Sentences": simple_sentences_list,
#     "Triple": triple_list,
#     "Tagged Triple": tagged_triple_list,
#     "Entity 1": entity_1_list,
#     "Tag 1": tag_1_list,
#     "Relationship": relationship_list,
#     "Relationship Tag": relationship_tag_list,
#     "Entity 2": entity_2_list,
#     "Tag 2": tag_2_list,
#     "MetaData": metadata_list
# })
# output_file_path = "nord_data/synonyms_only_final_output_nord.csv"
# df.to_csv(output_file_path, index=False)


# Step 2: Clean text and make relevant text for nord to pass them to llms
relevant_article_text_list = []
article_info_list = []

from bs4 import BeautifulSoup
import re

for i in range(len(df)):
    disease = str(df['Disease Name'].iloc[i]).strip()
    raw_text = df['Description'].iloc[i]

    if pd.notna(raw_text):
        soup = BeautifulSoup(str(raw_text), "html.parser")
        cleaned_text = soup.get_text(separator=" ", strip=True)
        cleaned_text = re.sub(r"&nbsp;|\xa0", " ", cleaned_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)

        # Append only if raw_text exists
        relevant_article_text_list.append(f"{disease}: {cleaned_text}")
        article_info_list.append(report_url_list[i])


# Optionally add to DataFrame
# Relevant Article Text,Article Info
# Create a new DataFrame
output_df = pd.DataFrame({
    "Relevant Article Text": relevant_article_text_list,
    "Article Info": article_info_list
})
# Step 3: Save to CSV
output_df.to_csv("nord_data/relevant_texts_nord_descriptions.csv", index=False)
