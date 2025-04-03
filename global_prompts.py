global_output_max_new_tokens = 512 #2048

pick_unique_sentences = """"""

llm_judge_prompt2 = """You are an expert in natural language processing. Given an extracted entity-relation triple from it, your task is to:
                                1. Evaluate the **Relevance** of the triple to understanding the disease ***GNE Myopathy***.
                                2. Assess the **Tag and Relationship Accuracy** to determine if the triple makes logical sense and if the entity tags are appropriate.
                                3. Assign a score from 1 to 5 based on these criteria

                                Use a scoring scale from 1 to 5, where:
                                - **5**: Highly relevant and correct
                                - **4**: Mostly relevant and correct with minor issues
                                - **3**: Somewhat relevant or partially correct
                                - **2**: Poorly relevant or mostly incorrect
                                - **1**: Completely irrelevant or incorrect

                                The final output or response with only be the numerical score.
                    """

llm_judge_prompt = """-Goal-
                            Given a context sentence and a tagged triplet, assess the relevance of each entity, relationship, and tag to GNE myopathy. Rate the overall relevance on a scale from 1 to 5, where 5 indicates high relevance and 1 indicates low relevance.

                            Relevance should be determined by the importance of the entity or relationship in understanding GNE myopathy within medical and biological contexts. Consider factors such as disease symptoms, affected body parts, biological markers, diagnostic and treatment methods, and research on the disease.

                            -Tagging Categories-
                            Entities in the triplet should fall under one of the following categories:
                            "location", "institute", "cell component", "disease", "body part", "enzyme", "biological process", "sample", "population group", "treatment", "symptom", "protein", "gene", "pathway", "mutation", "diagnostic procedure", "drug", "feature", "model", "chemical", "time period", "observation", "role".

                            -Steps-
                            1. Review the context sentence and the triplet to understand the relationship and entities in the context of GNE myopathy.
                            2. Verify that the two entities of the triplet are correctly tagged based on the provided categories, ensuring that each term accurately reflects its role within the context of sentence and GNE myopathy.
                            3. Assign a relevance score from 1 to 5 based on three criteria: (1) the relevance of the triplet to GNE myopathy, (2) the clarity and appropriateness of the meanings in the context sentence, and (3) the accuracy of the tagging for each term.

                            -Output Format-
                            Numerical score 

                            ################
                            -Examples-
                            ################

                            Example Input:
                            "Patients with GNE myopathy often experience scapular weakness, a common feature associated with the progression of this disease. -(GNE Myopathy (disease), HAS FEATURE, Scapular weakness (symptom))"

                            Expected Output:
                            5 

                            Example Input: 
                            "The introduction of new research highlights the significance of the GNE gene in muscle disorders. -(Introduction (feature), PRESENT IN, the GNE gene (gene))"

                            Expected Output: 
                            2 
"""



tagging_triples_prompt_with_relevant_sentences = """-Goal-
                                Given a context sentence and a triplet extracted from it, categorize the first and third terms based on the following categories and add the category in parentheses next to each term.

                                Possible categories include:
                                "location", "institute", "cell component", "disease", "body part", "enzyme", "biological process", "sample", "population group", "treatment", "symptom", "protein", "gene", "pathway", "mutation", "diagnostic procedure", "drug", "feature", "model", "chemical", "time period", "observation" and "role"
                                
                                Donot include entities that can fall in these categories:
                                "email", "author"
                                
                                -Steps-
                                1. Identify the first and third terms in the triplet present after - of the context sentence  
                                
                                2. Determine the appropriate category for each entity based on its meaning in the context sentence, using the provided category list.

                                2. Format the triplet by appending each terms category in parentheses immediately following the term.

                                -Output Format-
                                Display each triplet in the format:
                                (first term (category), relationship, third term (category))

                                ################
                                -Examples-
                                ################

                                Example Input:
                                "Patients with GNE myopathy often experience scapular weakness, a common feature associated with the progression of this disease.  - GNE Myopathy, HAS FEATURE, Scapular weakness"

                                Expected Output:
                                (GNE Myopathy (disease), HAS FEATURE, Scapular weakness (symptom))


"""


tagging_triples_prompt = """-Goal-
                                Given a triplet, categorize the first and third terms based on the following categories and add the category in parentheses next to each term.

                                Possible categories include:
                                "location", "institute", "cell component",  "disease", "body part", "enzyme", "biological process", "sample", "population group", "treatment", "symptom", "protein", "gene", "pathway", "mutation", "diagnostic procedure", "drug", "feature", "model", "chemical", "time period", "observation" and "role"
                                
                                Donot include entities that can fall in these categories:
                                "email", "author"
                                
                                -Steps-
                                1. Identify the first and third terms in the triplet and assign the appropriate category from the provided list.

                                2. Format the triplet by appending each terms category in parentheses immediately following the term.

                                -Output Format-
                                Display each triplet in the format:
                                (first term (category), relationship, third term (category))

                                ################
                                -Examples-
                                ################

                                Example Input:
                                "GNE Myopathy, HAS FEATURE, Scapular weakness"

                                Expected Output:
                                (GNE Myopathy (disease), HAS FEATURE, Scapular weakness (symptom))


"""


