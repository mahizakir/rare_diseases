import subprocess
import os
import sys

# Disease name
disease_name = "Zimmermann-Laband syndrome" #"Mabry syndrome" #"Endocrine-cerebro-osteodysplasia syndrome"

# Parent folder path
parent_folder = os.path.dirname(os.path.abspath(__file__))

# Define script execution order
script_order = [
    "1_keyword_based_line_extraction/1_keyword_based_line_extraction.py",
    "2_llm_simple_sentence_generator/2_llm_simple_sentence_generator.py",
    "3_llm_triples_generator_from_simple_sentences/3_llm_triples_generator_from_simple_sentences.py",
    "4_format_and_find_unique_generated_triples_per_paper_metadata/4_format_and_find_unique_generated_triples_per_paper_metadata.py",
    "5_llm_triple_tagger_with_context/5_llm_triple_tagger_with_context.py",
    "6_fix_metadata/6_fix_metadata.py",
    "7_classify_relations_and_cleaning/7_classify_relations_and_cleaning.py",
]

# Run each script in its respective folder
for script in script_order:
    script_path = os.path.join(parent_folder, script)
    script_folder = os.path.dirname(script_path)  # Get the script's folder

    print(f"\n>>> Running {script}...\n")

    # Run the script with real-time output
    process = subprocess.Popen(
        ["python", script_path, disease_name],
        cwd=script_folder,  # Set working directory
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Stream the output in real-time
    for line in process.stdout:
        print(line, end="")  # Print each line as it appears

    # Capture the stderr and suppress unwanted logs
    stderr_output = process.stderr.read()
    filtered_stderr = [line for line in stderr_output.splitlines() if "slow image processor" not in line]
    for error_line in filtered_stderr:
        print(f"ERROR: {error_line}")

    # Wait for process to finish
    process.wait()

    # Stop execution if there's an error
    if process.returncode != 0:
        break
