import sys, os
from hermes_tools import read_file, write_file

content = read_file(path="E:/ASTROLOGY AI/rectification_engine.py", limit=1000).get("content", "")

# 1. Replace EVENT_HOUSES
content = content.replace(
    'EVENT_HOUSES = {\n        "marriage": [7],\n        "career_job": [10, 6],',
    'EVENT_HOUSES = {\n        "marriage": {"primary": 7, "supporting": [2, 7, 11]},\n        "career_job": {"primary": 10, "supporting": [2, 6, 10, 11]},'
).replace(
    '"property_purchase": [4, 11],',
    '"property_purchase": {"primary": 4, "supporting": [4, 11, 12]},'
)

for old_v, new_v in [
    ('"birth_of_child": [5],', '"birth_of_child": {"primary": 5, "supporting": [2, 5, 11]},'),
    ('"accident_surgery": [6, 8, 12],', '"accident_surgery": {"primary": 8, "supporting": [6, 8, 12]},'),
    ('"financial_gain": [2, 11],', '"financial_gain": {"primary": 11, "supporting": [2, 6, 11]},'),
    ('"loss": [8, 12],', '"loss": {"primary": 12, "supporting": [8, 12]},'),
    ('"education": [4, 5, 9],', '"education": {"primary": 4, "supporting": [4, 9, 11]},'),
    ('"travel_foreign": [12, 3],', '"travel_foreign": {"primary": 12, "supporting": [3, 9, 12]},'),
    ('"health_issue": [6, 8],', '"health_issue": {"primary": 6, "supporting": [6, 8]},'),
    ('"spiritual": [9, 12],', '"spiritual": {"primary": 9, "supporting": [9, 12]},'),
    ('"death_family": [8, 3],', '"death_family": {"primary": 8, "supporting": [2, 7, 8]},'),
    ('"vehicle_purchase": [4, 1],', '"vehicle_purchase": {"primary": 4, "supporting": [4, 11]},'),
    ('"court_case": [6, 3, 8],', '"court_case": {"primary": 6, "supporting": [6, 8, 12]},'),
    ('"promotion": [10, 6],', '"promotion": {"primary": 10, "supporting": [2, 6, 10, 11]},')
]:
    content = content.replace(old_v, new_v)

# 2. CSL sig
from re import sub
content = sub(r"def _csl_significatorship_score\(kp_chart: Dict, event_house: int\) -> float:",
              "def _csl_significatorship_score(kp_chart: Dict, event_house: int, supporting_houses: List[int] = None) -> float:", content)

old_body = """            # Event-house cusp sub-lord
            cusp_sl = cusps[event_house - 1]["sub_lord"]

            # Significator set of the event house (A strongest → weight high)
            sig = abcd.get(str(event_house), {})
            level_a = sig.get("level_a", [])
            level_b = sig.get("level_b", [])
            level_c = sig.get("level_c", [])
            level_d = sig.get("level_d", [])

            score = 0.0
            if cusp_sl in level_a:
                score = max(score, 1.0)   # Star of occupant: strongest
            elif cusp_sl in level_b:
                score = max(score, 0.85)  # Occupant
            elif cusp_sl in level_c:
                score = max(score, 0.7)   # Star of lord
            elif cusp_sl in level_d:
                score = max(score, 0.6)   # Lord itself

            # Secondary: sub-lord in star of the house lord OR owns the house sign
            cusp = cusps[event_house - 1]
            sign_lord = cusp["sign_lord"]
            if cusp_sl == sign_lord:
                score = max(score, 0.7)

            return score"""

new_body = """            cusp_sl = cusps[event_house - 1]["sub_lord"]
            supp = supporting_houses if supporting_houses else [event_house]
            
            score = 0.0
            for h in supp:
                sig = abcd.get(str(h), {})
                if cusp_sl in sig.get("level_a", []): score = max(score, 1.0)
                elif cusp_sl in sig.get("level_b", []): score = max(score, 0.85)
                elif cusp_sl in sig.get("level_c", []): score = max(score, 0.7)
                elif cusp_sl in sig.get("level_d", []): score = max(score, 0.6)
            return score"""
