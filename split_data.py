#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import random
from pathlib import Path

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
DATA_DIR   = Path(os.getcwd()) / "Data"
SPLIT_DIR  = DATA_DIR / "splits"
SPLIT_DIR.mkdir(parents=True, exist_ok=True)

# Input files
PAIRED_FILE      = DATA_DIR / "COMBINED_GE_EN.json"
OLD_GEO_FILE     = DATA_DIR / "old_geo_clean.txt"
MIDDLE_GEO_FILE  = DATA_DIR / "middle_geo_clean.txt"

# Split sizes
TEST_SIZE      = 5_000
VAL_SIZE       = 5_000
MLM_VAL_SIZE   = 1_000          # optional monitor for MLM
RANDOM_SEED    = 42

# ------------------------------------------------------------------
# Helper writers
# ------------------------------------------------------------------
def save_jsonl(records: list, path: Path) -> None:
    """One JSON object per line (JSONL)."""
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def save_txt(lines: list, path: Path) -> None:
    """Plain-text, one sentence per line."""
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def copy_full(src: Path, dst: Path) -> None:
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

# ------------------------------------------------------------------
# 1. Load paired data
# ------------------------------------------------------------------
with PAIRED_FILE.open("r", encoding="utf-8") as f:
    paired = json.load(f)                     # list[dict{"en":..., "ka":...}]

print(f"Loaded {len(paired):,} parallel sentences.")

ka_sentences = [ex["ka"] for ex in paired]
en_sentences = [ex["en"] for ex in paired]

# ------------------------------------------------------------------
# 2. Random, reproducible indices
# ------------------------------------------------------------------
indices = list(range(len(paired)))
rng = random.Random(RANDOM_SEED)
rng.shuffle(indices)

test_idx  = indices[:TEST_SIZE]
val_idx   = indices[TEST_SIZE: TEST_SIZE + VAL_SIZE]
train_idx = indices[TEST_SIZE + VAL_SIZE:]          # ~95 k

# ------------------------------------------------------------------
# 3. MLM validation (1 k) – taken **from** the train pool
# ------------------------------------------------------------------
mlm_val_idx   = train_idx[:MLM_VAL_SIZE]
mlm_train_idx = train_idx[MLM_VAL_SIZE:]

# ------------------------------------------------------------------
# 4. Write everything
# ------------------------------------------------------------------
# ---- Translation (paired) splits ----
save_jsonl([paired[i] for i in train_idx], SPLIT_DIR / "train_paired.jsonl")
save_jsonl([paired[i] for i in val_idx],  SPLIT_DIR / "val_paired.jsonl")
save_jsonl([paired[i] for i in test_idx], SPLIT_DIR / "test_paired.jsonl")

# ---- Monolingual Modern Georgian (MLM) ----
save_txt([ka_sentences[i] for i in mlm_train_idx], SPLIT_DIR / "train_modern_geo.txt")
save_txt([ka_sentences[i] for i in mlm_val_idx],   SPLIT_DIR / "val_mlm_modern_geo.txt")
save_txt([ka_sentences[i] for i in val_idx],      SPLIT_DIR / "val_modern_geo.txt")   # optional, for reporting
save_txt([ka_sentences[i] for i in test_idx],     SPLIT_DIR / "test_modern_geo.txt")  # optional

# ---- Historical monolingual (full, no split) ----
copy_full(OLD_GEO_FILE,    SPLIT_DIR / "train_old_geo.txt")
copy_full(MIDDLE_GEO_FILE, SPLIT_DIR / "train_middle_geo.txt")

# ------------------------------------------------------------------
# 5. Summary
# ------------------------------------------------------------------
def linecount(p: Path) -> int:
    return sum(1 for _ in p.open("r", encoding="utf-8"))

print("\n" + "="*70)
print("SPLIT SUMMARY (LLaMA-ready)")
print("="*70)
print(f"Translation train   : {len(train_idx):,}  → train_paired.jsonl")
print(f"Translation val     : {VAL_SIZE:,}      → val_paired.jsonl")
print(f"Translation test    : {TEST_SIZE:,}     → test_paired.jsonl")
print(f"MLM train (modern)  : {len(mlm_train_idx):,} → train_modern_geo.txt")
print(f"MLM val   (modern)  : {MLM_VAL_SIZE:,}    → val_mlm_modern_geo.txt")
print(f"Old Georgian (full) : {linecount(OLD_GEO_FILE):,} → train_old_geo.txt")
print(f"Middle Georgian(full): {linecount(MIDDLE_GEO_FILE):,} → train_middle_geo.txt")
print("\nAll files are **JSONL** (paired) or **plain-text** (mono).")
print("Ready for:")
print("  1. Continued pre-training (MLM) on old → middle → modern")
print("  2. Fine-tuning on train_paired.jsonl")
print("="*70)