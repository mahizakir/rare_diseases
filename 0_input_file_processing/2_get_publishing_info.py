import os
import csv
from habanero import Crossref

# Function to get publication info
def search_article(partial_title):
    cr = Crossref()
    try:
        results = cr.works(query=partial_title)
        if 'message' in results and 'items' in results['message'] and results['message']['items']:
            item = results['message']['items'][0]  # Best match
            title = item.get('title', ["Unknown"])[0]
            journal = item.get('container-title', ["Unknown"])[0]
            doi = item.get('DOI', "No DOI available")
            return title, journal, doi
    except Exception as e:
        print(f"Error retrieving data for '{partial_title}': {e}")
        return "Error", "Error", "Error"
    
    return "Not Found", "Not Found", "Not Found"

# # Function to count occurrences of "GNE" and "Myopathy" in a CSV file
# def count_terms_in_csv(file_path):
#     gne_count = 0
#     myopathy_count = 0
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 for cell in row:
#                     cell_lower = cell.lower()  # Convert to lowercase for case-insensitive search
#                     gne_count += cell_lower.count("gne")
#                     myopathy_count += cell_lower.count("myopathy")
#     except Exception as e:
#         print(f"Error reading file '{file_path}': {e}")
#         return "Error", "Error"

#     return gne_count, myopathy_count

# Folder containing CSV files
disease_name = #"GNE myopathy"#"Bilateral adrenal hemorrhage" #"Nelson syndrome"
#"Acral persistent papular mucinosis" #"Nance-Horan syndrome"#"Adenine phosphoribosyltransferase deficiency"
#"Zimmermann-Laband syndrome" #"Mabry syndrome" #"Endocrine-cerebro-osteodysplasia syndrome"  #"pachydermoperiostosis"
folder_path = f"../data/{disease_name}/{disease_name}_csvs"  # Change this to your actual folder path
output_csv = f"../data/{disease_name}/publication_info_"+ disease_name +".csv"  # Output file

# Check if the folder exists
if not os.path.exists(folder_path):
    print(f"Error: Folder '{folder_path}' not found.")
    exit(1)

try:
    # Get all CSV filenames
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    num_files = len(csv_files)
    print(f"Number of CSV files found: {num_files}")

    # Store results
    results = []

    for i, csv_file in enumerate(csv_files, start=1):
        print(f"Processing file {i}/{num_files}: {csv_file}")
        article_name = os.path.splitext(csv_file)[0]  # Remove .csv extension
        file_path = os.path.join(folder_path, csv_file)

        try:
            # Get publication details
            title, journal, doi = search_article(article_name)
            string = f"{title},{journal} (https://doi.org/{doi})"
            # Count occurrences of "GNE" and "Myopathy"
            # gne_count, myopathy_count = count_terms_in_csv(file_path)
            # results.append([article_name, title, journal, doi, gne_count, myopathy_count])
            results.append([article_name, title, journal, doi, string])
            print(f"Processed: {article_name}")

        except Exception as e:
            print(f"Error processing file '{csv_file}': {e}")
            results.append([article_name, "Error", "Error", "Error"])

    # Save results to a CSV file
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["CSV Filename", "Matched Title", "Journal", "DOI", "full_metadata"])
        writer.writerows(results)

    print(f"Results saved to {output_csv}")

except Exception as e:
    print(f"Error accessing folder '{folder_path}': {e}")
