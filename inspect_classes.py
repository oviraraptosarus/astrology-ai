import inspect
import sys
sys.path.insert(0, r"E:\ASTROLOGY AI")
import advanced_avasthas
import bhrigu_nandi_nadi_engine
import ashtakavarga_engine

for cls in [advanced_avasthas.AdvancedAvasthaEngine, bhrigu_nandi_nadi_engine.BhriguNandiNadiEngine, ashtakavarga_engine.AshtakavargaEngine]:
    print(f"=== {cls.__name__} ===")
    for m in dir(cls):
        if not m.startswith("__"):
            print(" ", m)
