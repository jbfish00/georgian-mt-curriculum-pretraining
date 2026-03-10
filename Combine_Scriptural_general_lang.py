import json
from pathlib import Path
from typing import List, Dict, Any
import os
import pandas as pd
import random
from datasets import load_dataset, Dataset, concatenate_datasets

# ------------------------------------------------------
# COMBINING SCRIPTURE AND GENERAL
#-------------------------------------------------------
def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Load a JSON file and return a list of parallel-sentence dictionaries.
    Handles both array-of-objects and object-with-numeric-keys formats.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # If it's a direct list → already good
    if isinstance(data, list):
        return data
    
    # If it's an object with numeric keys (sometimes seen in scripture dumps)
    if isinstance(data, dict):
        # Sort keys to have a deterministic order (optional but nice)
        sorted_items = sorted(data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0])
        return [item for _key, item in sorted_items]
    
    raise ValueError(f"Unexpected JSON structure in {filepath}")

def combine_parallel_corpora(file1: str, file2: str, output_file: str):
    """
    Combine two Georgian↔English parallel JSON files into one.
    All fields are preserved; duplicates are not removed (you can add deduplication if needed).
    """
    # Load both files
    data1 = load_json_file(file1)
    data2 = load_json_file(file2)
    
    # Verify that every entry has 'en' and 'ka' (safety check)
    for i, entry in enumerate(data1 + data2):
        if not isinstance(entry, dict) or 'en' not in entry or 'ka' not in entry:
            print(f"Warning: Entry {i} is missing 'en' or 'ka': {entry}")
    
    # Combine
    combined = data1 + data2
    
    # Write out pretty-printed JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully combined {len(data1)} + {len(data2)} = {len(combined)} sentences.")
    print(f"Output written to: {output_file}")

# ------------------------------------------------------------------
# Usage
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Adjust the paths to match your actual filenames
    combine_parallel_corpora(
        file1="GENERAL_LDS_LANG.json",
        file2="SCRIPTURAL_LANG_DO_NOT_EDIT.json",
        output_file="COMBINED_GE_EN.json"
    )

