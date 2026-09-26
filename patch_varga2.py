import re
import os

with open('varga_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the helper function
helper_func = """    @staticmethod
    def _get_varga_idx(degree: float, divisions: int) -> int:
        import math
        quotient = (degree * divisions) / 30.0
        rounded = round(quotient)
        if math.isclose(quotient, rounded, rel_tol=0.0, abs_tol=1e-11):
            idx = int(rounded)
        else:
            idx = int(quotient)
        if idx >= divisions:
            idx = divisions - 1
        return idx

    @staticmethod
    def calc_d3_drekkana"""

content = content.replace("    @staticmethod\n    def calc_d3_drekkana", helper_func)

# Replace all the calc_dx formulas
content = re.sub(r'div3 = int\(\(degree / 10\.0\) \+ 1e-9\)\n        if div3 >= 3: div3 = 2.*\n', r'div3 = VargaEngine._get_varga_idx(degree, 3)\n', content)
content = re.sub(r'div4 = int\(\(degree / 7\.5\) \+ 1e-9\)\n        if div4 >= 4: div4 = 3\n', r'div4 = VargaEngine._get_varga_idx(degree, 4)\n', content)
content = re.sub(r'div7 = int\(\(degree / \(30\.0 / 7\.0\) \+ 1e-9\)\)\n        if div7 >= 7: div7 = 6\n', r'div7 = VargaEngine._get_varga_idx(degree, 7)\n', content)
content = re.sub(r'division = int\(\(degree / \(30\.0 / 9\.0\) \+ 1e-9\)\)\n        if division >= 9: division = 8\n', r'division = VargaEngine._get_varga_idx(degree, 9)\n', content)
content = re.sub(r'division = int\(\(degree / 3\.0\) \+ 1e-9\)\n        if division >= 10: division = 9\n', r'division = VargaEngine._get_varga_idx(degree, 10)\n', content)
content = re.sub(r'div12 = int\(\(degree / 2\.5\) \+ 1e-9\)\n        if div12 >= 12: div12 = 11\n', r'div12 = VargaEngine._get_varga_idx(degree, 12)\n', content)
content = re.sub(r'div16 = int\(\(degree / 1\.875\) \+ 1e-9\)\n        if div16 >= 16: div16 = 15\n', r'div16 = VargaEngine._get_varga_idx(degree, 16)\n', content)
content = re.sub(r'div20 = int\(\(degree / 1\.5\) \+ 1e-9\)\n        if div20 >= 20: div20 = 19\n', r'div20 = VargaEngine._get_varga_idx(degree, 20)\n', content)
content = re.sub(r'div24 = int\(\(degree / 1\.25\) \+ 1e-9\)\n        if div24 >= 24: div24 = 23\n', r'div24 = VargaEngine._get_varga_idx(degree, 24)\n', content)
content = re.sub(r'div27 = int\(\(degree / \(30\.0 / 27\.0\) \+ 1e-9\)\)\n        if div27 >= 27: div27 = 26\n', r'div27 = VargaEngine._get_varga_idx(degree, 27)\n', content)
content = re.sub(r'div40 = int\(\(degree / 0\.75\) \+ 1e-9\)\n        if div40 >= 40: div40 = 39\n', r'div40 = VargaEngine._get_varga_idx(degree, 40)\n', content)
content = re.sub(r'div45 = int\(\(degree / \(30\.0 / 45\.0\) \+ 1e-9\)\)\n        if div45 >= 45: div45 = 44\n', r'div45 = VargaEngine._get_varga_idx(degree, 45)\n', content)
content = re.sub(r'div60 = int\(\(degree / 0\.5\) \+ 1e-9\)\n        if div60 >= 60: div60 = 59\n', r'div60 = VargaEngine._get_varga_idx(degree, 60)\n', content)

with open('varga_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("varga patched.")
