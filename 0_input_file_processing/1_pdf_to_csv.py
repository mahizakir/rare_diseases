# import os
# from pdfminer.high_level import extract_text
# import spacy
# import language_tool_python
# import csv
# import re
# import glob

# # Load the spaCy model
# nlp = spacy.load("en_core_web_sm")
# # Load the LanguageTool grammar checker
# tool = language_tool_python.LanguageTool('en-US')


# def remove_references(text):
#     """Removes the last reference section and citations from the text."""
#     pattern = re.compile(
#         r"""
#         (
#             ([Rr]eference[s]?|[Rr]EFERENCE[S]?|[Bb]ibliography|[Bb]IBLIOGRAPHY|[Ww]orks [Cc]ited|[Ww]ORKS [Cc]ITED|[Ee]ndnotes|[Ee]NDNOTES)\s*\n.*  # Reference section headers
#         )
#         """,
#         re.VERBOSE | re.DOTALL  # Allow comments and matching across multiple lines
#     )
#     text = pattern.sub("", text)    
#     return text

# def remove_numbered_citations(text):
#     """Removes numbered citations from the text."""
#     citation_pattern = re.compile(
#         r"""
#         \[\d+(?:[,–]\s*\d+)*\]  # Numbered citations with optional ranges and spaces
#         """,
#         re.VERBOSE  # Allow comments and better readability
#     )

#     # Remove all matches for numbered citations from the text
#     text = citation_pattern.sub("", text)
#     return text

# def process_text_to_sentences(path_to_pdf):
#     # Extract text from the PDF article
#     text = extract_text(path_to_pdf)
#     text = remove_references(text)
#     text = remove_numbered_citations(text)

#     pattern = r'(\w+)-(\n)?(\w+)'
#     # Replace hyphenated words with a single word (concatenating word parts)
#     text = re.sub(pattern, r'\1\3', text)
#     # Split the text into lines
#     lines = text.split('\n')

#     # Use a list comprehension to filter out empty lines and lines with one character
#     filtered_lines = [line for line in lines if len(line.strip()) > 1]

#     # Rejoin the filtered lines to form the cleaned text
#     cleaned_text = '\n'.join(filtered_lines)
#     # Remove newline characters
#     cleaned_text = cleaned_text.replace("\n", " ")

#     # Process the text with spaCy
#     doc = nlp(cleaned_text)

#     # Extract sentences
#     sentences = [sent.text for sent in doc.sents]
#     print('~'*100)
#     # print(sentences[:50])

#     # Initialize a list to store corrected sentences
#     corrected_sentences = []
#     # Disable spell checking
#     tool.disable_spellchecking()
#     # Correct the grammar in each sentence
#     for sentence in sentences:
#         corrected = tool.correct(sentence)
#         corrected_sentences.append(corrected)

#     print('~'*100)
#     # print(corrected_sentences[:50])
#     return corrected_sentences

# def extract_title_from_path(file_path):
#     try:
#         # Split the path into directory and filename components
#         _, filename = os.path.split(file_path)

#         # Split the filename into base name and extension
#         title, _ = os.path.splitext(filename)

#         return title
#     except Exception as e:  # Add error handling for unexpected file paths
#         print(f"Error extracting title from '{file_path}': {e}")
#         return None 

# def process_pdfs(pdf_folder_path, disease_name):
#     """Iterates through PDFs in a folder and calls a processing script."""
    
#     pdf_files = glob.glob(pdf_folder_path + "/*.pdf")
#     output_directory =  f"../data/{disease_name}/{disease_name}_csvs" 

#     # Create output directory if it doesn't exist
#     os.makedirs(output_directory, exist_ok=True)  # This creates the directory if it doesn't exist

#     for pdf_file in pdf_files:
#         list_processed_sentences = process_text_to_sentences(pdf_file)
#         pdf_name = extract_title_from_path(pdf_file)
#         output_file = os.path.join(output_directory, pdf_name + ".csv")  # Use os.path.join for better path handling
        
#         with open(output_file, "w", newline="") as csvfile:
#             writer = csv.writer(csvfile, escapechar='\\')
#             # Write each sentence as a separate row
#             for s in list_processed_sentences:
#                 writer.writerow([s])

#         print(f"Processed: {pdf_file}")

import os
from pdfminer.high_level import extract_text
import spacy
import language_tool_python
import csv
import re
import glob

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")
# Load the LanguageTool grammar checker
tool = language_tool_python.LanguageTool('en-US')

