# import csv
# import xml.etree.ElementTree as ET
# import json
# import os
# import requests
# import time

# def parsePacket(path: str, orpha_code: int):
#     lines = []
#     more = []

#     with open(path) as file:
#         try:
#             packetDict = json.load(file)
#         except json.decoder.JSONDecodeError as e:
#             print(f'Could not parse ORPHA packet file:\n{e}')
#             return lines, more

#     packet = packetDict['Orphapacket']
#     date = (packet['creationDate'][:10]).replace('-', '/')
#     source = f"OrphaData:{orpha_code}; {date}"

#     disease_name = packet['Label']
#     disease_tag = "disease"
#     definition_text = packet.get('TextSection', {}).get('Contents', "")

#     # Disorder type
#     disorder_type = packet['DisorderType']['value']
#     lines.append(make_line(definition_text, disease_name, disease_tag, "IS", "Classification/Type", disorder_type, "disorder type", source))

#     # Synonyms
#     for syn in packet.get('Synonyms', []):
#         synonym = syn['Synonym']
#         lines.append(make_line(definition_text, disease_name, disease_tag, "HAS SYNONYM", "Classification/Type", synonym, "disease", source))

#     # Genes
#     for gene in packet.get('Genes', []):
#         gene_symbol = gene['Gene']['Symbol']
#         gene_name = gene['Gene']['Name']
#         lines.append(make_line(definition_text, disease_name, disease_tag, "INVOLVES", "Mechanism/Pathway", gene_symbol, "gene", source))
#         lines.append(make_line(definition_text, gene_name, "gene", "HAS SYNONYM", "Classification/Type", gene_symbol, "gene", source))

#     # Parents
#     for parent in packet.get('Parents', []):
#         parent_label = parent['Parent'][0]['Label']
#         parent_orpha = parent['Parent'][0]['ORPHAcode']
#         lines.append(make_line(definition_text, disease_name, disease_tag, "ISA", "Classification/Type", parent_label, "disease", source))
#         more.append(parent_orpha)

#     # Phenotypes
#     for pheno in packet.get('Phenotypes', []):
#         pheno_name = pheno['Phenotype']['HPOTerm']
#         lines.append(make_line(definition_text, disease_name, disease_tag, "HAS", "Containment/Component", pheno_name, "phenotype", source))

#     # Prevalence
#     for prev in packet.get('Prevalences', []):
#         prevalence = f"{prev['Prevalence']['PrevalenceClass'].replace(' ', '')}; {prev['Prevalence']['PrevalenceGeographic']}"
#         lines.append(make_line(definition_text, disease_name, disease_tag, "HAS", "Containment/Component", prevalence, "feature", source))

#     # Onset
#     for onset in packet.get('AverageAgeOfOnsets', []):
#         onset_value = onset['AverageAgeOfOnset']['value']
#         lines.append(make_line(definition_text, disease_name, disease_tag, "HAS", "Containment/Component", onset_value, "feature", source))

#     # Inheritance
#     for inherit in packet.get('TypeOfInheritances', []):
#         inherit_value = inherit['TypeOfInheritance']['value']
#         lines.append(make_line(definition_text, disease_name, disease_tag, "HAS", "Containment/Component", inherit_value, "feature", source))

#     return lines, more


# def parseProduct6(path: str, orpha_code: int):
#     lines = []
#     with open(path, 'rb') as file:
#         root = ET.parse(file).getroot()
#         date = (root.attrib['date'][:10]).replace('-', '/')
#         source = f"OrphaData:{orpha_code}; {date}"

#         for disorder in root.findall('.//Disorder'):
#             code = disorder.find('OrphaCode')
#             if code is not None and code.text == str(orpha_code):
#                 disease_name = disorder.find('Name').text
#                 for association in disorder.findall('.//DisorderGeneAssociation'):
#                     try:
#                         source_text = association.find('.//SourceOfValidation').text
#                     except:
#                         source_text = source

#                     gene_section = association.find('Gene')
#                     if gene_section is None:
#                         continue

#                     gene_name = gene_section.find('.//Name').text
#                     gene_symbol = gene_section.find('.//Symbol').text

#                     lines.append(make_line("Gene association", disease_name, "disease", "INVOLVES", "Mechanism/Pathway", gene_name, "gene", source_text))
#                     lines.append(make_line("Gene association", gene_name, "gene", "HAS SYNONYM", "Classification/Type", gene_symbol, "gene", source_text))

#                     for syn in gene_section.findall('.//Synonym'):
#                         lines.append(make_line("Gene association", gene_name, "gene", "HAS SYNONYM", "Classification/Type", syn.text, "gene", source_text))

