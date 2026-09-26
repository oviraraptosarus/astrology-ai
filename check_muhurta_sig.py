import sys
import inspect
sys.path.insert(0, r"E:\ASTROLOGY AI")

import astrology_engine

print("find_muhurta signature:", inspect.signature(astrology_engine.find_muhurta))
print()
print(astrology_engine.find_muhurta.__doc__[:1500] if astrology_engine.find_muhurta.__doc__ else "No docstring")