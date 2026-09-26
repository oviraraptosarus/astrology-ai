import sys
import os
sys.path.insert(0, "E:/ASTROLOGY AI")
from datetime import datetime
import json
import inspect
from astrology_engine import calculate_chart_with_object
import yogas
from sade_sati_engine import SadeSatiEngine
from forward_timing_scanner import ForwardTimingScanner
from condition_engine import ConditionEngine
from advanced_avasthas import AdvancedAvasthaEngine
from medical_astrology_engine import MedicalAstrologyEngine

chart, chart_dict = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8185549, 82.0641497, tz_name='Asia/Kolkata')

print("=== 1. ALL FIRED YOGAS ===")
for name, cls in inspect.getmembers(yogas, inspect.isclass):
    if issubclass(cls, yogas.Yoga) and cls is not yogas.Yoga:
        try:
            inst = cls()
            res = inst.evaluate(chart)
            if getattr(res, 'fired', False):
                print(f" [FIRED] {name:22s} | Confidence: {res.confidence:8s} | Reason: {res.reason}")
        except Exception:
            pass

print("\n=== 2. SADE SATI & SHANI TRANSITS ===")
sse = SadeSatiEngine(chart)
ss_cur = sse.evaluate_current_status(datetime.now())
print("Current Status:", json.dumps(ss_cur, indent=2))
ss_life = sse.generate_lifetime_sade_sati_timeline(datetime(2008, 8, 1, 12, 55))
print("\nLifetime Sade Sati Phases:")
for phase in ss_life:
    print(f" Phase: {phase.get('phase'):20s} | {phase.get('start_date')} -> {phase.get('end_date')} | Sign: {phase.get('saturn_sign')}")

print("\n=== 3. ADVANCED AVASTHAS ===")
aae = AdvancedAvasthaEngine(chart)
avasthas = aae.combine_all()
print("Avasthas:", json.dumps(avasthas, indent=2))

print("\n=== 4. FORWARD TIMING SCANNER ===")
fts = ForwardTimingScanner(chart)
for domain in ["career", "wealth", "business", "education"]:
    try:
        res = fts.scan_domain_windows(domain, start_year=2024, end_year=2032)
        print(f"\n--- Forward Scan: {domain.upper()} ---")
        for item in res:
            print(f" Window: {item.get('start_date')} -> {item.get('end_date')} | Score: {item.get('score')} | Confidence: {item.get('confidence')}%")
            print(f"   Dasha: {item.get('dasha_triad')} | Drivers: {item.get('drivers')}")
            if item.get('acute_micro_triggers'):
                print(f"   Micro-triggers: {item.get('acute_micro_triggers')}")
    except Exception as e:
        print(f" Error in domain {domain}: {e}")

print("\n=== 5. MEDICAL / PHYSICAL PROFILE ===")
try:
    mae = MedicalAstrologyEngine(chart)
    print('MAE methods:', [m for m in dir(mae) if not m.startswith('_')])
    for m in dir(mae):
        if not m.startswith('_'):
            try:
                fn = getattr(mae, m)
                if callable(fn):
                    print(f'{m} -> {fn()}')
            except Exception as e:
                print(f'{m} err -> {e}')
except Exception as e:
    print(f"Medical error: {e}")
