import os
import re

def search():
    found_dasha = []
    found_ashtakavarga = []
    
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or '.git' in root or '__pycache__' in root or 'Claude_Skills' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if re.search(r'def calculate_vimshottari|VIMSHOTTARI_YEARS|def calculate_dasha', content, re.IGNORECASE):
                        found_dasha.append(file)
                    if re.search(r'def calculate_ashtakavarga|def calculate_bav|def calculate_sav', content, re.IGNORECASE):
                        found_ashtakavarga.append(file)
                        
    print("Files containing Dasha logic:")
    for f in set(found_dasha): print(" -", f)
    
    print("\nFiles containing Ashtakavarga logic:")
    for f in set(found_ashtakavarga): print(" -", f)

if __name__ == '__main__':
    search()
