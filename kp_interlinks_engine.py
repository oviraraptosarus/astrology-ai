"""
KP Cuspal Interlinks (CIL) & 12-Bhava Event Gating Engine (Prof. K.S. Krishnamurti Method)
Implements:
1. 12 Cuspal Sub-Lords (CSL) Extraction from Placidus House Cusps.
2. ABCD 4-Tier Significator Mapping for each Cuspal Sub-Lord:
   - Level A: Planet in Nakshatra of House Occupant.
   - Level B: Planet in House.
   - Level C: Planet in Nakshatra of House Lord.
   - Level D: Planet ruling the House.
3. Deterministic Event Gating (Promise vs Denial Matrix for all 12 Life Domains):
   - Marriage (Cusp 7): 2, 7, 11 (Manifestation) vs 1, 6, 10 (Denial/Separation).
   - Career (Cusp 10): 2, 6, 10, 11 (Rise) vs 5, 9 (Retirement/Loss).
   - Wealth (Cusp 2): 2, 6, 11 (Accumulation) vs 5, 8, 12 (Expenditure).
   - Progeny (Cusp 5): 2, 5, 11 (Birth) vs 1, 4, 10 (Obstruction).
   - Foreign Move (Cusp 12): 3, 9, 12 (Relocation) vs 4, 11 (Retained in Homeland).
"""
from typing import Dict, Any, List
from datetime import datetime
from vedic_models import Chart, Planet
from kp_engine import KPEngine

KP_EVENT_RULES = {
    1: {"name": "Longevity & Vitality", "promise": [1, 3, 8, 11], "denial": [6, 8, 12, 2, 7], "label": "Physical Longevity & Robust Health"},
    2: {"name": "Wealth Accumulation", "promise": [2, 6, 11], "denial": [5, 8, 12], "label": "Financial Savings & Material Growth"},
    3: {"name": "Contracts & Media", "promise": [3, 9, 11], "denial": [4, 8], "label": "Contractual Success & Media Publishing"},
    4: {"name": "Property & Real Estate", "promise": [4, 11, 12], "denial": [3, 6], "label": "Fixed Asset & Property Acquisition"},
    5: {"name": "Progeny & Romance", "promise": [2, 5, 11], "denial": [1, 4, 10], "label": "Childbirth & Creative Recognition"},
    6: {"name": "Litigation & Healing", "promise": [6, 11], "denial": [5, 12], "label": "Victory over Adversaries & Disease Recovery"},
    7: {"name": "Marriage & Partnership", "promise": [2, 7, 11], "denial": [1, 6, 10], "label": "Marital Bond & Business Partnership"},
    8: {"name": "Inheritance & Sudden Gains", "promise": [2, 8, 11], "denial": [12], "label": "Sudden Windfalls & Legacy Inheritance"},
    9: {"name": "Higher Wisdom & Dharma", "promise": [9, 11], "denial": [3], "label": "Pilgrimage, Higher Education & Fortune"},
    10: {"name": "Career & Executive Status", "promise": [2, 6, 10, 11], "denial": [5, 9], "label": "Career Elevation & Executive Command"},
    11: {"name": "Fulfillment of Ambitions", "promise": [2, 11], "denial": [12], "label": "Realization of Major Desires & Cash Flow"},
    12: {"name": "Foreign Travel & Relocation", "promise": [3, 9, 12], "denial": [4, 11], "label": "Overseas Relocation & Spiritual Liberation"}
}

class KPCuspalInterlinksEngine:
    def __init__(self, chart: Chart, y: int = 1990, m: int = 1, d: int = 15, h: int = 14, mn: int = 30, lat: float = 28.6139, lon: float = 77.2090, tz: str = "Asia/Kolkata"):
        self.chart = chart
        btime = getattr(chart, "birth_time", None)
        if isinstance(btime, datetime):
            y, m, d, h, mn = btime.year, btime.month, btime.day, btime.hour, btime.minute
        
        self.kp_payload = KPEngine.calculate_kp_chart(y, m, d, h, mn, lat, lon, tz)
        self.cusps = {c["house"]: c for c in self.kp_payload.get("cusps", [])}
        self.significators = self.kp_payload.get("significators_abcd", {})

    def evaluate_cuspal_promises(self) -> Dict[str, Any]:
        """Evaluates all 12 Cuspal Sub-Lords against KP Promise/Denial rules."""
        results = {}
        for cusp_num, config in KP_EVENT_RULES.items():
            cusp_data = self.cusps.get(cusp_num, {})
            sub_lord = cusp_data.get("sub_lord", "Jupiter")
            
            # Find houses signified by this Sub-Lord
            sub_sig_houses = []
            for h_num, sig_dict in self.significators.items():
                all_planets = sig_dict.get("level_a", []) + sig_dict.get("level_b", []) + sig_dict.get("level_c", []) + sig_dict.get("level_d", [])
                if sub_lord in all_planets:
                    sub_sig_houses.append(int(h_num))

            sub_sig_houses = list(set(sub_sig_houses))
            
            promise_hits = [h for h in config["promise"] if h in sub_sig_houses]
            denial_hits = [h for h in config["denial"] if h in sub_sig_houses]

            # Gate Verdict
            if len(promise_hits) > 0 and len(denial_hits) == 0:
                verdict = f"STRONG PROMISE (Signifies {promise_hits} with zero denial)"
                gate = "APPROVED"
            elif len(promise_hits) >= len(denial_hits):
                verdict = f"PROMISE WITH MODIFIERS (Signifies {promise_hits}, with minor friction from {denial_hits})"
                gate = "CONDITIONAL"
            else:
                verdict = f"BLOCKED / DENIED (Denial houses {denial_hits} overpower promise {promise_hits})"
                gate = "DENIED"

            results[f"Cusp_{cusp_num}_{config['name'].replace(' ', '_')}"] = {
                "cusp_number": cusp_num,
                "domain_name": config["name"],
                "cusp_sub_lord": sub_lord,
                "signified_houses": sub_sig_houses,
                "promise_houses_activated": promise_hits,
                "denial_houses_activated": denial_hits,
                "gate_status": gate,
                "astrological_verdict": verdict
            }

        return results