content = content.replace(old_body, new_body)

# 3. Dasha connectivity
content = sub(r"def _dasha_connectivity_score\(kp_chart: Dict, dasha: Dict\[str, str], event_house: int\) -> float:",
              "def _dasha_connectivity_score(kp_chart: Dict, dasha: Dict[str, str], event_house: int, supporting_houses: List[int] = None) -> float:", content)

dasha_old = """        abcd = kp_chart.get("abcd_significators", {})
        sig = abcd.get(str(event_house), {})
        all_sig = set(sig.get("level_a", []) + sig.get("level_b", []) + sig.get("level_c", []) + sig.get("level_d", []))
        dasha_lords = {dasha["mahadasha"], dasha["antardasha"], dasha["pratyantardasha"]}
        overlap = dasha_lords & all_sig
        return len(overlap) / 3.0"""

dasha_new = """        abcd = kp_chart.get("abcd_significators", {})
        all_sig = set()
        supp = supporting_houses if supporting_houses else [event_house]
        for h in supp:
            sig = abcd.get(str(h), {})
            all_sig.update(sig.get("level_a", []) + sig.get("level_b", []) + sig.get("level_c", []) + sig.get("level_d", []))
        
        dasha_lords = {dasha["mahadasha"], dasha["antardasha"], dasha["pratyantardasha"]}
        overlap = dasha_lords & all_sig
        return len(overlap) / 3.0"""
content = content.replace(dasha_old, dasha_new)

# 4. The Loop
loop_old = """                total = 0.0
                per_event = []
                for ev_type, ev_date_str, ev_utc in event_dates:
                    event_houses = RectificationEngine.EVENT_HOUSES.get(ev_type, [7, 10])
                    eh = event_houses[0]

                    csl = RectificationEngine._csl_significatorship_score(kp, eh)
                    dasha = RectificationEngine._dasha_on_date(birth_nak_lord, candidate_utc, ev_utc)
                    dasha_sc = RectificationEngine._dasha_connectivity_score(kp, dasha, eh)
                    lagna_sc = RectificationEngine._lagna_nakshatra_score(lagna_lon, eh, kp)"""

loop_new = """                total = 0.0
                per_event = []
                for ev_type, ev_date_str, ev_utc in event_dates:
                    rules = RectificationEngine.EVENT_HOUSES.get(ev_type, {"primary": 1, "supporting": [1]})
                    primary = rules["primary"]
                    supporting = rules["supporting"]

                    csl = RectificationEngine._csl_significatorship_score(kp, primary, supporting)
                    dasha = RectificationEngine._dasha_on_date(birth_nak_lord, candidate_utc, ev_utc)
                    dasha_sc = RectificationEngine._dasha_connectivity_score(kp, dasha, primary, supporting)
                    lagna_sc = RectificationEngine._lagna_nakshatra_score(lagna_lon, primary, kp)"""
content = content.replace(loop_old, loop_new)

# 5. Score penalty
score_old = """                avg = total / len(event_dates)
                curve.append({"shift_minutes": step, "score": round(avg, 4)})"""

score_new = """                avg = total / len(event_dates)
                # Gravity penalty: deduct exponentially for straying from hospital record
                # e.g., 60 mins away = -0.15 score. This heavily anchors to recorded time if math is a tie.
                time_penalty = (abs(step) / 60.0) ** 1.5 * 0.15
                adjusted_score = max(0.0, avg - time_penalty)
                curve.append({"shift_minutes": step, "score": round(adjusted_score, 4)})"""
content = content.replace(score_old, score_new)

write_file("E:/ASTROLOGY AI/rectification_engine.py", content)
print("PATCH 3 APPLIED.")
