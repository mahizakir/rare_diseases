import pandas as pd
import csv, os, sys

disease_name = 'pachydermoperiostosis'
file_path = '../data/' + disease_name + '/formatted_triples_' + disease_name + '.csv' 

df = pd.read_csv(file_path, usecols=[0, 1, 2, 3, 4, 5, 6], header=0) # Read the CSV file, skipping the header
list_of_relevant_sentences = df.iloc[:, 0].tolist() #[0:20] # Convert the first column values to a list, skipping the header
list_of_simple_sentences =  df.iloc[:, 1].tolist() #[0:20]
list_of_triples = df.iloc[:, 2].tolist() #[0:20]
list_of_entity_1 = df.iloc[:, 3].tolist() #[0:20]
list_of_relations = df.iloc[:, 4].tolist() #[0:20] 
list_of_entity_2 =df.iloc[:, 5].tolist() #[0:20] 
list_of_meta_data =  df.iloc[:, 6].tolist() #[0:20]

# list_of_inputs = list_of_triples

# Create list_of_inputs by combining elements from list_of_relevant_sentences and list_of_triples
list_of_inputs = [f"{list_of_relevant_sentences[i]}- {list_of_triples[i]}" for i in range(len(list_of_relevant_sentences))]
# print(list_of_inputs)

import torch
import pandas as pd
import re, csv

parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))
sys.path.append(parent_directory)
from global_prompts import tagging_triples_prompt_with_relevant_sentences, global_output_max_new_tokens

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

given_prompt = tagging_triples_prompt_with_relevant_sentences

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





# Function to extract Entity1, Tag1, Relationship, Entity2, Tag2
def extract_triple_components(tagged_triple):
    # Regular expression to extract the relevant parts from the Tagged Triple
    match = re.match(r"\((.*) \((.*)\), (.*), (.*) \((.*)\)\)", tagged_triple)
    
    if match:
        entity1 = match.group(1)
        tag1 = match.group(2)
        relationship = match.group(3)
        entity2 = match.group(4)
        tag2 = match.group(5)
    else:
        # If the structure doesn't match, return None for each part
        entity1 = tag1 = relationship = entity2 = tag2 = None
    
    return entity1, tag1, relationship, entity2, tag2

entity1_list = []
tag1_list = []
relationship_list = []
entity2_list = []
tag2_list = []
for tt in responses_list:
    entity1, tag1, relationship, entity2, tag2 = extract_triple_components(tt)
    # Append each part to its respective list
    entity1_list.append(entity1)
    tag1_list.append(tag1)
    relationship_list.append(relationship)
    entity2_list.append(entity2)
    tag2_list.append(tag2)



output_file = '../data/' + disease_name + '/tagged_triples_from_triple_and_relevant_sentence_with_' + disease_name + '.csv' 
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Relevant Text', 'Simple Sentences', 'Triple', 'Tagged Triple','Entity 1', 'Tag 1', 'Relationship', 'Entity 2', 'Tag 2', 'MetaData'])
    for item1, item2, item3, item4, item5, item6, item7, item8, item9, item10 in zip(list_of_relevant_sentences, list_of_simple_sentences, list_of_triples, responses_list, entity1_list, tag1_list, relationship_list, entity2_list, tag2_list, list_of_meta_data):
        writer.writerow([item1, item2, item3, item4, item5, item6, item7, item8, item9, item10])