import os

def create_tests():
    tests_dir = "tests/vargas"
    vargas = [3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
    
    template = """import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from varga_engine import VargaEngine

def test_d{v_num}():
    # Basic edge case to make sure it runs without exceptions
    assert isinstance(VargaEngine.calc_d{v_num}_{name}("Aries", 5.0), str)
    print("test_d{v_num} passed!")

if __name__ == "__main__":
    test_d{v_num}()
"""

    names = {
        3: "drekkana", 4: "chaturthamsha", 7: "saptamsha", 9: "navamsha",
        10: "dasamsha", 12: "dwadashamsha", 16: "shodashamsha", 20: "vimshamsha",
        24: "chaturvimshamsha", 27: "saptavimshamsha", 30: "trimshamsha",
        40: "khavedamsha", 45: "akshavedamsha", 60: "shashtiamsha"
    }

    for v in vargas:
        content = template.format(v_num=v, name=names[v])
        with open(f"{tests_dir}/test_d{v}.py", "w") as f:
            f.write(content)

    # test_vargottama.py
    with open(f"{tests_dir}/test_vargottama.py", "w") as f:
        f.write("def test_vargottama():\n    pass\n")

if __name__ == "__main__":
    create_tests()
