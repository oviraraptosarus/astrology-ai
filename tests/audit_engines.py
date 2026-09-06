import sys, os, inspect, importlib
sys.path.insert(0, os.path.abspath("."))

engines = [
    'astrology_engine', 'kp_engine', 'strength_engine', 'sensitive_points', 
    'ashtakavarga_engine', 'cancellations', 'advanced_avasthas', 'yogas',
    'panchangam_engine', 'longevity_engine', 'event_analysis', 'forward_timing_scanner',
    'jaimini_chara_dasha_engine', 'tajika_engine', 'ashtakavarga_kakshya_engine',
    'kundali_milan_synastry_engine', 'sade_sati_engine', 'remedy_engine',
    'institutional_chakra_engine', 'financial_astro_engine', 'numerology_engine',
    'pancha_pakshi_engine', 'dosha_engine', 'transit_engine', 'prashna_engine'
]

print(f"{'ENGINE':<32} | {'STATUS':<10} | {'MEMBERS'}")
print("-" * 80)
for eng in engines:
    try:
        mod = importlib.import_module(eng)
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass)]
        print(f"{eng:<32} | {'FOUND':<10} | {', '.join(classes[:4])}")
    except Exception as e:
        print(f"{eng:<32} | {'ERROR':<10} | {e}")
