import sys
import os
sys.path.insert(0, "E:/ASTROLOGY AI")
from datetime import datetime
import json
from astrology_engine import calculate_chart_with_object
from jaimini_arudha_argala_engine import JaiminiArudhaArgalaEngine
from yogas import (
    BudhadityaYoga, KemadrumaYoga, RuchakaYoga, BhadraYoga, 
    HamsaYoga, MalavyaYoga, ShashaYoga, DhanaYoga,
    ViparitaRajaYoga, NeechabhangaRajaYoga,
    RajaSambandhaYoga, JaiminiRajaYogaAKPK,
    ChamaraYoga, YogadaYoga, SoolaYoga, SunaphaYoga, AnaphaYoga, VesiYoga, VosiYoga, RajaYoga, DaridraYoga
)
from sade_sati_engine import SadeSatiEngine
from forward_timing_scanner import ForwardTimingScanner

chart, chart_dict = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8185549, 82.0641497, tz_name='Asia/Kolkata')

print("=== 1. ARUDHA PADAS & ARGALA ===")
jae = JaiminiArudhaArgalaEngine(chart)
arudhas = jae.calculate_all_padas()
print("Arudhas:", json.dumps(arudhas, indent=2))

print("\n=== 2. YOGAS EVALUATION ===")
yoga_classes = [
    BudhadityaYoga, KemadrumaYoga, RuchakaYoga, BhadraYoga, 
    HamsaYoga, MalavyaYoga, ShashaYoga, DhanaYoga,
    ViparitaRajaYoga, NeechabhangaRajaYoga,
    RajaSambandhaYoga, JaiminiRajaYogaAKPK,
    ChamaraYoga, YogadaYoga, SoolaYoga, SunaphaYoga, AnaphaYoga, VesiYoga, VosiYoga, RajaYoga, DaridraYoga
]

for ycls in yoga_classes:
    try:
        yinst = ycls(chart)
        res = yinst.evaluate()
        if getattr(res, 'fired', False):
            print(f" [FIRED] {ycls.__name__}: {res.description} (Strength: {res.strength})")
    except Exception as e:
        print(f" [ERR] {ycls.__name__}: {e}")

print("\n=== 3. SADE SATI / SHANI GOCHARA ===")
sse = SadeSatiEngine(chart)
ss_report = sse.analyze_lifetime_sade_sati(datetime(2008, 8, 1, 12, 55))
print("Current Status:", json.dumps(ss_report.get('current_status', {}), indent=2))
for p in ss_report.get('lifetime_cycles', []):
    print(f" Cycle {p.get('cycle')}: {p.get('start_date')} -> {p.get('end_date')}")

print("\n=== 4. FORWARD TIMING SCANNER (CAREER, WEALTH, PROPERTY/EDUCATION) ===")
fts = ForwardTimingScanner(chart)
for domain in ["CAREER", "WEALTH", "PROPERTY", "BUSINESS", "EDUCATION"]:
    try:
        windows = fts.scan_domain_windows(domain, start_year=2024, end_year=2030)
        print(f"\n--- Domain: {domain} ---")
        for w in windows:
            print(f" Window: {w.get('start_date')} to {w.get('end_date')} | Score: {w.get('score')} | Confidence: {w.get('confidence')}% | Drivers: {w.get('drivers')}")
            if w.get('acute_micro_triggers'):
                print(f"   Micro-triggers: {w.get('acute_micro_triggers')}")
    except Exception as e:
        print(f" Domain {domain} scan error: {e}")
