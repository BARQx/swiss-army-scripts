import re
import csv
from collections import defaultdict

# Keyman to XKB physical key mapping (QWERTY-based)
KEYMAN_TO_XKB = {
    'K_Q': 'AD01', 'K_W': 'AD02', 'K_E': 'AD03', 'K_R': 'AD04', 'K_T': 'AD05',
    'K_Y': 'AD06', 'K_U': 'AD07', 'K_I': 'AD08', 'K_O': 'AD09', 'K_P': 'AD10',
    'K_A': 'AC01', 'K_S': 'AC02', 'K_D': 'AC03', 'K_F': 'AC04', 'K_G': 'AC05',
    'K_H': 'AC06', 'K_J': 'AC07', 'K_K': 'AC08', 'K_L': 'AC09', 'K_COLON': 'AC10',
    'K_Z': 'AB01', 'K_X': 'AB02', 'K_C': 'AB03', 'K_V': 'AB04', 'K_B': 'AB05',
    'K_N': 'AB06', 'K_M': 'AB07', 'K_COMMA': 'AB08', 'K_PERIOD': 'AB09', 'K_SLASH': 'AB10',
    'K_1': 'AE01', 'K_2': 'AE02', 'K_3': 'AE03', 'K_4': 'AE04', 'K_5': 'AE05',
    'K_6': 'AE06', 'K_7': 'AE07', 'K_8': 'AE08', 'K_9': 'AE09', 'K_0': 'AE10',
    'K_HYPHEN': 'AE11', 'K_EQUAL': 'AE12',
    'K_LBRKT': 'AD11', 'K_RBRKT': 'AD12', 'K_BKSLASH': 'BKSL',
    'K_BKQUOTE': 'TLDE', 'K_SPACE': 'SPCE', 'K_QUOTE': 'AC11'
}

MODIFIER_NAMES = {
    0: "Base",
    1: "Shift",
    2: "AltGr",
    3: "Shift+AltGr"
}

def parse_kmn(kmn_text):
    key_data = defaultdict(lambda: [None, None, None, None])

    pattern = re.compile(
        r'^\s*\+?\s*\[([A-Za-z_ ]*K_[A-Z0-9_]+)\]\s*>\s*U\+([0-9a-fA-F]+)',
        re.IGNORECASE
    )

    for line in kmn_text.split('\n'):
        match = pattern.match(line.strip())
        if not match:
            continue

        modifiers, unicode_char = match.groups()
        modifiers = modifiers.split()
        key_name = modifiers[-1]

        level = 0
        if 'SHIFT' in modifiers and 'RALT' in modifiers:
            level = 3
        elif 'SHIFT' in modifiers:
            level = 1
        elif 'RALT' in modifiers:
            level = 2

        if key_name in KEYMAN_TO_XKB:
            xkb_key = KEYMAN_TO_XKB[key_name]
            key_data[xkb_key][level] = f"U{unicode_char.upper()}"

    return key_data

def parse_xkb(xkb_text):
    key_data = {}

    pattern = re.compile(
        r'key\s*<([A-Z0-9]+)>\s*{\s*\[\s*([^]]+)\s*\]\s*};'
    )

    for line in xkb_text.split('\n'):
        match = pattern.search(line.strip())
        if not match:
            continue

        key_name, symbols = match.groups()
        symbols = [s.strip() for s in symbols.split(',')]
        symbols = [s if s != "NoSymbol" else None for s in symbols]
        key_data[key_name] = symbols

    return key_data

def get_char(unicode_str):
    if not unicode_str:
        return ""
    try:
        return chr(int(unicode_str[1:], 16))
    except:
        return ""

def compare_layouts(kmn_data, xkb_data):
    results = []
    all_keys = set(kmn_data.keys()).union(set(xkb_data.keys()))

    for key in sorted(all_keys):
        kmn_symbols = kmn_data.get(key, [None]*4)
        xkb_symbols = xkb_data.get(key, [None]*4)

        for level in range(4):
            kmn_char = kmn_symbols[level]
            xkb_char = xkb_symbols[level]

            kmn_decoded = get_char(kmn_char)
            xkb_decoded = get_char(xkb_char)

            status = "Match" if kmn_char == xkb_char else "Mismatch"

            results.append({
                'Key': key,
                'Modifier': MODIFIER_NAMES[level],
                'KMN_Unicode': kmn_char or "None",
                'XKB_Unicode': xkb_char or "None",
                'KMN_Char': kmn_decoded,
                'XKB_Char': xkb_decoded,
                'Status': status
            })

    return results

def save_to_csv(results, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Key', 'Modifier', 'KMN_Unicode', 'XKB_Unicode',
                    'KMN_Char', 'XKB_Char', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in results:
            writer.writerow(row)

def main():
    kmn_file = "keyboard.kmn"
    xkb_file = "keyboard.xkb"
    output_csv = "keyboard_comparison.csv"

    with open(kmn_file, 'r', encoding='utf-8') as f:
        kmn_text = f.read()
    with open(xkb_file, 'r', encoding='utf-8') as f:
        xkb_text = f.read()

    kmn_data = parse_kmn(kmn_text)
    xkb_data = parse_xkb(xkb_text)

    results = compare_layouts(kmn_data, xkb_data)
    save_to_csv(results, output_csv)

    print(f"Comparison complete. Results saved to {output_csv}")

    # Print summary stats
    total = len(results)
    matches = sum(1 for r in results if r['Status'] == "Match")
    mismatches = total - matches
    print(f"\nSummary: {matches} matches, {mismatches} mismatches ({matches/total:.1%} match rate)")

if __name__ == "__main__":
    main()
