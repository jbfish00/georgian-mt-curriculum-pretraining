#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# ----------------------------------------------------------------------
# 1. SCRIPT NORMALISATION
# ----------------------------------------------------------------------
def normalize_georgian(c: str) -> str:
    o = ord(c)
    if 0x10A0 <= o <= 0x10CF:          
        return chr(o + 0x30)
    if 0x2D00 <= o <= 0x2D2F:          
        return chr(o - 0x1C30)
    if 0x1C90 <= o <= 0x1CBF:          
        return chr(o - 0xBC0)
    return c


# ----------------------------------------------------------------------
# 2. CLEANING + SMART LINE/SENTENCE SPLITTING + FILTER SHORT LINES
# ----------------------------------------------------------------------
GEORGIAN_RANGE = re.compile(r'[\u10A0-\u10FF\u2D00-\u2D2F\u1C90-\u1CBF]+')

def is_georgian_line(line: str) -> bool:
    return bool(GEORGIAN_RANGE.search(line))


def clean_and_split_text(raw: str) -> str:
    """
    Clean the page and split into lines/sentences:
    - If line contains '.', split into sentences
    - Otherwise keep as one line
    - Remove any resulting line with < 3 words
    Returns multi-line string.
    """
    # 1. Remove TITUS headers and metadata
    raw = re.sub(r'^TITUS Texts:.*$', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^Text:.*$', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'^\w+ \d{1,2}\.\d{1,2}\.\d{4}.*$', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'(?i)manuscript page:.*$', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'Line of ed\.: \d+', '', raw, flags=re.MULTILINE)
    raw = re.sub(r'[\[\]]', '', raw)
    raw = re.sub(r'\(\s*\)', '', raw)

    # 2. Get raw lines
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    geo_lines = [ln for ln in lines if is_georgian_line(ln)]

    # 3. Clean each line
    cleaned = []
    for ln in geo_lines:
        ln = re.sub(r'\(javascript:ci\(.*?\)\)', '', ln)
        ln = re.sub(r'^\d+\.\s*', '', ln)
        ln = re.sub(r'\s+', ' ', ln).strip()
        if ln:
            cleaned.append(ln)

    # 4. Normalize script
    normalized = [''.join(normalize_georgian(c) for c in ln) for ln in cleaned]

    # 5. Split by sentence IF period exists, otherwise keep line
    final_lines = []
    for line in normalized:
        if '.' in line:
            # Split after periods, but keep the period attached
            sentences = re.split(r'(?<=[.])\s+', line)
            for s in sentences:
                s = s.strip()
                if s and len(s.split()) >= 3:
                    final_lines.append(s)
        else:
            # No period → keep full line if long enough
            if len(line.split()) >= 3:
                final_lines.append(line)

    return '\n'.join(final_lines)


# ----------------------------------------------------------------------
# 3. PAGE FETCH + CLEAN
# ----------------------------------------------------------------------
def extract_normalized_text(url: str) -> str | None:
    try:
        r = requests.get(url, timeout=12, headers=HEADERS)
        r.encoding = 'utf-8'
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        raw = soup.get_text(separator="\n", strip=True)
        cleaned = clean_and_split_text(raw)
        if cleaned:
            print(f"[TEXT FOUND] {url} → {len(cleaned.splitlines())} lines")
        else:
            print(f"[NO TEXT] {url}")
        return cleaned
    except Exception as e:
        print(f"[ERROR] {url} → {e}")
        return None


# ----------------------------------------------------------------------
# 4. NAVIGATION (unchanged)
# ----------------------------------------------------------------------
NUM_PATTERN = re.compile(r'(\d{3,})\.htm$')

def find_prev_next_links(soup: BeautifulSoup, base_url: str):
    current_filename = base_url.split('/')[-1]
    match = NUM_PATTERN.search(current_filename)
    if not match:
        return None, None
    try:
        current_num = int(match.group(1))
    except ValueError:
        return None, None

    prev = None
    nxt = None
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'javascript' in href or '..' in href or 'database' in href:
            continue
        full_url = urljoin(base_url, href)
        link_filename = full_url.split('/')[-1]
        link_match = NUM_PATTERN.search(link_filename)
        if link_match:
            try:
                link_num = int(link_match.group(1))
                if link_num < current_num:
                    prev = full_url
                elif link_num > current_num:
                    nxt = full_url
            except ValueError:
                pass
    return prev, nxt


# ----------------------------------------------------------------------
# 5. CRAWL SUB-CORPUS
# ----------------------------------------------------------------------
def scrape_sub_corpus(seed_url: str, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    visited = set()
    pages   = []

    # Backward
    cur = seed_url
    while cur and cur not in visited:
        print(f"[BACK] Fetching: {cur}")
        visited.add(cur)
        txt = extract_normalized_text(cur)
        if txt:
            pages.append(txt)
        time.sleep(1)

        r = requests.get(cur, headers=HEADERS)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        prev, _ = find_prev_next_links(soup, cur)
        cur = prev

    pages.reverse()

    # Forward
    cur = seed_url
    while cur:
        if cur not in visited:
            print(f"[FWD] Fetching: {cur}")
            visited.add(cur)
            txt = extract_normalized_text(cur)
            if txt:
                pages.append(txt)
            time.sleep(1)

        r = requests.get(cur, headers=HEADERS)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, "html.parser")
        _, nxt = find_prev_next_links(soup, cur)
        cur = nxt

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(pages))
    print(f"→ {out_path}  ({len(pages)} parts, {sum(len(p.splitlines()) for p in pages)} total lines)")


