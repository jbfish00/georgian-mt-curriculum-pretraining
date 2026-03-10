# Transfer Learning from Historical Monolingual Data for Low-Resource MT: A Case Study of Georgian

**Course:** CS 479 — BYU
**Author:** Jacob B. Fisher

---

## Overview

This project investigates whether the **order** in which historical monolingual data is presented during continued pretraining of a large language model (LLM) affects the quality of machine translation (MT) for a low-resource language — specifically **English → Modern Georgian**.

Four variants of **LLaMA 3.2-3B** are trained and compared:

| Model | Description |
|---|---|
| **Baseline** | Supervised fine-tuning (SFT) for MT only — no historical pretraining |
| **Mixed** | Continued pretraining on shuffled historical + modern Georgian, then SFT |
| **Chronological** | Continued pretraining Old → Middle → Modern Georgian (epoch-wise), then SFT |
| **Reverse** | Continued pretraining Modern → Middle → Old Georgian (epoch-wise), then SFT |

The core research question draws from **curriculum learning**: does presenting a model with language data in a structured, chronological order improve its downstream translation ability more than random ordering or no historical pretraining at all?

**Key result:** Chronological ordering produced the best COMET score (36.31) and best human evaluation (MTEval 3.24), while Reverse ordering unexpectedly achieved the highest BLEU (0.86). All models produced low-quality translations overall, as LLaMA 3.2-3B has essentially no Georgian in its original pretraining data and the compute budget was limited.

---

## Results Summary

| Model | BLEU ↑ | COMET ↑ | MTEval ↓ |
|---|---|---|---|
| Baseline | 0.05 | 30.06 | 3.99 |
| Mixed | 0.40 | 34.54 | 3.65 |
| **Chronological** | 0.41 | **36.31** | **3.24** |
| Reverse | **0.86** | 34.76 | 3.55 |

- **BLEU** and **COMET**: higher is better.
- **MTEval** (human evaluation): lower is better.

Pretrained models all produced actual Georgian script output; the Baseline produced Georgian-looking Latin-script gibberish, indicating continued pretraining meaningfully bootstrapped script acquisition.

---

## Background & Motivation

**Georgian** is a morphologically rich, low-resource language with a unique script (Mkhedruli, Unicode U+10D0–U+10FF) that presents significant challenges for NMT systems:
- Limited parallel data with English
- Agglutinative morphology (complex word structure)
- Unique script not well-represented in most LLM pretraining corpora

**Curriculum learning** in NLP has shown that structured data ordering can accelerate convergence and improve transfer learning. This project applies that idea to the *diachronic* (across time) dimension of Georgian, leveraging historical texts spanning 15 centuries:
- **Old Georgian** (5th–11th centuries): hagiographic, biblical, inscriptional texts
- **Middle Georgian** (12th–18th centuries): literary and poetic texts
- **Modern Georgian** (19th century onward): contemporary religious and general texts

---

## Repository Structure

