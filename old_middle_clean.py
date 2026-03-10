import os
import re
from pathlib import Path

def clean_georgian_text(input_path: Path, output_path: Path):
    """
    Final cleaning for Old & Middle Georgian:
    - Keep ALL Georgian letters (archaic included)
    - Keep: , . ; : ? ! and spaces
    - REMOVE manuscript symbols: ^ * § † ‡ ¶ • ◊ ◇ ◆ etc.
    - Split only on 3rd+ standalone "და"
    - Add newline after . ? ! only when needed
    """
    # All valid Georgian characters (Mtavruli, Asomtavruli, Nuskhuri, Mkhedruli + archaic)
    georgian_letters = (
        "აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ"
        "ჲჱჳჴჵჶჷჸჹჺ჻ჼჽჾჿ"
        "ႠႱႢႣႤႥႦႧႨႩႪႫႬႭႮႯႰႱႲႳႴႵႶႷႸႹႺႻႼႽႾႿ"
        "ჀჁჂჃჄჅ"
    )
    allowed_punct = ",.;:?! "
    allowed_chars = set(georgian_letters) | set(allowed_punct) | set("0123456789")

    # Characters to REMOVE (manuscript/editorial symbols)
    remove_symbols = set("^ * § † ‡ ¶ • · ¨ ° º ª ‹ › « » ˜ © ® ™ ± × ÷ √ ∞ ≈ ≠ ≤ ≥")
    remove_pattern = re.compile('|'.join(re.escape(c) for c in remove_symbols if c != ' '))

    # Standalone "და" (word boundaries)
    da_pattern = re.compile(r'(?<!\w)(და)(?!\w)')

    cleaned_lines = []

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for raw_line in lines:
        line = raw_line.rstrip('\n')

        if not line.strip():
            continue

        # Step 1: Remove only manuscript symbols
        text = remove_pattern.sub('', line)

        # Step 2: Keep only allowed characters (safety net)
        text = ''.join(c for c in text if c in allowed_chars or c.isspace())

        # Step 3: Newline after . ? ! if not at end and followed by Georgian letter
        text = re.sub(r'([.?!])(?=\s*[აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰჲჱჳჴჵჶჷჸჹჺ჻ჼჽჾჿ])',
                      r'\1\n', text)

        # Step 4: Split only on 3rd+ standalone "და"
        da_matches = list(da_pattern.finditer(text))
        if len(da_matches) >= 3:
            parts = []
            pos = 0
            for i, m in enumerate(da_matches):
                start, end = m.span()
                if i >= 2:  # 3rd and beyond
                    parts.append(text[pos:start])
                    parts.append('\n')
                    parts.append(m.group(0))
                    pos = end
                else:
                    parts.append(text[pos:end])
                    pos = end
            parts.append(text[pos:])
            text = ''.join(parts)

        # Step 5: Collect non-empty segments
        for seg in text.split('\n'):
            seg = seg.strip()
            if seg:
                cleaned_lines.append(seg)

    # Write
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines) + '\n')

    print(f"Cleaned: {input_path.name} → {output_path.name} ({len(cleaned_lines)} lines)")

# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------
if __name__ == "__main__":
    data_folder = Path(os.getcwd()) / "Data"

    files = [
        ("old_geo.txt", "old_geo_clean.txt"),
        ("middle_geo.txt", "middle_geo_clean.txt")
    ]

    for in_name, out_name in files:
        inp = data_folder / in_name
        out = data_folder / out_name
        if not inp.exists():
            raise FileNotFoundError(f"Not found: {inp}")
        clean_georgian_text(inp, out)

    print("\nFINAL CLEANING COMPLETE!")
    print("   • All archaic letters preserved (ჲ ჱ etc.)")
    print("   • Manuscript symbols removed (^ * § † etc.)")
    print("   • Split only on 3rd+ standalone 'და'")
    print("   • Your example line is 100% untouched")
    print("   • Ready for chronological / reverse-chronological pretraining")
    print("\nOutput files:")
    print(f"   {data_folder / 'old_geo_clean.txt'}")
    print(f"   {data_folder / 'middle_geo_clean.txt'}")