triplets_from_simple_sentence_prompt = """-Goal-
                                            Given a complex sentence, extract all entity pair relation triples from it. Each extracted triples should consist of two related entities and describe their relationship. 
                                            Only use information from the given text.
            
                                            -Steps-

                                            Extract Entities: From the given sentence, identify relevant entities. Ensure each extracted entity retains the original context and meaning.

                                            entity_1: The first related entity.
                                            entity_2: The second related entity.
                                            Formulate Relationships: For each pair of related entities, define a one or two word phrase that describes their relationship while retaining the original context and meaning.

                                            relationship_description: One-two word explanation of how entity_1 and entity_2 are related.
                                            Output Format: Return the extracted entity pair relations in a list format, ensuring each relation conveys the original meaning.

                                            Donot generate multiple entity1-relation-entity2 triples with the same meaning.

                                            Use a new line as the list delimiter. Only output the triples as response in this format and nothing else.

                                            ################
                                            -Examples-
                                            ################

                                            Example Input:
                                            "Mutations in the GNE gene lead to GNE Myopathy, which affects muscle function and causes progressive weakness."

                                            Expected Output:
                                            (Mutations in the GNE gene, LEAD TO, GNE Myopathy)
                                            (GNE Myopathy, AFFECTS, muscle function)
                                            (GNE Myopathy, CAUSES, progressive weakness)

                                            Example Input:
                                            "Onset in proximal leg muscles in GNE Myopathy can mimic an unusual pattern of limb girdle muscular dystrophy."

                                            Expected Output:
                                            (Onset in proximal leg muscles, PRESENT IN, GNE Myopathy)
                                            (Onset in proximal leg muscles, MIMICS, limb girdle muscular dystrophy)
                                            (Unusual pattern, PRESENT IN, limb girdle muscular dystrophy)
                                            
                                            Example Input:
                                            "T1 values of calf muscles in GNE myopathy decreased with the gradual aggravation of fat infiltration."

                                            Expected Output:
                                            (T1 values, MEASURED IN, calf muscles)
                                            (T1 values of calf muscles, PRESENT IN, GNE myopathy)
                                            (calf muscles in GNE myopathy, HAS, gradual aggravation of fat infiltration)
                                            (T1 values of calf muscles, DECREASE WITH, gradual aggravation of fat infiltration)


                                            Example Input:
                                            "ERp72 has no positive staining in cytoplasm of GNE myopathy muscle fibers."

                                            Expected Output:
                                            (ERp72, HAS, no positive staining)
                                            (no positive staining, LOCATED IN, cytoplasm)
                                            (cytoplasm, PART OF, GNE myopathy muscle fibers)

"""




simple_sentence_prompt = """-Goal-
                                Given a complex sentence, extract smaller, meaningful sentences that convey the same meaning as the original. Each extracted sentence should consist of two related entities and describe their relationship. Only use information from the given text. 
                                Avoid generating sentences with the same meaning.

                                -Steps-

                                Extract Entities: From the given complex sentence, identify all relevant entities. Ensure each extracted entity retains the original context and meaning.
                                entity_1: The first related entity.
                                entity_2: The second related entity.

                                Formulate Relationships: For each pair of related entities, create a meaningful sentence that describes their relationship which retains the original context and meaning.
                                relationship_description: A brief explanation of how entity_1 and entity_2 are related.

                                Output Format: Return the extracted sentences in a list format, ensuring each sentence conveys the original meaning.

                                Use a new line as the list delimiter. Only output the response in this format and nothing else.
                                ################
                                -Examples-
                                ################

                                Example Input:
                                "The progression of GNE myopathy is influenced by genetic factors, while environmental factors contribute to the variability of symptoms observed in affected individuals."

                                Expected Output:

                                ("The progression of GNE myopathy is influenced by genetic factors.")
                                ("Environmental factors contribute to the variability of symptoms in affected individuals.")
                                ("Symptoms in affected individuals vary due to environmental factors.")

"""






#"Given a complex sentence, extract smaller, meaningful sentences that each convey the same meaning as the original. Each extracted sentence should consist of two related entities and describe their relationship. Ensure the original context and meaning are preserved in these simpler sentences. Donot produce extra irrelevant sentences apart from the simple sentences."



# ssimple_sentence_prompt = """Given the following input text, identify sentences from there that are directly relevant to 'GNE myopathy' only. 
#                             Extract only the sentences or portions of sentences that contain important information about GNE myopathy, 
#                             such as its causes, symptoms, biological processes, treatment considerations, or any other facts unique to this condition. 
#                             Simplify each extracted sentence into clear, concise language that emphasizes the core idea. 
#                             Format each simplified sentence separately within brackets, ensuring that each conveys a complete thought and stands alone as a meaningful statement about GNE myopathy. 
#                             Exclude unrelated information that does not directly inform about GNE myopathy.
                            
#                             ######
#                             Example input: Input Text: "The progression of GNE myopathy and the contribution of genetic and environmental factors to its variability need to be further delineated. 
#                             PATHOLOGICAL FEATURES of GNE myopathy include ‘rimmed’ vacuoles, aggregation of various proteins, and fiber size variation. 
#                             ‘Rimmed’ vacuoles are recognized as small empty spaces surrounded by tiny red granules in the cytoplasm of muscle fibers typically on modified Gomori trichrome (mGT) staining. 
#                             Although this empty space is called “vacuole”, this is a space artificially produced during staining procedures. 
#                             The area was originally occupied mostly by red-colored granules, but they become detached from slide glass."
#                             Output: "(The progression of GNE myopathy and the role of genetic and environmental factors require further investigation.) (Pathological features of GNE myopathy include rimmed vacuoles, protein aggregation, and fiber size variation.)"
#                             """
# simple_sentence_prompt = "From the following text, identify and extract sentences that contain any of the keywords: 'GNE myopathy,' 'myopathy,' or 'GNE.' Ensure that each extracted sentence provides relevant information about these terms. Format each identified sentence within brackets for clarity, and avoid including unrelated content."
# # "Extract all meaningful sentences related to GNE myopathy only from the provided text. Include any information, whether direct or indirect, that contributes to understanding GNE myopathy."