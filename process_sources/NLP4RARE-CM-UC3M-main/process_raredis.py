import os
import csv

def process_brat_ann(file_path):
    entities = {}
    triples = []
    disease_names = set()  # To collect disease names from this file

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("T"):
                # Entity line
                parts = line.split("\t")
                if len(parts) < 3:
                    continue
                tid = parts[0]
                type_info = parts[1].split(" ")[0]
                text = parts[2]
                entities[tid] = (text, type_info)

                if type_info == "RAREDISEASE" or type_info == "DISEASE":
                    disease_names.add(text)

            elif line.startswith("R"):
                # Relation line
                parts = line.split("\t")
                if len(parts) < 2:
                    continue
                relation_info = parts[1].split(" ")
                if len(relation_info) < 3:
                    continue
                relation = relation_info[0]
                arg1 = relation_info[1].split(":")[1]
                arg2 = relation_info[2].split(":")[1]

                if arg1 in entities and arg2 in entities:
                    ent1_text, ent1_type = entities[arg1]
                    ent2_text, ent2_type = entities[arg2]

                    simple_sentence = f"{ent1_text} {relation.replace('_', ' ')} {ent2_text}"
                    triple = (ent1_text, relation.upper(), ent2_text)
                    tagged_triple = (f"{ent1_text} ({ent1_type})", f"{relation.upper()}", f"{ent2_text} ({ent2_type})")

                    triples.append({
                        "relevant_text": simple_sentence,
                        "simple_sentence": simple_sentence,
                        "triple": triple,
                        "tagged_triple": tagged_triple,
                        "entity1": ent1_text,
                        "tag1": ent1_type,
                        "relationship": relation.upper(),
                        "relationship_tag": relation.upper(),
                        "entity2": ent2_text,
                        "tag2": ent2_type,
                        "metadata": f"https://github.com/isegura/NLP4RARE-CM-UC3M/blob/main/{os.path.relpath(file_path)}"
                        #"metadata": os.path.relpath(file_path, start="RareDis-v1-without-texts")  # relative path
                    })

    return triples, disease_names

def process_all_ann_files(base_folder):
    all_triples = []
    all_diseases = set()
    file_count = 0

    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith(".ann"):
                file_path = os.path.join(root, file)
                triples, disease_names = process_brat_ann(file_path)
                all_triples.extend(triples)
                all_diseases.update(disease_names)
                file_count += 1

    return all_triples, all_diseases, file_count

if __name__ == "__main__":
    base_folder = "RareDis-v1-without-texts"
    output_csv = "final_raredis_ann_triples.csv"

    all_triples, all_diseases, file_count = process_all_ann_files(base_folder)

    # Write to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Relevant Text", "Simple Sentences", "Triple", "Tagged Triple",
            "Entity 1", "Tag 1", "Relationship", "Relationship Tag",
            "Entity 2", "Tag 2", "MetaData"
        ])

        for triple in all_triples:
            writer.writerow([
                triple["relevant_text"],
                triple["simple_sentence"],
                f"({triple['triple'][0]}, {triple['triple'][1]}, {triple['triple'][2]})",
                f"({triple['entity1']} ({triple['tag1']}), {triple['relationship']} ({triple['relationship_tag']}), {triple['entity2']} ({triple['tag2']}))",
                triple["entity1"], triple["tag1"],
                triple["relationship"], triple["relationship_tag"],
                triple["entity2"], triple["tag2"],
                triple["metadata"]
            ])

    # Print summary
    print("\n✅ Extraction completed!")
    print(f"📄 Number of .ann files processed: {file_count}")
    print(f"🧬 Number of unique diseases found: {len(all_diseases)}")
    print(f"🔗 Total number of triples extracted: {len(all_triples)}")
    print(f"📝 Saved into: {output_csv}")
