"""
Parashari Ayurdaya Verification Runner (Pindayu & Amshayu)
Evaluates exact mathematical lifespan across the corpus.
"""

from astrology_engine import calculate_chart_with_object
from pindayu_engine import ParashariAyurdayaEngine
from death_window_analysis import CHARTS

def run_parashari_eval():
    print("=" * 95)
    print("PARASHARI MATHEMATICAL AYURDAYA ENGINE (BPHS Ch. 43-45) — ALL CHARTS")
    print("=" * 95)

    for name, info in CHARTS.items():
        y, m, d, h, mi, lat, lon, tz = info["b"]
        chart, _ = calculate_chart_with_object(y, m, d, h, mi, lat, lon, tz, name=name)
        
        eval_res = ParashariAyurdayaEngine.evaluate_tri_ayurdaya(chart)
        auth = eval_res["authoritative_model"]
        pind = eval_res["pindayu_result"]
        amsh = eval_res["amshayu_result"]

        actual_death = info.get("died", "Alive")

        print(f"\n🏛️ {name}")
        print(f"   • Selection Reason : {eval_res['selection_reason']}")
        print(f"   • Pindayu Lifespan : {pind['total_longevity_years']} Years ({pind['exact_lifespan_breakdown']})")
        print(f"   • Amshayu Lifespan : {amsh['total_longevity_years']} Years ({amsh['exact_lifespan_breakdown']})")
        print(f"   • Actual Ground Truth Death: {actual_death}")

if __name__ == "__main__":
    run_parashari_eval()
