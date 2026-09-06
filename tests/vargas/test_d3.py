import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from varga_engine import VargaEngine

def test_d3():
    # Basic edge case to make sure it runs without exceptions
    assert isinstance(VargaEngine.calc_d3_drekkana("Aries", 5.0), str)
    print("test_d3 passed!")

if __name__ == "__main__":
    test_d3()
