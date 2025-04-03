import pandas as pd
import csv, math
import matplotlib.pyplot as plt

disease_name = 'pachydermoperiostosis'
input_file_path_here = '../data/' + disease_name + '/updated_metadata_tagged_triple_' + disease_name + '.csv'
df2 = pd.read_csv(input_file_path_here)

# Create lists from the columns of the second CSV
input_relevant_text_list = df2['Relevant Text'].tolist()
input_simple_sentences_list = df2['Simple Sentences'].tolist()
input_triple_list = df2['Triple'].tolist()
input_tagged_triple_list = df2['Tagged Triple'].tolist()
input_entity_1_list = df2['Entity 1'].tolist()
input_tag_1_list = df2['Tag 1'].tolist()
input_relationship_list = df2['Relationship'].tolist()
input_entity_2_list = df2['Entity 2'].tolist()
input_tag_2_list = df2['Tag 2'].tolist()
input_metadata_list = df2['MetaData'].tolist()

valid_tags = ["location", "institute", "cell component", "disease", "body part", "enzyme", "biological process", 
              "sample", "population group", "treatment", "symptom", "protein", "gene", 
              "pathway", "mutation", "diagnostic procedure", "drug", "feature", "model", 
              "chemical", "time period", "observation", "role"]

# Combine input tag lists
tags_list = input_tag_1_list + input_tag_2_list

# Identify tags that are not in valid_tags
extra_tags = {tag for tag in tags_list if tag not in valid_tags}
print("Extra tags:", extra_tags)

# Count occurrences, categorizing tags not in valid_tags as "extra"
tag_counts = pd.Series([tag if tag in valid_tags else "extra" for tag in tags_list]).value_counts()

# Calculate total number of tags
total_tags = len(tags_list)

# Plotting the distribution using Matplotlib
plt.figure(figsize=(14, 8))  # Set figure size
plt.bar(tag_counts.index, tag_counts.values)  # Vertical bar chart
plt.title('Distribution of Entity Tags')
plt.xlabel('Tags')
plt.ylabel('Count')

# Add total number of tags as text on top of the plot
plt.text(0.5, 1.1, f'Total Tags: {total_tags}', ha='center', va='center', transform=plt.gca().transAxes, fontsize=12, fontweight='bold')

# Rotate x-axis labels for better visibility
plt.xticks(rotation=45, ha='right')  # Rotate and align labels

# Save the figure
plt.savefig('../data/' + disease_name + '/tags_distribution_' + disease_name +'.png', bbox_inches='tight')  # Save as PNG
plt.close()  # Close figure to free up memory





from sentence_transformers import SentenceTransformer, util
from collections import Counter

# Load MiniLM model for embedding
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

