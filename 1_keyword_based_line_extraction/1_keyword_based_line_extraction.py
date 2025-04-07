import pandas as pd
import os, re, sys
from get_keywords import find_keywords

no_of_csv_in_folder = 0

## Below deals with empty csvs and prints the file names with issues.
def read_csv_files_from_folder(folder_path):
    contents_list = []
    global no_of_csv_in_folder
    
    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            no_of_csv_in_folder += 1
            try:
                # Check if the file is empty
                if os.path.getsize(file_path) == 0:
                    print(f"Skipping empty file: {filename}")
                    continue
                # Read only the first column
                df = pd.read_csv(file_path, usecols=[0])
                for content in df.iloc[:, 0]:  # Iterate through each content in the first column
                    # Ensure content is a string and handle NaN
                    if pd.notna(content):  # Skip NaN values
                        contents_list.append((str(content), filename))  # Convert to string and append
            
            except pd.errors.EmptyDataError:
                print(f"Skipping file with no data or columns: {filename}")
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
    
    return contents_list

#disease_name = "pachydermoperiostosis"
disease_name = sys.argv[1]
folder_path = f"../data/{disease_name}/{disease_name}_csvs"
csv_contents_with_file_name = read_csv_files_from_folder(folder_path)

keywords = find_keywords(disease_name)
print(type(keywords))
for i in range(len(keywords)):
    print(keywords[i])


# Function to calculate 90% of the length of a word
# def get_90_percent_match(word):
#     length = len(word)
#     # Calculate the first 90% of the word's length
#     match_length = int(length * 0.9)
#     return re.escape(word[:match_length]).replace(r'\ ', ' ')
# # Build regex pattern dynamically for 90% match of each keyword
# pattern_parts = [get_90_percent_match(keyword) for keyword in keywords]
# print(pattern_parts)


pattern = r"\b(" + "|".join(map(re.escape, keywords)) + r")\b"


matched_items = []

for item in csv_contents_with_file_name:
    first_column = item[0]  # Get the first column
    if re.search(pattern, first_column, re.IGNORECASE):  # Check against the pattern
        matched_items.append((item[0], item[1]))  # Append both columns as a tuple

print("Number of lines in csvs in folder", len(csv_contents_with_file_name))
print("Number of lines in relevant sentences:", len(matched_items))

# Create a DataFrame from matched items
df = pd.DataFrame(matched_items, columns=['Relevant Article Text', 'Article Info'])

# Save to CSV
df.to_csv('../data/' + disease_name + '/relevant_texts_' + disease_name + '.csv', index=False)
