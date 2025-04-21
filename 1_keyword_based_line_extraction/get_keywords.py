import pandas as pd
import requests
import torch
import re
from bs4 import BeautifulSoup
import spacy
from unsloth import FastLanguageModel
from transformers import TextStreamer



# Load CSV file (Update filename accordingly)
df = pd.read_csv("ORPHAnomenclature_MasterFile_en_2024..xlsx - ICD10.csv")

def get_orphacode(term: str) -> int:
    """Find ORPHAcode for a given disease term."""
    match = df[df["PreferredTerm"].str.lower() == term.lower()]
    if match.empty:
        # If no match in PreferredTerm, try searching in Synonyms
        match = df[df["Synonyms"].str.lower().str.contains(term.lower(), na=False)]
    return match["ORPHAcode"].values[0] if not match.empty else None

def scrape_disease_definition(orphacode: int) -> str:
    """Scrape 'Disease definition' from Orphanet using ORPHAcode."""
    url = f"https://www.orpha.net/en/disease/detail/{orphacode}"
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error: Unable to fetch data (status code {response.status_code})"
    
    soup = BeautifulSoup(response.text, "html.parser")
    definition_box = soup.find("div", class_="service-color-box")
    if definition_box:
        definition_paragraph = definition_box.find("p")
        return definition_paragraph.get_text(strip=True) if definition_paragraph else "Disease definition not found."
    return "Disease definition not found."

# Check CUDA availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model Configuration
max_seq_length = 512
load_in_4bit = True  # Reduce memory usage

# Load finetuned model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name='unsloth/gemma-3-27b-it-unsloth-bnb-4bit',
    max_seq_length=max_seq_length,
    dtype=None,
    load_in_4bit=load_in_4bit,
    token="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",
)
FastLanguageModel.for_inference(model)

# Define prompts
given_prompt = (
    "You are an advanced NLP model. Extract biologically relevant words (diseases, symptoms, genes, etc.) from the given text."
    " Provide the extracted words as a comma-separated list without any additional explanations.\n\n"
    "Text:\nThe study of human genes has revealed insights into hereditary diseases such as cystic fibrosis and sickle cell anemia."
    " Symptoms of these diseases may include chronic respiratory issues and fatigue. Proteins play crucial roles in the mechanisms of these conditions,"
    " and understanding their functions can lead to advancements in medical treatments.\n\n"
    "Example output:\ncystic fibrosis, sickle cell anemia, symptoms, chronic respiratory issues, fatigue, treatments"
)

alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{}\n\n### Input:\n{}\n\n### Response:\n{}"""

def extract_response(input_string: str) -> str:
    """Extract the response content from the generated output."""
    match = re.search(r'### Response:\n(.*?)(?=\n###|$)', input_string, re.DOTALL)
    return match.group(1).strip() if match else ""

def generate_response(definition: str) -> str:
    """Generate biologically relevant words from the disease definition using the model."""
    input_text = alpaca_prompt.format(given_prompt, definition, "")
    inputs = tokenizer([input_text], return_tensors="pt").to(device)
    text_streamer = TextStreamer(tokenizer)
    output_ids = model.generate(**inputs, streamer=text_streamer, max_new_tokens=max_seq_length)
    return extract_response(tokenizer.decode(output_ids[0], skip_special_tokens=True))



def find_keywords(disease_name):
    orphacode = get_orphacode(disease_name)

    if orphacode:
        print(f"ORPHAcode for {disease_name}: {orphacode}")
        definition = scrape_disease_definition(orphacode)
        print(f"Disease definition: {definition}")
        print("~" * 100)
        extracted_terms = generate_response(definition)
        print(extracted_terms)
        keywords = extracted_terms.split(", ")

        # Check if the disease_name is already in the keywords list
        if disease_name.lower() not in [keyword.lower() for keyword in keywords]:
            keywords.append(disease_name)  # Add the disease_name if not found

    elif orphacode is None:
        if disease_name == "Bilateral adrenal hemorrhage":
            definition = "Bilateral adrenal hemorrhage is the condition when bleeding occurs in both adrenal glands, which could be instantly life-threatening. Over half of the bilateral cases are related to acute stress, such as infection, congestive myocardial infarction, complications of pregnancy, surgery or invasive procedure. Other common causes include hemorrhagic diatheses, thromboembolic diseases, blunt trauma, and adrenocorticotropic hormone (ACTH) therapy. With sepsis, the mortality rate of this condition can reach 90%"

        extracted_terms = generate_response(definition)
        print(extracted_terms)
        keywords = extracted_terms.split(", ")

        # Check if the disease_name is already in the keywords list
        if disease_name.lower() not in [keyword.lower() for keyword in keywords]:
            keywords.append(disease_name)  # Add the disease_name if not found

    return keywords




# import re
# import math

# def create_regex_for_match(word):
#     # Calculate 90% of the word's length
#     match_length = math.floor(len(word) * 0.9)
    
#     # Create a regex pattern that matches the first 90% of the word
#     # The first 'match_length' characters are matched literally
#     pattern = r"^" + re.escape(word[:match_length])  # Escape to handle special characters

#     return pattern

# # Example word to test
# word = "Pachydermoperiostosis"
# pattern = create_regex_for_match(word)

# # Example text to search for matches
# text = ["Pachydermoperiostosis", "Pachydermoperiostos", "Pachy", "Pachyderma"]

# # Apply regex to each word in the list
# for w in text:
#     if re.match(pattern, w):
#         print(f"Match found: {w}")
#     else:
#         print(f"No match: {w}")