base_categories_for_relations = {
    "Classification/Type": [
        "IS", "ARE", "MATCHED TO", "IDENTIFIED AS", "CLASSIFIED AS", "CATEGORIZED AS", 
        "REPRESENTS", "DESCRIBED AS", "TYPIFIED BY", "DEFINED AS"
    ],
    "Containment/Component": [
        "HAS", "HAVE", "CONTAINS", "INCLUDE", "PART OF", "COMPOSED OF", "ENCLOSED IN", 
        "HOUSED IN", "CONSTITUTES", "IS A COMPONENT OF", "IS PART OF", "BELONGS TO"
    ],
    "Location/Presence": [
        "PRESENT IN", "LOCATED IN", "FOUND IN", "RESIDES IN", "EXISTS IN", 
        "OCCURS IN", "SITUATED IN", "DETECTED IN", "APPEARS IN", "EXHIBITS"
    ],
    "Cause/Effect": [
        "CAUSES", "RESULTS IN", "LEADS TO", "INDUCES", "CONTRIBUTES TO", 
        "PROMOTES", "TRIGGERS", "PROVOKES", "FACILITATES", "ENCOURAGES"
    ],
    "Function/Usage": [
        "USED IN", "APPLIED TO", "PERFORMED IN", "EMPLOYED FOR", "UTILIZED IN", 
        "DESIGNED FOR", "FUNCTIONS AS", "SERVES TO", "ACTS AS", "PURPOSED FOR"
    ],
    "Measurement/Expression": [
        "MEASURED IN", "SHOWS", "HAS", "DEMONSTRATES", "EXHIBITS", 
        "DISPLAYS", "INDICATES", "QUANTIFIED BY", "REPRESENTS", "SIGNIFIES"
    ],
    "Association/Link": [
        "ASSOCIATED WITH", "LINK", "RELATED TO", "CORRELATED WITH", "CONNECTED TO", 
        "INTERACTS WITH", "ALIGNED WITH", "BONDS WITH", "TIES TO", "INFLUENCES"
    ],
    "Process/Progression": [
        "OCCURS IN", "PROGRESSES TO", "FORMS", "DEVELOPS INTO", "TRANSITIONS TO", 
        "EVOLVES TO", "MATURES INTO", "ADVANCES TO", "CHANGES INTO", "MOVES TO"
    ],
    "Documentation/Evidence": [
        "DOCUMENTED IN", "ANALYZED IN", "REPORTED FOR", "OBSERVED IN", "RECORDED IN", 
        "VALIDATED IN", "CONFIRMED IN", "ESTABLISHED IN", "NOTED IN", "REGISTERED IN"
    ],
    "Action/Delivery": [
        "DELIVERS", "TARGETS", "TRANSPORTS TO", "CARRIES TO", "DISTRIBUTES TO", 
        "DISPATCHES TO", "CONVEYS", "SUPPLIES", "PROVIDES TO", "ENFOLDS"
    ],
    "Similarity/Comparison": [
        "SIMILAR TO", "COMPARED TO", "MATCHES", "ANALOGOUS TO", "EQUIVALENT TO", 
        "RESEMBLES", "ALIGNED WITH", "COMPARABLE TO", "LIKE", "PARALLELS"
    ],
    "Activation/Inhibition": [
        "ACTIVATED IN", "INHIBITED BY", "STIMULATED BY", "INITIATED BY", "INFLUENCED BY", 
        "ENHANCED BY", "SUPPRESSED BY", "MODULATED BY", "TRIGGERED BY", "REGULATED BY"
    ],
    "Regulation/Control": [
        "REGULATED BY", "CONTROLS", "SUPPRESSED BY", "MODULATED BY", "GOVERNED BY", 
        "MAINTAINED BY", "ADJUSTED BY", "DIRECTED BY", "OVERSEEN BY", "ADMINISTERED BY"
    ],
    "Interaction/Engagement": [
        "INTERACTS WITH", "ENGAGES WITH", "COOPERATES WITH", "COLLABORATES WITH", 
        "PARTICIPATES IN", "CONTRIBUTES TO", "ASSISTS WITH", "SUPPORTS", "REINFORCES", "CONNECTS TO"
    ],
    "Development/Change": [
        "EVOLVES", "CHANGES", "TRANSFORMS", "ADAPTS", "MODIFIES", 
        "MATURES", "GROWS", "PROGRESSES", "DEVELOPS", "REFINES"
    ],
    "Condition/State": [
        "IS PRESENT", "IS ABSENT", "EXISTS AS", "OCCURS AS", "MANIFESTS AS", 
        "APPEARS AS", "IS DETERMINED BY", "DEPENDS ON", "AFFECTS", "IMPACTS"
    ],
    "Therapeutic/Treatment": [
        "TREATED BY", "MANAGED BY", "ADDRESSING", "HELPED BY", "CURING", 
        "FACILITATES TREATMENT", "ENHANCES HEALING", "ASSISTS IN RECOVERY", 
        "RESTORES", "SUPPORTS RECOVERY"
    ],
    "Mechanism/Pathway": [
        "INVOLVED IN", "ENGAGED IN", "PARTICIPATES IN", "PLAYS A ROLE IN", 
        "CONTRIBUTES TO", "FACILITATES", "ENABLES", "AFFECTS", "MODIFIES", "INTERFERES WITH"
    ]
}

# Encode base category examples
category_embeddings = {category: model.encode(examples) for category, examples in base_categories_for_relations.items()}

relationships = [str(item) for item in input_relationship_list]
# Prepare to store categorization and counts
relationship_to_category = {}
base_counts = Counter()

# Categorize each relationship
for relation in relationships:
    embed = model.encode(relation)
    best_category, best_score = None, float("-inf")
    for category, category_embeds in category_embeddings.items():
        # Use .max() to get the highest similarity score for this category
        score = util.cos_sim(embed, category_embeds).max().item()  # Convert to scalar
        if score > best_score:
            best_category, best_score = category, score
    relationship_to_category[relation] = best_category
    base_counts[best_category] += 1

# print("Relationship Categorization:", relationship_to_category)
# print({k for k, v in relationship_to_category.items() if v == "Therapeutic/Treatment"})

print("Counts per Category:", base_counts)
# Calculate and print total count of relationships categorized
total_count = sum(base_counts.values())
print("Total Count of Relationships:", total_count)



# Prepare data for plotting
categories = list(base_counts.keys())
counts = list(base_counts.values())

# Plotting the histogram of categories
plt.figure(figsize=(12, 6))  # Increase the figure size
plt.bar(categories, counts, color='skyblue', edgecolor='black')
plt.title('Distribution of Relationship Categories')
plt.xlabel('Categories')
plt.ylabel('Counts')

# Add total number of tags as text on top of the plot
plt.text(0.5, 1.1, f'Total Relationships: {total_count}', ha='center', va='center', transform=plt.gca().transAxes, fontsize=12, fontweight='bold')