```
.
├── README.md
├── .gitignore
│
├── ── Data Pipeline Scripts ──
├── titus_scrape.py                  # Web scraper for TITUS historical corpus
├── old_mid_combine.py               # Combines scraped corpus files by era
├── old_middle_clean.py              # Cleans & normalizes historical Georgian text
├── Combine_Scriptural_general_lang.py  # Merges LDS parallel corpora JSON files
├── split_data.py                    # Splits parallel corpus into train/val/test
├── model_translations.py            # Inference: runs all 4 LoRA models on test set
│
├── ── Corpus (small files included) ──
├── titus_corpus/                    # Raw scraped TITUS text files (~8.6 MB)
│   ├── old_georgian_hagi_vol1.txt   # Old Georgian hagiography vol. 1 (1.7 MB)
│   ├── old_georgian_hagi_vol2.txt   # vol. 2 (1.0 MB)
│   ├── old_georgian_hagi_vol3.txt   # vol. 3 (1.1 MB)
│   ├── old_georgian_hagi_vol4.txt   # vol. 4 (445 KB)
│   ├── old_georgian_hagi_vol5.txt   # vol. 5 (663 KB)
│   ├── old_georgian_hagi_vol6.txt   # vol. 6 (2.0 MB)
│   ├── old_georgian_bible_mcx.txt   # Old Georgian Bible excerpts (11 KB)
│   ├── old_georgian_inscr.txt       # Old Georgian inscriptions (121 KB)
│   ├── middle_georgian_visramiani.txt     # Middle Georgian prose (1.2 MB)
│   ├── middle_georgian_arcil_visr.txt     # Arcil's Visramiani (146 KB)
│   ├── middle_georgian_omainiani.txt      # Omainiani (365 KB)
│   └── middle_georgian_aleksiani.txt      # Aleksiani (1.8 KB)
│
├── titus_corpus_lines/              # Same texts split into individual lines (~17 MB)
│
├── Data/
│   ├── old_geo.txt                  # Raw combined Old Georgian text (15 MB)
│   ├── old_geo_clean.txt            # Cleaned Old Georgian (15 MB)
│   ├── middle_geo.txt               # Raw combined Middle Georgian (2.4 MB)
│   ├── middle_geo_clean.txt         # Cleaned Middle Georgian (2.4 MB)
│   └── splits/
│       ├── val_paired.jsonl         # Validation set — 5,000 EN↔KA pairs (2.7 MB)
│       ├── test_paired.jsonl        # Test set — 5,000 EN↔KA pairs (2.7 MB)
│       ├── val_modern_geo.txt       # Modern Georgian validation sentences (1.8 MB)
│       ├── test_modern_geo.txt      # Modern Georgian test sentences (1.8 MB)
│       ├── val_mlm_modern_geo.txt   # MLM validation subset — 1,000 sentences (377 KB)
│       ├── train_old_geo.txt        # Old Georgian for pretraining (15 MB)
│       └── train_middle_geo.txt     # Middle Georgian for pretraining (2.4 MB)
│       # train_paired.jsonl         — gitignored (77 MB)
│       # train_modern_geo.txt       — gitignored (51 MB)
│
├── models/
│   ├── baseline_sft_final/          # Baseline LoRA adapter
│   │   ├── adapter_config.json
│   │   ├── chat_template.jinja
│   │   ├── tokenizer_config.json
│   │   ├── special_tokens_map.json
│   │   └── README.md
│   ├── chron_sft_final/             # Chronological LoRA adapter (same structure)
│   ├── mixed_sft_final/             # Mixed LoRA adapter (same structure)
│   └── rev_sft_final/               # Reverse LoRA adapter (same structure)
│   # adapter_model.safetensors files — gitignored (36 MB each)
│   # tokenizer.json files           — gitignored (17 MB each)
│
├── Evaluation/
│   ├── Average_score.xlsx           # Aggregated metric scores
│   ├── Human_Eval_Jacob.tsv         # Human evaluation annotations
│   ├── results (1).tsv              # Evaluation results (evaluator 1)
│   └── results (2).tsv              # Evaluation results (evaluator 2)
│
├── all_models_50_translations.csv   # 50-sentence translations from all 4 models (25 KB)
│
└── Turn-in Folder/
    ├── CS479_Final_Paper.pdf        # Full research paper (90 KB)
    ├── Copy of Final_Llama_Pre-training_Fine-tuning.ipynb  # Google Colab notebook (393 KB)
    ├── Instructions.txt             # Setup instructions for running the notebook
    ├── Time Log Template.xlsx       # Project time log
    └── full_test_predictions_all_models.csv  # Full test-set predictions, all models (5.2 MB)
    # LLaMA_project demo.mp4        — gitignored (386 MB)
    # Model folders & train splits  — gitignored (duplicates of above)
```

---

## Methodology

### Phase 1: Data Collection & Preprocessing

#### 1a. Scraping Historical Georgian Texts (`titus_scrape.py`)

The **TITUS corpus** (Thesaurus Indogermanischer Text- und Sprachmaterialien, Goethe University Frankfurt) contains digitized historical Georgian texts. The scraper:

- Crawls TITUS HTML pages bidirectionally from seed URLs using `requests` + `BeautifulSoup`
- Extracts and normalizes the Georgian script:
  - **Asomtavruli / Mtavruli** (uppercase ecclesiastical) → **Mkhedruli** (modern script)
  - **Nuskhuri** (small ecclesiastical) → **Mkhedruli**