def remove_references(text):
    """Removes the last reference section and citations from the text."""
    pattern = re.compile(
        r"""
        (
            ([Rr]eference[s]?|[Rr]EFERENCE[S]?|[Bb]ibliography|[Bb]IBLIOGRAPHY|[Ww]orks [Cc]ited|[Ww]ORKS [Cc]ITED|[Ee]ndnotes|[Ee]NDNOTES)\s*\n.*  # Reference section headers
        )
        """,
        re.VERBOSE | re.DOTALL  # Allow comments and matching across multiple lines
    )
    text = pattern.sub("", text)    
    return text

def remove_numbered_citations(text):
    """Removes numbered citations from the text."""
    citation_pattern = re.compile(
        r"""
        \[\d+(?:[,–]\s*\d+)*\]  # Numbered citations with optional ranges and spaces
        """,
        re.VERBOSE  # Allow comments and better readability
    )
    text = citation_pattern.sub("", text)
    return text

def process_text_to_sentences(path_to_pdf):
    try:
        # Extract text from the PDF article
        text = extract_text(path_to_pdf)
        text = remove_references(text)
        text = remove_numbered_citations(text)

        pattern = r'(\w+)-(\n)?(\w+)'
        text = re.sub(pattern, r'\1\3', text)  # Remove hyphenation
        
        # Split the text into lines and filter out empty lines
        lines = text.split('\n')
        filtered_lines = [line for line in lines if len(line.strip()) > 1]
        cleaned_text = ' '.join(filtered_lines).replace("\n", " ")

        # Process the text with spaCy
        doc = nlp(cleaned_text)
        sentences = [sent.text for sent in doc.sents]

        # Correct grammar
        corrected_sentences = []
        tool.disable_spellchecking()
        for sentence in sentences:
            corrected_sentences.append(tool.correct(sentence))

        return corrected_sentences

    except Exception as e:
        print(f"Error processing PDF: {path_to_pdf}")
        print(f"Error details: {e}")
        return []  # Return an empty list to continue processing other PDFs

def extract_title_from_path(file_path):
    try:
        _, filename = os.path.split(file_path)
        title, _ = os.path.splitext(filename)
        return title
    except Exception as e:
        print(f"Error extracting title from '{file_path}': {e}")
        return None 

def process_pdfs(pdf_folder_path, disease_name):
    """Iterates through PDFs in a folder and calls a processing script."""
    
    pdf_files = glob.glob(pdf_folder_path + "/*.pdf")
    output_directory = f"../data/{disease_name}/{disease_name}_csvs"
    os.makedirs(output_directory, exist_ok=True)  # Ensure output directory exists

    for pdf_file in pdf_files:
        try:
            pdf_name = extract_title_from_path(pdf_file)
            if pdf_name is None:
                continue  # Skip if title extraction failed

            list_processed_sentences = process_text_to_sentences(pdf_file)
            if not list_processed_sentences:
                print(f"Skipping {pdf_file} due to errors.")
                continue

            output_file = os.path.join(output_directory, pdf_name + ".csv")
            
            # with open(output_file, "w", newline="") as csvfile:
            #     writer = csv.writer(csvfile, escapechar='\\')
            #     for s in list_processed_sentences:
            #         writer.writerow([s])
            with open(output_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile, escapechar='\\')
                # Group sentences in chunks of 3
                for i in range(0, len(list_processed_sentences), 3):
                    chunk = list_processed_sentences[i:i+3]
                    combined = " ".join(chunk)
                    writer.writerow([combined])


            print(f"Processed: {pdf_file}")

        except Exception as e:
            print(f"Failed to process {pdf_file}: {e}")
            continue  # Ensure the loop continues even if an error occurs

disease =#"Acral persistent papular mucinosis"#"Nelson syndrome"#"Bilateral adrenal hemorrhage" #"Zimmermann-Laband syndrome"#"Adenine phosphoribosyltransferase deficiency"# "pachydermoperiostosis" #"Endocrine-cerebro-osteodysplasia syndrome" "Mabry syndrome" "Zimmermann-Laband syndrome"
#disease = #"Endocrine-cerebro-osteodysplasia syndrome" #"Nance-Horan syndrome" #"GNE myopathy" #"Mabry syndrome" #"Bilateral adrenal hemorrhage" #"Nelson syndrome"#"Nance-Horan syndrome" #"Adenine phosphoribosyltransferase deficiency" #"Acral persistent papular mucinosis" #"Zimmermann-Laband syndrome"
pdf_folder = f"../data/{disease}/{disease}_pdfs"
process_pdfs(pdf_folder, disease)



