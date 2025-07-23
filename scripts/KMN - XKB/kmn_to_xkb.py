import re
from collections import defaultdict

# Keyman to XKB physical key mapping (QWERTY-based)
# Adjust if your layout is non-QWERTY
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

def parse_kmn(kmn_text):
    key_data = defaultdict(lambda: [None, None, None, None])

    # Regex to extract: [MODIFIERS K_XX] > U+XXXX
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
        key_name = modifiers[-1]  # e.g., K_A

        # Determine XKB level (1=base, 2=Shift, 3=AltGr, 4=Shift+AltGr)
        level = 1
        if 'SHIFT' in modifiers and 'RALT' in modifiers:
            level = 4
        elif 'SHIFT' in modifiers:
            level = 2
        elif 'RALT' in modifiers:
            level = 3

        # Store in key_data
        if key_name in KEYMAN_TO_XKB:
            xkb_key = KEYMAN_TO_XKB[key_name]
            key_data[xkb_key][level-1] = f"U{unicode_char.upper()}"

    return key_data

def generate_xkb(key_data):
    xkb_output = []
    for key, symbols in sorted(key_data.items()):
        # Replace None with NoSymbol
        symbols = [s if s is not None else "NoSymbol" for s in symbols]
        xkb_output.append(f'key <{key}> {{ [ {", ".join(symbols)} ] }};')
    return "\n".join(xkb_output)

def main():
    # Read .kmn file
    kmn_file = input("Enter path to .kmn file: ").strip()
    with open(kmn_file, 'r', encoding='utf-8') as f:
        kmn_text = f.read()

    # Parse and convert
    key_data = parse_kmn(kmn_text)
    xkb_output = generate_xkb(key_data)

    # Write .xkb file
    output_file = kmn_file.replace('.kmn', '.xkb')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"default partial alphanumeric_keys\n")
        f.write(f"xkb_symbols \"basic\" {{\n\n")
        f.write(xkb_output)
        f.write("\n\n};\n")

    print(f"Successfully converted to {output_file}")

if __name__ == "__main__":
    main()