# Rotate x-axis labels and set alignment
plt.xticks(rotation=45, ha='right', fontsize=10)  # Adjust rotation and alignment
plt.tight_layout()  # Automatically adjust layout

# Save the histogram as an image file
plt.savefig('../data/' + disease_name + '/relationship_category_distribution_' + disease_name +'.png', bbox_inches='tight')  # Use bbox_inches to include all labels
plt.close()  # Close the plot to free memory


list_of_relationships_tag = []
for rel in relationships:
    if relationship_to_category[rel]:
        list_of_relationships_tag.append(relationship_to_category[rel])
    else:
        list_of_relationships_tag.append('None')





row_count1 = 0
file = '../data/' + disease_name + '/final_with_extra_tag_' + disease_name + '.csv' 
with open(file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Relevant Text', 'Simple Sentences', 'Triple', 'Tagged Triple','Entity 1', 'Tag 1', 'Relationship', 'Relationship Tag', 'Entity 2', 'Tag 2', 'MetaData'])
    for item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11 in zip(input_relevant_text_list, input_simple_sentences_list, input_triple_list, input_tagged_triple_list, input_entity_1_list, input_tag_1_list, input_relationship_list, list_of_relationships_tag, input_entity_2_list, input_tag_2_list, input_metadata_list):
        row_count1 += 1
        if item6 in valid_tags and item10 in valid_tags:
            writer.writerow([item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11])
        else:
            if item6 not in valid_tags and item10 in valid_tags:
                writer.writerow([item1, item2, item3, item4, item5, 'extra', item7, item8, item9, item10, item11])
            elif item10 not in valid_tags and item6 in valid_tags:
                writer.writerow([item1, item2, item3, item4, item5, item6, item7, item8, item9, 'extra', item11])
            else:
                writer.writerow([item1, item2, item3, item4, item5, 'extra', item7, item8, item9, 'extra', item11])
print("Number of tripes in the final file with extra tags:", row_count1)





row_count2 = 0
file = '../data/' + disease_name + '/final_without_extra_tag_' + disease_name + '.csv' 
with open(file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Relevant Text', 'Simple Sentences', 'Triple', 'Tagged Triple','Entity 1', 'Tag 1', 'Relationship', 'Relationship Tag', 'Entity 2', 'Tag 2', 'MetaData'])
    for item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11 in zip(input_relevant_text_list, input_simple_sentences_list, input_triple_list, input_tagged_triple_list, input_entity_1_list, input_tag_1_list, input_relationship_list, list_of_relationships_tag, input_entity_2_list, input_tag_2_list, input_metadata_list):
        if item6 in valid_tags and item10 in valid_tags:
            row_count2 += 1
            writer.writerow([item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11])
print("Number of tripes in the final file without extra tags:", row_count2)




# This final file contains all the extra tags but with their real names, like dosage or cell line is used instead of extra
# However, these removed tags such as nan, number, author, email, person, 
# hence only these tags are are not included in this final file
unwanted_values_for_tags = {float('nan'), 'number', 'author', 'email', 'person'}
row_count3 = 0
file = '../data/' + disease_name + '/final_' + disease_name + '.csv' 
with open(file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Relevant Text', 'Simple Sentences', 'Triple', 'Tagged Triple','Entity 1', 'Tag 1', 'Relationship', 'Relationship Tag', 'Entity 2', 'Tag 2', 'MetaData'])
    for item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11 in zip(input_relevant_text_list, input_simple_sentences_list, input_triple_list, input_tagged_triple_list, input_entity_1_list, input_tag_1_list, input_relationship_list, list_of_relationships_tag, input_entity_2_list, input_tag_2_list, input_metadata_list):
        if (item6 not in unwanted_values_for_tags and not (isinstance(item6, float) and math.isnan(item6))) or \
           (item10 not in unwanted_values_for_tags and not (isinstance(item10, float) and math.isnan(item10))):
            row_count3 += 1
            writer.writerow([item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11])
print("Number of tripes in the final file with extra tags:", row_count3)





ontology_strings_list = []
for i in range(0, len(input_tag_1_list)):
    if str(input_tag_1_list[i]) in valid_tags and str(input_tag_2_list[i]) in valid_tags:
        if str(input_tag_1_list[i]) == 'disease' or str(input_tag_2_list[i]) == 'disease':
            i_am_a_string = str(input_tag_1_list[i]) +" - "+ str(list_of_relationships_tag[i]) +" - "+ str(input_tag_2_list[i])
            ontology_strings_list.append(i_am_a_string)

ontology_strings_list = list(set(ontology_strings_list))

# Print each value in a new line using a loop in one line
print(*(item for item in ontology_strings_list), sep='\n')