#                     for locus in gene_section.findall('.//GeneLocus'):
#                         lines.append(make_line("Gene association", gene_name, "gene", "LOCATED", "Location/Presence", locus.text, "location", source_text))

#     return lines


# def parseFunctConsequence(path: str, orpha_code: int):
#     lines = []
#     with open(path, 'rb') as file:
#         root = ET.parse(file).getroot()
#         date = (root.attrib['date'][:10]).replace('-', '/')
#         source = f"OrphaData:{orpha_code}; {date}"

#         for disorder in root.findall('.//Disorder'):
#             code = disorder.find('OrphaCode')
#             if code is not None and code.text == str(orpha_code):
#                 disease_name = disorder.find('Name').text
#                 for d in disorder.findall('.//DisabilityDisorderAssociation'):
#                     disability = d.find('Disability')
#                     if disability is not None:
#                         dis_name = disability.find('Name').text
#                         lines.append(make_line("Functional consequence", disease_name, "disease", "IMPACTS", "Condition/State", dis_name, "ability", source))
#     return lines

# def make_line(relevant_text, entity1, tag1, relation, rel_tag, entity2, tag2, metadata):
#     simple_sentence = f"{entity1} {relation} {entity2}"
#     return {
#         "relevant_text": simple_sentence,#relevant_text,
#         "simple_sentence": simple_sentence,
#         "triple": (entity1, relation, entity2),
#         "tagged_triple": (entity1, tag1, relation, rel_tag, entity2, tag2),
#         "entity1": entity1,
#         "tag1": tag1,
#         "relationship": relation,
#         "relationship_tag": rel_tag,
#         "entity2": entity2,
#         "tag2": tag2,
#         "metadata": metadata
#     }


# def downloadFiles(orpha_code: int):
#     try:
#         if not os.path.exists('DATA'):
#             os.makedirs('DATA')
#     except OSError as e:
#         print(f"Error creating DATA folder: {e}")

#     orpha_url = f"https://raw.githubusercontent.com/Orphanet/orphapacket/refs/heads/master/json/ORPHApacket_{orpha_code}.json"
#     prod6_url = "https://www.orphadata.com/data/xml/en_product6.xml"
#     funct_url = "https://www.orphadata.com/data/xml/en_funct_consequences.xml"

#     files_dict = {
#         orpha_url: f"DATA/ORPHApacket_{orpha_code}.json",
#         prod6_url: "DATA/en_product6.xml",
#         funct_url: "DATA/en_funct_consequences.xml"
#     }

#     for url, filepath in files_dict.items():
#         if os.path.exists(filepath):
#             print(f"File already exists: {filepath} ...Skipping download!")
#             continue
#         else:
#             try:
#                 response = requests.get(url, stream=True)
#                 response.raise_for_status()
#                 with open(filepath, 'wb') as file:
#                     for chunk in response.iter_content(chunk_size=8192):
#                         if chunk:
#                             file.write(chunk)
#                 print(f"Downloaded: {filepath}")
#             except requests.exceptions.RequestException as e:
#                 print(f"Error downloading {url}: {e}")
#                 return None

#     return [f"DATA/ORPHApacket_{orpha_code}.json", "DATA/en_product6.xml", "DATA/en_funct_consequences.xml"]


# def extractORPHA(orpha_code: int):
#     all_lines = []
#     files = downloadFiles(orpha_code)
#     if files is None:
#         return

#     packet_lines, more = parsePacket(files[0], orpha_code)
#     all_lines.extend(packet_lines)

#     prod6_lines = parseProduct6(files[1], orpha_code)
#     all_lines.extend(prod6_lines)

#     funct_lines = parseFunctConsequence(files[2], orpha_code)
#     all_lines.extend(funct_lines)

#     return all_lines, more


# if __name__ == "__main__":
#     start = time.time()
#     lines, more = extractORPHA(602)
#     if lines:
#         with open("OUTPUT.csv", "w", newline="", encoding="utf-8") as file:
#             writer = csv.writer(file)
#             writer.writerow([
#                 "Relevant Text", "Simple Sentences", "Triple", "Tagged Triple",
#                 "Entity 1", "Tag 1", "Relationship", "Relationship Tag",
#                 "Entity 2", "Tag 2", "MetaData"
#             ])

