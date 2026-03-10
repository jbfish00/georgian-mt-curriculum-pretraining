# translate_unsloth_final.py
# Uses Unsloth's FastLanguageModel — the ONLY way to load your Unsloth-trained LoRAs
import json
import pandas as pd
from unsloth import FastLanguageModel
from tqdm import tqdm

# ===================== CONFIG =====================
TEST_FILE = "Data/splits/test_paired.jsonl"
MODEL_DIR = "models"

MODEL_FOLDERS = {
    "mixed":         "models/mixed_final",
    "chronological": "models/chron_final",
    "reverse":       "models/rev_final",
}

NUM_LINES = 50
# ==================================================

print("Loading test data...")
with open(TEST_FILE, "r", encoding="utf-8") as f:
    lines = [json.loads(line) for line in f.readlines()[:NUM_LINES]]
test_df = pd.DataFrame(lines)
print(f"Loaded {len(test_df)} examples")

def make_prompt(text):
    return f"Translate English to Georgian:\n{text}\n###\n"

inputs = [make_prompt(ex["en"]) for ex in lines]

results = {"src_en": test_df["en"].tolist(), "ref_ka": test_df["ka"].tolist()}

for name, folder in MODEL_FOLDERS.items():
    print(f"\n{'='*80}")
    print(f"TRANSLATING WITH {name.upper()}")
    print(f"{'='*80}")
    
    # This is the ONLY line that works with your Unsloth-trained LoRAs
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = folder,           # Your local *_final folder
        max_seq_length = 2048,
        dtype = None,                  # Auto
        load_in_4bit = True,
    )
    
    FastLanguageModel.for_inference(model)
    
    preds = []
    for prompt in tqdm(inputs, desc="Generating"):
        inputs_tok = tokenizer(prompt, return_tensors="pt").to("cuda")
        output = model.generate(**inputs_tok, max_new_tokens=256, do_sample=False)
        text = tokenizer.decode(output[0], skip_special_tokens=True)
        pred = text.split("###\n")[-1].strip() if "###\n" in text else text[len(prompt):].strip()
        preds.append(pred)
    
    results[f"{name}_pred"] = preds
    pd.DataFrame({"src_en": test_df["en"], "ref_ka": test_df["ka"], "pred_ka": preds}).to_csv(f"{name}_50.csv", index=False)
    print(f"Saved {name}_50.csv")

pd.DataFrame(results).to_csv("all_50_translations.csv", index=False)
print("\nSUCCESS! All translations saved using your exact trained models.")