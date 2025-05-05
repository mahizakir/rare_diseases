import pandas as pd

# === Step 1: Load input files ===
orpha_file = "ORPHAnomenclature_MasterFile_en_2024..xlsx - ICD10.csv"
nord_file = "synonyms_only_final_output_nord.csv"

# Load ORPHA file
orpha_df = pd.read_csv(orpha_file)

# Load NORD synonyms file
nord_df = pd.read_csv(nord_file)

# === Step 2: Extract (Disease Name, Synonym) pairs ===

# From ORPHA file
orpha_synonym_pairs = []
for idx, row in orpha_df.iterrows():
    disease = str(row['PreferredTerm']).strip().strip('"')
    synonym = str(row['Synonyms']).strip().strip('"')

    if synonym and synonym.lower() != 'nan':
        orpha_synonym_pairs.append((disease, synonym))

# From NORD file
nord_synonym_pairs = []
for idx, row in nord_df.iterrows():
    disease = str(row['Entity 1']).strip().strip('"')
    synonym = str(row['Entity 2']).strip().strip('"')

    if synonym and synonym.lower() != 'nan':
        nord_synonym_pairs.append((disease, synonym))

# === Step 3: Merge both lists ===
combined_pairs = orpha_synonym_pairs + nord_synonym_pairs

# === Step 4: Create DataFrame and remove duplicates ===
final_df = pd.DataFrame(combined_pairs, columns=["Disease Name", "Synonym"])

final_df = final_df.drop_duplicates()

# === Step 5: Save to final CSV ===
final_df.to_csv("final_disease_synonym_mapping.csv", index=False)

print(f"✅ Saved {len(final_df)} clean disease-synonym pairs into final_disease_synonym_mapping.csv")