#             for triple in lines:
#                 writer.writerow([
#                     triple["relevant_text"],
#                     triple["simple_sentence"],
#                     f"({triple['triple'][0]}, {triple['triple'][1]}, {triple['triple'][2]})",
#                     f"({triple['entity1']} ({triple['tag1']}), {triple['relationship']} ({triple['relationship_tag']}), {triple['entity2']} ({triple['tag2']}))",
#                     triple["entity1"], triple["tag1"],
#                     triple["relationship"], triple["relationship_tag"],
#                     triple["entity2"], triple["tag2"],
#                     triple["metadata"]
#                 ])
#         print(f"Saved triples in OUTPUT.csv in {time.time() - start:.2f} seconds.")
#     else:
#         print("No data extracted.")



import csv
import xml.etree.ElementTree as ET
import json
import os
import requests
import time
import pandas as pd

def parsePacket(path: str, orpha_code: int):
    lines = []
    more = []

    with open(path) as file:
        try:
            packetDict = json.load(file)
        except json.decoder.JSONDecodeError as e:
            print(f'Could not parse ORPHA packet file:\n{e}')
            return lines, more

    packet = packetDict['Orphapacket']
    disease_name = packet['Label']
    # source = f"{disease_name} (OrphaCode: {orpha_code}) - https://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=EN&Expert={orpha_code}"
    # source = f"{disease_name} (OrphaCode: {orpha_code}) - https://www.orpha.net/en/disease/detail/{orpha_code}"
    source = f"{disease_name} (OrphaCode: {orpha_code}) - https://raw.githubusercontent.com/Orphanet/orphapacket/master/json/ORPHApacket_{orpha_code}.json"


    disease_name = packet['Label']
    disease_tag = "disease"
    definition_text = packet.get('TextSection', {}).get('Contents', "")

    # Disorder type
    disorder_type = packet['DisorderType']['value']
    lines.append(make_line(disease_name, disease_tag, "IS", "Classification/Type", disorder_type, "disorder type", source))

    # Synonyms
    for syn in packet.get('Synonyms', []):
        synonym = syn['Synonym']
        lines.append(make_line(disease_name, disease_tag, "HAS SYNONYM", "Classification/Type", synonym, "disease", source))

    # Genes
    for gene in packet.get('Genes', []):
        gene_symbol = gene['Gene']['Symbol']
        gene_name = gene['Gene']['Name']
        lines.append(make_line(disease_name, disease_tag, "INVOLVES", "Mechanism/Pathway", gene_symbol, "gene", source))
        lines.append(make_line(gene_name, "gene", "HAS SYNONYM", "Classification/Type", gene_symbol, "gene", source))

    # Parents
    for parent in packet.get('Parents', []):
        parent_label = parent['Parent'][0]['Label']
        parent_orpha = parent['Parent'][0]['ORPHAcode']
        lines.append(make_line(disease_name, disease_tag, "ISA", "Classification/Type", parent_label, "disease", source))
        more.append(parent_orpha)

    # Phenotypes
    for pheno in packet.get('Phenotypes', []):
        pheno_name = pheno['Phenotype']['HPOTerm']
        lines.append(make_line(disease_name, disease_tag, "HAS", "Containment/Component", pheno_name, "phenotype", source))

    # Prevalence
    for prev in packet.get('Prevalences', []):
        prevalence = f"{prev['Prevalence']['PrevalenceClass'].replace(' ', '')}; {prev['Prevalence']['PrevalenceGeographic']}"
        lines.append(make_line(disease_name, disease_tag, "HAS", "Containment/Component", prevalence, "feature", source))

    # Onset
    try:
        onset_field = packet.get('AverageAgeOfOnsets', {})
        if isinstance(onset_field, dict):  # dict: go inside
            onsets = onset_field.get('AverageAgeOfOnset', [])
            if isinstance(onsets, dict):
                onsets = [onsets]
        elif isinstance(onset_field, list):  # list: use directly
            onsets = onset_field
        else:
            onsets = []

        for onset in onsets:
            if isinstance(onset, dict) and 'value' in onset:
                onset_value = onset['value']
                lines.append(make_line(disease_name, disease_tag, "HAS", "Containment/Component", onset_value, "feature", source))

    except Exception as e:
        print(f"Error parsing AverageAgeOfOnsets for ORPHAcode {orpha_code}: {e}")




    # Inheritance
    # New robust way
    try:
        inheritances = packet.get('TypeOfInheritances', {}).get('TypeOfInheritance', [])
        if isinstance(inheritances, dict):
            inheritances = [inheritances]  # Wrap single dictionary into a list
        for inherit in inheritances:
            inherit_value = inherit['value']
            lines.append(make_line(disease_name, disease_tag, "HAS", "Containment/Component", inherit_value, "feature", source))
    except Exception as e:
        print(f"Error parsing TypeOfInheritances for ORPHAcode {orpha_code}: {e}")


    return lines, more


