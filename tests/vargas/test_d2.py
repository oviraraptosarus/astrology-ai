import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from varga_engine import VargaEngine

def test_d2_hora():
    # Sun Hora: Odd signs (0-15), Even signs (15-30) -> Leo
    # Moon Hora: Odd signs (15-30), Even signs (0-15) -> Cancer
    
    # Aries (Odd)
    assert VargaEngine.calc_d2_hora("Aries", 5.0) == "Leo"
    assert VargaEngine.calc_d2_hora("Aries", 16.0) == "Cancer"
    
    # Taurus (Even)
    assert VargaEngine.calc_d2_hora("Taurus", 5.0) == "Cancer"
    assert VargaEngine.calc_d2_hora("Taurus", 16.0) == "Leo"
    
    print("test_d2_hora passed!")

if __name__ == "__main__":
    test_d2_hora()
