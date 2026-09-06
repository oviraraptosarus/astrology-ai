
import sys, os
sys.path.insert(0, "E:/ASTROLOGY AI")
from kp_engine import KPEngine
import json

# Polar location: Svalbard, Norway (78°13'N, 15°38'E) 
# Note: June 15, 2026, 12:00 UTC
res = KPEngine.calculate_kp_chart(
    2026, 6, 15, 12, 0, 78.2232, 15.6267, "UTC"
)

# Print house cusps
for cusp in res['cusps']:
    print(f"H{cusp['house']}: {cusp['sign']} {cusp['degree']:.2f}")

