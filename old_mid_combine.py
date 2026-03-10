import os
from pathlib import Path

def combine_files(input_folder: str, output_folder: str, old_files: list, middle_files: list):
    """
    Combine specified Old and Middle Georgian text files into two separate output files.
    Preserves all content by concatenating with newlines between files.
    """
    # Ensure output folder exists
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Combine Old Georgian files
    old_output = output_path / "old_geo.txt"
    with open(old_output, 'w', encoding='utf-8') as outfile:
        for fname in old_files:
            input_file = Path(input_folder) / fname
            if input_file.exists():
                with open(input_file, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()  # Strip trailing whitespace
                    outfile.write(content + '\n\n')  # Add separator between files
            else:
                print(f"Warning: File {input_file} not found.")
    
    # Combine Middle Georgian files
    middle_output = output_path / "middle_geo.txt"
    with open(middle_output, 'w', encoding='utf-8') as outfile:
        for fname in middle_files:
            input_file = Path(input_folder) / fname
            if input_file.exists():
                with open(input_file, 'r', encoding='utf-8') as infile:
                    content = infile.read().strip()
                    outfile.write(content + '\n\n')
            else:
                print(f"Warning: File {input_file} not found.")
    
    print(f"Combined Old Georgian into: {old_output}")
    print(f"Combined Middle Georgian into: {middle_output}")

# ------------------------------------------------------------------
# Usage
# ------------------------------------------------------------------
if __name__ == "__main__":
    input_folder = "titus_corpus_lines"  # Adjust if path is different
    
    old_files = [
        "old_georgian_hagi_vol1.txt",
        "old_georgian_hagi_vol2.txt",
        "old_georgian_hagi_vol3.txt",
        "old_georgian_hagi_vol4.txt",
        "old_georgian_hagi_vol5.txt",
        "old_georgian_hagi_vol6.txt",
        "old_georgian_inscr.txt",
        "old_georgian_bible_mcx.txt"
    ]
    
    middle_files = [
        "middle_georgian_omainiani.txt",
        "middle_georgian_aleksiani.txt",
        "middle_georgian_visramiani.txt",
        "middle_georgian_arcil_visr.txt"
    ]
    
    output_folder = os.path.join(os.getcwd(), "Data")  # ./Data in current working directory
    
    combine_files(input_folder, output_folder, old_files, middle_files)