def parseProduct6(path: str, orpha_code: int):
    lines = []
    try:
        with open(path, 'rb') as file:
            root = ET.parse(file).getroot()
            date = (root.attrib['date'][:10]).replace('-', '/')
            source = f"OrphaData:{orpha_code}; {date}"

            for disorder in root.findall('.//Disorder'):
                code = disorder.find('OrphaCode')
                if code is not None and code.text == str(orpha_code):
                    disease_name = disorder.find('Name').text
                    for association in disorder.findall('.//DisorderGeneAssociation'):
                        try:
                            source_text = association.find('.//SourceOfValidation').text
                        except:
                            source_text = source

                        gene_section = association.find('Gene')
                        if gene_section is None:
                            continue

                        gene_name = gene_section.find('.//Name').text
                        gene_symbol = gene_section.find('.//Symbol').text

                        lines.append(make_line(disease_name, "disease", "INVOLVES", "Mechanism/Pathway", gene_name, "gene", source_text))
                        lines.append(make_line(gene_name, "gene", "HAS SYNONYM", "Classification/Type", gene_symbol, "gene", source_text))

                        for syn in gene_section.findall('.//Synonym'):
                            lines.append(make_line(gene_name, "gene", "HAS SYNONYM", "Classification/Type", syn.text, "gene", source_text))

                        for locus in gene_section.findall('.//GeneLocus'):
                            lines.append(make_line(gene_name, "gene", "LOCATED", "Location/Presence", locus.text, "location", source_text))
    except Exception as e:
        print(f"Error parsing product6 for ORPHAcode {orpha_code}: {e}")
    return lines


def parseFunctConsequence(path: str, orpha_code: int):
    lines = []
    try:
        with open(path, 'rb') as file:
            root = ET.parse(file).getroot()
            date = (root.attrib['date'][:10]).replace('-', '/')
            source = f"OrphaData:{orpha_code}; {date}"

            for disorder in root.findall('.//Disorder'):
                code = disorder.find('OrphaCode')
                if code is not None and code.text == str(orpha_code):
                    disease_name = disorder.find('Name').text
                    for d in disorder.findall('.//DisabilityDisorderAssociation'):
                        disability = d.find('Disability')
                        if disability is not None:
                            dis_name = disability.find('Name').text
                            lines.append(make_line(disease_name, "disease", "IMPACTS", "Condition/State", dis_name, "ability", source))
    except Exception as e:
        print(f"Error parsing functional consequences for ORPHAcode {orpha_code}: {e}")
    return lines


def make_line(entity1, tag1, relation, rel_tag, entity2, tag2, metadata):
    simple_sentence = f"{entity1} {relation} {entity2}"
    return {
        "relevant_text": simple_sentence,
        "simple_sentence": simple_sentence,
        "triple": (entity1, relation, entity2),
        "tagged_triple": (entity1, tag1, relation, rel_tag, entity2, tag2),
        "entity1": entity1,
        "tag1": tag1,
        "relationship": relation,
        "relationship_tag": rel_tag,
        "entity2": entity2,
        "tag2": tag2,
        "metadata": metadata
    }


