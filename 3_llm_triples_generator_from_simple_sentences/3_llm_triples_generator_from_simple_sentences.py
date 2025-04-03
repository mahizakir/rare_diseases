import torch
import pandas as pd
import re, csv, os, sys
from unsloth import FastLanguageModel
from transformers import TextStreamer

parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(parent_directory)
from global_prompts import triplets_from_simple_sentence_prompt, global_output_max_new_tokens

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

given_prompt = triplets_from_simple_sentence_prompt

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
file_path = '../data/' + disease_name + '/generated_simple_sentences' + disease_name + '.csv' 
df = pd.read_csv(file_path, usecols=[0, 1, 2], header=0) # Read the CSV file, skipping the header
list_of_unformatted_original_sentences = df.iloc[:, 0].tolist() # Convert the first column values to a list, skipping the header
list_of_unformatted_simple_sentences =  df.iloc[:, 1].tolist()
list_of_unformatted_meta_data =  df.iloc[:, 2].tolist()

list_of_formatted_original_sentences = []
list_of_formatted_simple_sentences = []
list_of_formatted_meta_data = []

for i in range(0,len(list_of_unformatted_simple_sentences)):
    lines = list_of_unformatted_simple_sentences[i].splitlines()
    cleaned_sentences = []
    for line in lines:
        sentence = line.strip() # Remove leading and trailing whitespace
        if sentence.startswith('(') and sentence.endswith(')'): # Strip parentheses if they are present at the beginning and end
            sentence = sentence[1:-1].strip()
        if sentence.startswith('"') and sentence.endswith('"'): # Strip quotes if they are present at the beginning and end
            sentence = sentence[1:-1].strip()
        if sentence:  # Only add non-empty sentences
            cleaned_sentences.append(sentence)
    if len(cleaned_sentences) > 0:
        clean_length = len(cleaned_sentences)
        list_of_formatted_original_sentences.extend([list_of_unformatted_original_sentences[i]] * clean_length)
        list_of_formatted_simple_sentences.extend(cleaned_sentences)
        list_of_formatted_meta_data.extend([list_of_unformatted_meta_data[i]] * clean_length)


print(len(list_of_formatted_original_sentences), len(list_of_formatted_simple_sentences), len(list_of_formatted_meta_data))
        

list_of_inputs = list_of_formatted_simple_sentences #[0:3]
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



output_file = '../data/' + disease_name + '/generated_triples_from_simple_sentences_' + disease_name + '.csv' 
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Relevant Text', 'Simple Sentences', 'Triples', 'MetaData'])
    for item1, item2, item3, item4 in zip(list_of_formatted_original_sentences, list_of_formatted_simple_sentences, responses_list, list_of_formatted_meta_data):
        writer.writerow([item1, item2, item3, item4])

print(f'CSV file "{output_file}" created successfully.')

# import subprocess
# subprocess.run(["python", "simple_sentence_to_triples/format_generated_triples.py"])