- Removes TITUS metadata, manuscript editorial symbols, line numbers, and headers
- Splits text into sentences (on `.`) or keeps full lines; filters segments < 3 words
- Outputs separate files per sub-corpus (hagiography vols 1–6, Bible, inscriptions, and four Middle Georgian works)

**Old Georgian sources:** 6 volumes of hagiography, Old Georgian Bible (Mariam Chetatatini version), inscriptions
**Middle Georgian sources:** Visramiani (12th c. prose), Arcil's Visramiani, Omainiani, Aleksiani

#### 1b. Combining Corpus Files (`old_mid_combine.py`)

Concatenates the per-work TITUS files into two era-level files:
- `Data/old_geo.txt` — all Old Georgian texts
- `Data/middle_geo.txt` — all Middle Georgian texts

#### 1c. Cleaning Historical Text (`old_middle_clean.py`)

Applies final normalization to the combined era files:
- Preserves **all Georgian letters** including archaic characters (ჲ ჱ ჳ ჴ ჵ ჶ ჷ ჸ ჹ ჺ)
- Removes remaining manuscript editorial symbols (`^`, `*`, `§`, `†`, `‡`, `¶`, `•`, etc.)
- Inserts newlines after sentence terminators (`. ? !`) when followed by a Georgian letter
- Splits long strings on the 3rd+ occurrence of standalone **და** (Georgian conjunction "and")
- Outputs `old_geo_clean.txt` and `middle_geo_clean.txt`

#### 1d. Building the Parallel Corpus (`Combine_Scriptural_general_lang.py`)

Merges two English ↔ Georgian parallel JSON corpora from The Church of Jesus Christ of Latter-day Saints translation memories:
- `GENERAL_LDS_LANG.json` — modern Georgian general religious text (~63 MB)
- `SCRIPTURAL_LANG_DO_NOT_EDIT.json` — scriptural/biblical Georgian (~23 MB)

Both files use `{"en": "...", "ka": "..."}` record format. The script handles both JSON array and object-with-numeric-keys formats, validates all entries, and outputs `Data/COMBINED_GE_EN.json` (~100,000 sentence pairs total).

#### 1e. Train/Val/Test Splitting (`split_data.py`)

Splits the combined parallel corpus reproducibly (seed 42):

| Split | Size | Files |
|---|---|---|
| Test | 5,000 pairs | `test_paired.jsonl`, `test_modern_geo.txt` |
| Validation | 5,000 pairs | `val_paired.jsonl`, `val_modern_geo.txt` |
| MLM Validation | 1,000 sentences | `val_mlm_modern_geo.txt` |
| Train | ~90,000 pairs | `train_paired.jsonl`, `train_modern_geo.txt` |

Historical era files are copied in full (no split) as `train_old_geo.txt` and `train_middle_geo.txt`.

---

### Phase 2: Continued Pretraining

All pretraining uses **causal language modeling** (next-token prediction) on the LLaMA 3.2-3B decoder.