# ----------------------------------------------------------------------
# 6. SEEDS
# ----------------------------------------------------------------------
OLD_SEEDS = {
    "hagi_vol1": "https://titus.uni-frankfurt.de/texte/etcs/cauc/ageo/gh/gh1/gh1004.htm",
    "hagi_vol2": "https://titus.uni-frankfurt.de/texte/etcs/cauc/ageo/gh/gh2/gh2104.htm",
    "hagi_vol3": "https://titus.uni-frankfurt.de/texte/etcs/cauc/ageo/gh/gh3/gh3029.htm",
    "hagi_vol4": "https://titus.uni-frankfurt.de/texte/etcg/cauc/ageo/gh/gh4/gh4020.htm",
    "hagi_vol5": "https://titus.uni-frankfurt.de/texte/etcg/cauc/ageo/gh/gh5/gh5005.htm",
    "hagi_vol6": "https://titus.uni-frankfurt.de/texte/etcg/cauc/ageo/gh/gh6/gh6004.htm",
    "inscr":     "https://titus.uni-frankfurt.de/texte/etcg/cauc/ageo/inscr/carcera/carce034.htm",
    "bible_mcx": "https://titus.uni-frankfurt.de/texte/etcs/cauc/ageo/at/mcat/mcat001.htm",
}

MIDDLE_SEEDS = {
    "visramiani":      "https://titus.uni-frankfurt.de/texte/etca/cauc/mgeo/visr/visrg/visrg074.htm",
    "arcil_visr":      "https://titus.uni-frankfurt.de/texte/etca/cauc/mgeo/arcil/arcilvis/arcil011.htm",
    "omainiani":       "https://titus.uni-frankfurt.de/texte/etca/cauc/mgeo/omainian/omain030.htm",
    "aleksiani":       "https://titus.uni-frankfurt.de/texte/etcg/cauc/mgeo/aleksian/aleks003.htm",
}

# ----------------------------------------------------------------------
# 7. RUN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    for name, url in OLD_SEEDS.items():
        scrape_sub_corpus(url, f"titus_corpus/old_georgian_{name}.txt")

    for name, url in MIDDLE_SEEDS.items():
        scrape_sub_corpus(url, f"titus_corpus/middle_georgian_{name}.txt")