def downloadFiles(orpha_code: int):
    try:
        if not os.path.exists('DATA'):
            os.makedirs('DATA')
    except OSError as e:
        print(f"Error creating DATA folder: {e}")

    orpha_url = f"https://raw.githubusercontent.com/Orphanet/orphapacket/refs/heads/master/json/ORPHApacket_{orpha_code}.json"
    prod6_url = "https://www.orphadata.com/data/xml/en_product6.xml"
    funct_url = "https://www.orphadata.com/data/xml/en_funct_consequences.xml"

    files_dict = {
        orpha_url: f"DATA/ORPHApacket_{orpha_code}.json",
        prod6_url: "DATA/en_product6.xml",
        funct_url: "DATA/en_funct_consequences.xml"
    }

    for url, filepath in files_dict.items():
        if os.path.exists(filepath):
            continue
        else:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                # NEW CHECK HERE: is it actually JSON?
                if "ORPHApacket" not in response.text and "Orphapacket" not in response.text:
                    print(f"⚠️ Invalid packet for ORPHAcode {orpha_code} (not proper JSON). Skipping.")
                    return None

                with open(filepath, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")
                return None

    return [f"DATA/ORPHApacket_{orpha_code}.json", "DATA/en_product6.xml", "DATA/en_funct_consequences.xml"]


def extractORPHA(orpha_code: int, log_file):
    all_lines = []
    files = downloadFiles(orpha_code)
    if files is None:
        log_file.write(f"Download failed for ORPHAcode {orpha_code}\n")
        return []

    try:
        packet_lines, more = parsePacket(files[0], orpha_code)
        all_lines.extend(packet_lines)
    except Exception as e:
        log_file.write(f"Error parsing packet for ORPHAcode {orpha_code}: {e}\n")

    try:
        prod6_lines = parseProduct6(files[1], orpha_code)
        all_lines.extend(prod6_lines)
    except Exception as e:
        log_file.write(f"Error parsing product6 for ORPHAcode {orpha_code}: {e}\n")

    try:
        funct_lines = parseFunctConsequence(files[2], orpha_code)
        all_lines.extend(funct_lines)
    except Exception as e:
        log_file.write(f"Error parsing functional consequence for ORPHAcode {orpha_code}: {e}\n")

    return all_lines



# if __name__ == "__main__":
#     start = time.time()

#     # Read ORPHA codes
#     df = pd.read_csv('ORPHAnomenclature_MasterFile_en_2024..xlsx - ICD10.csv')
#     unique_orphacodes = df['ORPHAcode'].dropna().unique()

#     all_lines = []

#     # Open log.txt for writing
#     with open("log.txt", "w", encoding="utf-8") as log_file:

#         # LIMIT to first 5 codes for testing
#         for idx, code in enumerate(unique_orphacodes):
#             if idx >= 5:
#                 break
#             try:
#                 code_int = int(code)
#                 print(f"Extracting for ORPHAcode {code_int}...")
#                 triples = extractORPHA(code_int, log_file)
#                 if triples:
#                     all_lines.extend(triples)
#             except Exception as e:
#                 log_file.write(f"General error for ORPHAcode {code}: {e}\n")

#     # Write OUTPUT.csv
#     if all_lines:
#         with open("final_orphapacket_jsons.csv", "w", newline="", encoding="utf-8") as file:
#             writer = csv.writer(file)
#             writer.writerow([
#                 "Relevant Text", "Simple Sentences", "Triple", "Tagged Triple",
#                 "Entity 1", "Tag 1", "Relationship", "Relationship Tag",
#                 "Entity 2", "Tag 2", "MetaData"
#             ])

#             for triple in all_lines:
#                 writer.writerow([
#                     triple["relevant_text"],
#                     triple["simple_sentence"],
#                     f"({triple['triple'][0]}, {triple['triple'][1]}, {triple['triple'][2]})",
#                     f"({triple['entity1']} ({triple['tag1']}), {triple['relationship']} ({triple['relationship_tag']}), {triple['entity2']} ({triple['tag2']}))",
#                     triple["entity1"], triple["tag1"],
#                     triple["relationship"], triple["relationship_tag"],
#                     triple["entity2"], triple["tag2"],
#                     triple["metadata"]
#                 ])
#         print(f"\n✅ Saved all triples into OUTPUT.csv ({len(all_lines)} rows) in {time.time() - start:.2f} seconds.")
#     else:
#         print("\n⚠️ No data extracted.")

if __name__ == "__main__":
    start = time.time()

    # Read ORPHA codes
    df = pd.read_csv('ORPHAnomenclature_MasterFile_en_2024..xlsx - ICD10.csv')
    unique_orphacodes = df['ORPHAcode'].dropna().unique()

    all_lines = []

    # Open log.txt for writing
    with open("log.txt", "w", encoding="utf-8") as log_file:

        # No limit now: run for all ORPHA codes
        for code in unique_orphacodes:
            try:
                code_int = int(code)
                print(f"Extracting for ORPHAcode {code_int}...")
                triples = extractORPHA(code_int, log_file)
                if triples:
                    all_lines.extend(triples)
            except Exception as e:
                log_file.write(f"General error for ORPHAcode {code}: {e}\n")

    # Write OUTPUT.csv
    if all_lines:
        with open("final_orphapacket_jsons.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Relevant Text", "Simple Sentences", "Triple", "Tagged Triple",
                "Entity 1", "Tag 1", "Relationship", "Relationship Tag",
                "Entity 2", "Tag 2", "MetaData"
            ])

            for triple in all_lines:
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
        print(f"\n✅ Saved all triples into final_orphapacket_jsons.csv ({len(all_lines)} rows) in {time.time() - start:.2f} seconds.")
    else:
        print("\n⚠️ No data extracted.")