**Hyperparameters:**
- Optimizer: AdamW, bfloat16 precision
- Learning rate: 1e-5
- Global batch size: 32 (with gradient accumulation)
- Epochs per stage: 5
- Hardware: NVIDIA A100 GPU (Google Colab)
- Library: Hugging Face Transformers + [Unsloth](https://github.com/unslothai/unsloth) optimizations

**Curriculum variants:**

| Variant | Pretraining Data Order |
|---|---|
| Baseline | No pretraining |
| Mixed | Shuffled: Old + Middle + Modern Georgian |
| Chronological | Epoch 1–5 Old → Epoch 1–5 Middle → Epoch 1–5 Modern |
| Reverse | Epoch 1–5 Modern → Epoch 1–5 Middle → Epoch 1–5 Old |

Input sequences are concatenated Georgian paragraphs/lines, truncated/padded to 2048 tokens.

---

### Phase 3: Supervised Fine-Tuning for MT

After pretraining (or directly from base for Baseline), each model is fine-tuned for translation using **LoRA** (Low-Rank Adaptation):

- **Base model:** `unsloth/llama-3.2-3b-instruct-unsloth-bnb-4bit`
- **LoRA rank:** 32–64, alpha 16–32 — approximately 15–20M trainable parameters (~0.5–1% of total)
- **Task format:**
  ```
  Translate the following English text to Georgian.
  <English source>
  ###
  <Georgian target>
  ```
- **Hyperparameters:** Learning rate 2e-4 (cosine decay + warmup), batch size 64–128, 5 epochs
- **Library:** Unsloth's optimized LoRA trainer (≥2× speedup vs. standard PEFT)

The trained adapters are saved in `models/<name>_sft_final/` and can be loaded with `unsloth.FastLanguageModel`.

---

### Phase 4: Evaluation

**Automatic metrics:**
- **SacreBLEU** — n-gram precision-based translation quality
- **COMET** — neural MT evaluation metric (model-based, correlates better with human judgment)

**Human evaluation (MTEval):**
- Translations rated by human evaluators; lower score = better quality

**Inference script (`model_translations.py`):**
Loads each LoRA adapter via `FastLanguageModel.from_pretrained()`, runs the 50-sample test subset through all models, and saves per-model and combined CSV outputs.

---

## Running the Code

### Prerequisites

```bash
pip install unsloth transformers peft trl accelerate
pip install requests beautifulsoup4 pandas tqdm sacrebleu
```

A **HuggingFace token** is required to load the base model. Set it as an environment variable or in Google Colab Secrets:
```bash
export HF_TOKEN=hf_...
```

### Step-by-Step Pipeline

**Step 1 — Scrape TITUS corpus** (optional; scraped files already in `titus_corpus/`)
```bash
python titus_scrape.py
```

**Step 2 — Combine scraped files by era**
```bash
python old_mid_combine.py
```

**Step 3 — Clean historical Georgian text**
```bash
python old_middle_clean.py
```

**Step 4 — Combine parallel corpora** (requires the large JSON source files)
```bash
python Combine_Scriptural_general_lang.py
```

**Step 5 — Split data into train/val/test**
```bash
python split_data.py
```

**Step 6 — Train models** (requires GPU; use the Colab notebook)
Open `Turn-in Folder/Copy of Final_Llama_Pre-training_Fine-tuning.ipynb` in Google Colab.
See `Turn-in Folder/Instructions.txt` for setup details (path configuration, HF token, which cells to run).

**Step 7 — Run inference on test samples**
```bash
python model_translations.py
```

---

## Google Colab Notebook

The notebook `Turn-in Folder/Copy of Final_Llama_Pre-training_Fine-tuning.ipynb` contains the complete training and evaluation pipeline:

1. **Setup** — mount Google Drive, install dependencies, authenticate HuggingFace
2. **QLoRA fine-tuning** — baseline SFT training
3. **Training variants** — chronological, mixed, and reverse-chronological pretraining + SFT
4. **Merge LoRA** — optionally merge adapter weights into the base model
5. **Evaluation:**
   - Single-sentence translation through all 4 models
   - 50-sample batch translation
   - Full test set translation + BLEU/chrF scoring
   - COMET scoring on full predictions

> **Note:** Training sections (QLoRA + Variants) take many hours on an A100. Skip these and load the pre-trained adapters directly for evaluation.

All paths marked with `@@@` in the notebook must be updated to match your Google Drive mount point pointing to the `Turn-in Folder/` directory.

---

## Model Adapters

Four LoRA adapters are stored in `models/`. Each has the same structure:

```
models/<name>_sft_final/
├── adapter_config.json        # LoRA configuration (rank, alpha, target modules)
├── adapter_model.safetensors  # Trained weights — gitignored (36 MB)
├── chat_template.jinja        # Jinja2 prompt template for the model
├── special_tokens_map.json    # Special token definitions
├── tokenizer.json             # Tokenizer vocabulary — gitignored (17 MB)
├── tokenizer_config.json      # Tokenizer settings (50 KB)
└── README.md                  # HuggingFace model card
```

**Base model:** `unsloth/llama-3.2-3b-instruct-unsloth-bnb-4bit` (Meta LLaMA 3.2-3B, 4-bit quantized)

To load a model for inference:
```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="models/chron_sft_final",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
```

> The `.safetensors` weight files are excluded from this repo due to size. Download or retrain to use the models.

---

## Dataset Details

### TITUS Corpus (Monolingual Georgian, Pretraining)

Source: [TITUS — Thesaurus Indogermanischer Text- und Sprachmaterialien](http://titus.uni-frankfurt.de/indexe.htm), Goethe University Frankfurt

| Era | Period | Sources | Size |
|---|---|---|---|
| Old Georgian | 5th–11th c. | Hagiography (6 vols), Bible, Inscriptions | ~15 MB |
| Middle Georgian | 12th–18th c. | Visramiani, Arcil's Visramiani, Omainiani, Aleksiani | ~2.4 MB |

### LDS Parallel Corpus (Fine-tuning)

Source: Translation memories of The Church of Jesus Christ of Latter-day Saints
~100,000 English–Georgian sentence pairs from religious texts
Format: `{"en": "...", "ka": "..."}` JSON records

### Data Files Not Included in This Repo (Too Large)

| File | Size | Description |
|---|---|---|
| `GENERAL_LDS_LANG.json` | 63 MB | Modern LDS Georgian parallel data |
| `SCRIPTURAL_LANG_DO_NOT_EDIT.json` | 23 MB | Scriptural Georgian parallel data |
| `Data/COMBINED_GE_EN.json` | 86 MB | Merged parallel corpus |
| `Data/splits/train_paired.jsonl` | 77 MB | Training translation pairs |
| `Data/splits/train_modern_geo.txt` | 51 MB | Modern Georgian training sentences |
| `models/*/adapter_model.safetensors` | 36 MB each | LoRA adapter weights (×4) |
| `models/*/tokenizer.json` | 17 MB each | Tokenizer vocabulary (×4) |
| `Turn-in Folder/LLaMA_project demo.mp4` | 386 MB | Project demo video |

---

## Related Work

- **Campos (2021)** — Curriculum learning for language modeling; linguistically motivated curricula improve transfer learning
- **Jasonarson & Steingrímsson (2025)** — Continued pretraining of Llama 3.2 on monolingual Icelandic for low-resource MT; closest architectural analog to this project
- **Liu et al. (2021)** — Continual mixed-language pretraining for extremely low-resource NMT
- **Sennrich et al. (2016)** — Back-translation as a method for augmenting parallel data from monolingual text
- **Fadaee et al. (2017)** — Translation data augmentation for low-resource NMT via rare-word substitution
- **Hamilton et al. (2018)** — Diachronic word embeddings reveal statistical laws of semantic change
- **Takaku et al. (2020)** — NMT from historical Japanese to contemporary Japanese using diachronically adapted embeddings; key motivation for reverse-chronological ordering
- **Gibadullin et al. (2019)** — Survey of monolingual data methods for low-resource NMT

---

## Conclusions & Future Work

**Conclusions:**
- Continued pretraining on historical Georgian data, in any order, improved script acquisition: all three pretrained models generated actual Georgian (Mkhedruli) script, while the Baseline generated Latin-script pseudowords.
- Chronological ordering yielded the best COMET score and human evaluation, suggesting curriculum-based pretraining helps — consistent with the literature.
- Reverse-chronological ordering unexpectedly achieved the highest BLEU score, possibly due to BLEU's sensitivity to surface n-gram overlap rather than semantic quality.
- Low overall scores reflect the fundamental challenge: LLaMA 3.2-3B has virtually no Georgian in its original training data, requiring much more pretraining than was computationally feasible.

**Future work:**
- Establish a solid MT fine-tuning baseline *before* adding pretraining variants
- Scale pretraining data and compute (more epochs, larger corpus)
- Experiment with vocabulary expansion for Georgian characters
- Compare against dedicated multilingual models (mBART, NLLB) as stronger baselines
- Apply the curriculum-ordering approach to other morphologically rich, low-resource languages

---

## Citation

If you use this code or data pipeline, please cite:

```
Fisher, Jacob B. (2025). Transfer Learning from Historical Monolingual Data
for Low-Resource MT: A Case Study of Georgian. CS 479 Final Project,
Brigham Young University.
```

---

## License

This repository contains scripts written for a university course project. The TITUS corpus texts are subject to their original licensing from Goethe University Frankfurt. The LDS parallel corpus is property of The Church of Jesus Christ of Latter-day Saints and is not redistributed here.
