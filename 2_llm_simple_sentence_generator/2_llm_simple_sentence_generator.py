import torch
import pandas as pd
import re, csv, os, sys
from unsloth import FastLanguageModel
from transformers import TextStreamer

parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(parent_directory)
from global_prompts import simple_sentence_prompt, global_output_max_new_tokens

# Initialize CUDA if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Configuration
max_seq_length = global_output_max_new_tokens
dtype = None
load_in_4bit = True  # Use 4bit quantization to reduce memory usage. Can be False.

# Load finetuned model
if True:
    from unsloth import FastLanguageModel
    # Load finetuned model
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name='unsloth/gemma-3-27b-it-unsloth-bnb-4bit',
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=load_in_4bit,
        token="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",
    )
    FastLanguageModel.for_inference(model)

given_prompt = simple_sentence_prompt

# Include every prompt in this format
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

def extract_response(input_string):
    pattern = r'### Response:\n(.*?)(?=\n###|$)'  # Updated pattern to ensure it captures the full response
    match = re.search(pattern, input_string, re.DOTALL)
    if match:
        response = match.group(1).strip()  # Extract and clean the response
        return response

disease_name = 'pachydermoperiostosis'
file_path = '../data/' + disease_name + '/relevant_texts_' + disease_name + '.csv'  # Replace with your CSV file path
df = pd.read_csv(file_path, usecols=[0, 1], header=0) # Read the CSV file, skipping the header
list_of_inputs = df.iloc[:, 0].tolist() # Convert the first column values to a list, skipping the header
list_of_meta_data =  df.iloc[:, 1].tolist()

# list_of_inputs = list_of_inputs[0:3]
print(len(list_of_inputs))
print("~"*100)

responses_list = [None for _ in list_of_inputs]
for i in range(0,len(list_of_inputs)):
    input_here = list_of_inputs[i]

    print("~"*100)
    inputs = tokenizer(
    [
        alpaca_prompt.format(
                    given_prompt,
                    input_here,
                    "", 
                )
    ], return_tensors = "pt").to("cuda")

    from transformers import TextStreamer
    text_streamer = TextStreamer(tokenizer)
    # _ = model.generate(**inputs, streamer = text_streamer, max_new_tokens = global_output_max_new_tokens)
    output_ids = model.generate(**inputs, streamer=text_streamer, max_new_tokens=global_output_max_new_tokens)
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    res = extract_response(generated_text)
    responses_list[i] = res
    print(i)




import warnings
# Suppress specific FutureWarning from transformers
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers.tokenization_utils_base")
# Remove the redundant simple sentences with the same meaning generated from the relevant text
from sentence_transformers import SentenceTransformer, util
# Load a sentence-transformer model optimized for paraphrase detection
model_to_find_unique_sentences = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def find_unique_sentences(list_of_sentences_here):
    # Get sentence embeddings
    embeddings_to_find_unique_sentences = model_to_find_unique_sentences.encode(list_of_sentences_here, convert_to_tensor=True)
    unique_sentences = []
    cosine_scores = util.pytorch_cos_sim(embeddings_to_find_unique_sentences, embeddings_to_find_unique_sentences)
    added = set()
    threshold = 0.95  # Similarity threshold

    for i in range(len(list_of_sentences_here)):
        if i in added:
            continue
        unique_sentences.append(list_of_sentences_here[i])
        for j in range(i + 1, len(list_of_sentences_here)):
            if cosine_scores[i][j] > threshold:
                added.add(j)
    return unique_sentences


number_of_cleaned_sentences = 0
number_of_unique_sentences = 0
new_response_list = []
for res in responses_list:
    lines = res.splitlines()
    cleaned_sentences = []
    for line in lines:
        sentence = line.strip() # Remove leading and trailing whitespace
        if sentence.startswith('(') and sentence.endswith(')'): # Strip parentheses if they are present at the beginning and end
            sentence = sentence[1:-1].strip()
        if sentence.startswith('"') and sentence.endswith('"'): # Strip quotes if they are present at the beginning and end
            sentence = sentence[1:-1].strip()
        if sentence:  # Only add non-empty sentences
            cleaned_sentences.append(sentence)

    number_of_cleaned_sentences = number_of_cleaned_sentences + len(cleaned_sentences)  
    unique_sentences = find_unique_sentences(cleaned_sentences)
    number_of_unique_sentences = number_of_unique_sentences + len(unique_sentences)
    formatted_string = "\n".join(f'("{sen}")' for sen in unique_sentences)
    new_response = formatted_string
    new_response_list.append(new_response)
    





output_file = '../data/' + disease_name + '/generated_simple_sentences' + disease_name + '.csv' 
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Relevant Text', 'Simple Sentences', 'MetaData'])
    for item1, item2, item3 in zip(list_of_inputs, new_response_list, list_of_meta_data):
        writer.writerow([item1, item2, item3])

print(f'CSV file "{output_file}" created successfully.')

print("Number of simple sentences in llm response:", number_of_cleaned_sentences)
print("Number of unique sentences found in final output:", number_of_unique_sentences)

# import subprocess
# subprocess.run(["python3", "triplets_generator_from_simple_sentences.py"])