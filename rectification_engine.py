"""
KP-Correct Birth Time Rectification Engine
==========================================
Rebuilt on the REAL Krishnamurti Paddhati (KP) engine: Placidus cusps,
249 sub-lords, and 4-fold ABCD significators.

Classical KP rectification principle:
  The Cuspal Sub-Lord (CSL) of a house must be a significator of that
  house's events. For a given life event (marriage → 7th cusp), the
  correct birth time is the one where the 7th cusp sub-lord has
  ABCD-significatorship linkage to house 7 (occupancy, lordship, or
  stellar linkage).

Scoring per candidate time:
  For each life event → target house:
    1. CSL Significatorship : does the cusp sub-lord of the target house
       appear in that house's ABCD significator set? (0..1, strongest signal)
    2. Dasha Connectivity    : Vimshottari (Moon-keyed) lord at event date
       connected to event house. (weaker signal — Moon moves slowly)
    3. Lagna Fine Motion     : nakshatra-lord of lagna (coarse anchor).
  Weighted blend + peak-sharpness-aware confidence.
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from kp_engine import KPEngine


class RectificationEngine:

    EVENT_HOUSES = {
        "marriage": {"primary": 7, "supporting": [2, 7, 11]},
        "career_job": {"primary": 10, "supporting": [2, 6, 10, 11]},
        "property_purchase": {"primary": 4, "supporting": [4, 11, 12]},
        "birth_of_child": {"primary": 5, "supporting": [2, 5, 11]},
        "accident_surgery": {"primary": 8, "supporting": [6, 8, 12]},
        "financial_gain": {"primary": 11, "supporting": [2, 6, 11]},
        "loss": {"primary": 12, "supporting": [8, 12]},
        "education": {"primary": 4, "supporting": [4, 9, 11]},
        "travel_foreign": {"primary": 12, "supporting": [3, 9, 12]},
        "health_issue": {"primary": 6, "supporting": [6, 8]},
        "spiritual": {"primary": 9, "supporting": [9, 12]},
        "death_family": {"primary": 8, "supporting": [2, 7, 8]},
        "vehicle_purchase": {"primary": 4, "supporting": [4, 11]},
        "court_case": {"primary": 6, "supporting": [6, 8, 12]},
        "promotion": {"primary": 10, "supporting": [2, 6, 10, 11]},
    }

    DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
                   "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
    NAKSHATRA_LORDS = [
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
        "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
    ]

    @staticmethod
    def _dasha_on_date(birth_moon_nak_lord: str, birth_utc: datetime, event_utc: datetime) -> Dict[str, str]:
        years_elapsed = (event_utc - birth_utc).total_seconds() / (365.25 * 24 * 3600)
        if years_elapsed < 0:
            return {"mahadasha": "Unknown", "antardasha": "Unknown", "pratyantardasha": "Unknown"}
        try:
            start_idx = RectificationEngine.NAKSHATRA_LORDS.index(birth_moon_nak_lord)
        except ValueError:
            return {"mahadasha": "Unknown", "antardasha": "Unknown", "pratyantardasha": "Unknown"}

        elapsed = years_elapsed
        maha_idx = start_idx
        while elapsed > RectificationEngine.DASHA_YEARS[RectificationEngine.DASHA_SEQUENCE[maha_idx]]:
            elapsed -= RectificationEngine.DASHA_YEARS[RectificationEngine.DASHA_SEQUENCE[maha_idx]]
            maha_idx = (maha_idx + 1) % 9
        maha_lord = RectificationEngine.DASHA_SEQUENCE[maha_idx]
        maha_years = RectificationEngine.DASHA_YEARS[maha_lord]

        sub_seq = RectificationEngine.DASHA_SEQUENCE
        sub_elapsed = elapsed
        sub_idx = maha_idx
        while sub_elapsed > (maha_years * RectificationEngine.DASHA_YEARS[sub_seq[sub_idx]] / 120.0):
            sub_elapsed -= maha_years * RectificationEngine.DASHA_YEARS[sub_seq[sub_idx]] / 120.0
            sub_idx = (sub_idx + 1) % 9
        sub_lord = sub_seq[sub_idx]
        sub_years = maha_years * RectificationEngine.DASHA_YEARS[sub_lord] / 120.0

        praty_idx = sub_idx
        praty_elapsed = sub_elapsed
        while praty_elapsed > (sub_years * RectificationEngine.DASHA_YEARS[sub_seq[praty_idx]] / 120.0):
            praty_elapsed -= sub_years * RectificationEngine.DASHA_YEARS[sub_seq[praty_idx]] / 120.0
            praty_idx = (praty_idx + 1) % 9

        return {
            "mahadasha": sub_seq[maha_idx],
            "antardasha": sub_seq[sub_idx],
            "pratyantardasha": sub_seq[praty_idx]
        }

    @staticmethod
    def _csl_significatorship_score(kp_chart: Dict, event_house: int, supporting_houses: List[int] = None) -> float:
        """
        THE core KP signal: the event-house cusp sub-lord must be a
        significator of the event house via the ABCD matrix.

        kp_chart = KPEngine.calculate_kp_chart(...) output.
        Returns 0..1.
        """
        try:
            cusps = kp_chart["cusps"]
            abcd = kp_chart["abcd_significators"]

            cusp_sl = cusps[event_house - 1]["sub_lord"]
            supp = supporting_houses if supporting_houses else [event_house]
            
            score = 0.0
            for h in supp:
                sig = abcd.get(str(h), {})
                if cusp_sl in sig.get("level_a", []): score = max(score, 1.0)
                elif cusp_sl in sig.get("level_b", []): score = max(score, 0.85)
                elif cusp_sl in sig.get("level_c", []): score = max(score, 0.7)
                elif cusp_sl in sig.get("level_d", []): score = max(score, 0.6)
            return score
        except Exception:
            return 0.0

    @staticmethod
    def _lagna_nakshatra_score(lagna_lon: float, event_house: int, kp_chart: Dict) -> float:
        """
        Coarse anchor: lagna sub-lord (nakshatra lord) should relate to event house.
        Changes every ~53 min, so it gives a slow baseline, not fine signal.
        """
        lagna_lords = KPEngine.calculate_kp_lords(lagna_lon)
        lagna_sl = lagna_lords["sub_lord"]

        # Check if lagna sub-lord appears anywhere in the event house ABCD set
        abcd = kp_chart.get("abcd_significators", {})
        sig = abcd.get(str(event_house), {})
        all_sig = set(sig.get("level_a", []) + sig.get("level_b", []) + sig.get("level_c", []) + sig.get("level_d", []))
        return 1.0 if lagna_sl in all_sig else 0.0

    @staticmethod
    def _dasha_connectivity_score(kp_chart: Dict, dasha: Dict[str, str], event_house: int, supporting_houses: List[int] = None) -> float:
        """Dasha lords (Moon-keyed, slow-moving) vs event-house ABCD set."""
        abcd = kp_chart.get("abcd_significators", {})
        all_sig = set()
        supp = supporting_houses if supporting_houses else [event_house]
        for h in supp:
            sig = abcd.get(str(h), {})
            all_sig.update(sig.get("level_a", []) + sig.get("level_b", []) + sig.get("level_c", []) + sig.get("level_d", []))
        
        dasha_lords = {dasha["mahadasha"], dasha["antardasha"], dasha["pratyantardasha"]}
        overlap = dasha_lords & all_sig
        return len(overlap) / 3.0

    @staticmethod
    def rectify(birth_datetime: datetime, birth_lat: float, birth_lon: float,
                events: List[Dict], timezone_str: str = "Asia/Kolkata",
                search_minutes: int = 120, step_minutes: int = 4,
                include_double_transit: bool = True) -> Dict:
        import pytz
        from astrology_engine import calculate_chart_with_object

        if not events:
            return {"error": "No events provided for rectification."}

        tz = pytz.timezone(timezone_str)
        local_dt = tz.localize(birth_datetime)

        best_score = -1.0
        best_shift = 0.0
        best_scores_detail = None
        curve = []

        total_steps = (2 * search_minutes) // step_minutes + 1

        # Precompute universal event UTCs (independent of candidate)
        event_dates = []
        for ev in events:
            ev_date = datetime.strptime(ev["date"], "%d-%m-%Y")
            ev_utc = tz.localize(ev_date.replace(hour=12, minute=0)).astimezone(pytz.utc)
            event_dates.append((ev.get("type", "career_job"), ev["date"], ev_utc))

        for step in range(-search_minutes, search_minutes + 1, step_minutes):
            candidate_dt = local_dt + timedelta(minutes=step)
            candidate_utc = candidate_dt.astimezone(pytz.utc)

            try:
                # Full KP chart (Placidus cusps + ABCD matrix)
                kp = KPEngine.calculate_kp_chart(
                    candidate_dt.year, candidate_dt.month, candidate_dt.day,
                    candidate_dt.hour, candidate_dt.minute,
                    birth_lat, birth_lon, timezone_str
                )

                # Vedic chart for Moon nakshatra (dasha seed)
                cand_obj = calculate_chart_with_object(
                    year=candidate_dt.year, month=candidate_dt.month,
                    day=candidate_dt.day, hour=candidate_dt.hour,
                    minute=candidate_dt.minute, lat=birth_lat, lon=birth_lon,
                    tz_name=timezone_str
                )
                cand_chart = cand_obj[0] if isinstance(cand_obj, tuple) else cand_obj
                if cand_chart is None or "Moon" not in cand_chart.planets:
                    continue

                moon_deg = cand_chart.planets["Moon"].degree + (cand_chart.get_sign_index(cand_chart.planets["Moon"].sign) * 30)
                nak_idx = int(moon_deg // (360.0 / 27.0)) % 27
                birth_nak_lord = RectificationEngine.NAKSHATRA_LORDS[nak_idx]

                # Lagna longitude from KP cusps (1st cusp)
                lagna_lon = kp["cusps"][0]["longitude"]

                total = 0.0
                per_event = []
                for ev_type, ev_date_str, ev_utc in event_dates:
                    rules = RectificationEngine.EVENT_HOUSES.get(ev_type, {"primary": 1, "supporting": [1]})
                    primary = rules["primary"]
                    supporting = rules["supporting"]

                    csl = RectificationEngine._csl_significatorship_score(kp, primary, supporting)
                    dasha = RectificationEngine._dasha_on_date(birth_nak_lord, candidate_utc, ev_utc)
                    dasha_sc = RectificationEngine._dasha_connectivity_score(kp, dasha, primary, supporting)
                    lagna_sc = RectificationEngine._lagna_nakshatra_score(lagna_lon, primary, kp)

                    # CSL is the dominant KP signal: weight 0.6
                    ev_score = 0.6 * csl + 0.25 * dasha_sc + 0.15 * lagna_sc
                    total += ev_score
                    per_event.append({
                        "event_type": ev_type,
                        "date": ev_date_str,
                        "dasha": dasha,
                        "csl_score": round(csl, 2),
                        "dasha_score": round(dasha_sc, 2),
                        "lagna_score": round(lagna_sc, 2),
                        "total": round(ev_score, 2)
                    })

                avg = total / len(event_dates)
                # Gravity penalty: deduct exponentially for straying from hospital record
                # e.g., 60 mins away = -0.15 score. This heavily anchors to recorded time if math is a tie.
                time_penalty = (abs(step) / 60.0) ** 1.5 * 0.15
                adjusted_score = max(0.0, avg - time_penalty)
                curve.append({"shift_minutes": step, "score": round(adjusted_score, 4)})

                if avg > best_score:
                    best_score = avg
                    best_shift = step
                    best_scores_detail = per_event
            except Exception as e:
                # Keep first error for diagnostics
                if not hasattr(RectificationEngine, "_last_error"):
                    RectificationEngine._last_error = str(e)
                continue

        rectified_dt = local_dt + timedelta(minutes=best_shift)

        # Peak-sharpness-aware confidence:
        # A real peak (best >> neighbors) = high confidence. Flat curve = low.
        curve_sorted = sorted(curve, key=lambda x: x["score"], reverse=True)
        runner_up = curve_sorted[1]["score"] if len(curve_sorted) > 1 else 0.0
        peak_clearness = max(0.0, best_score - runner_up)
        scores_list = [c["score"] for c in curve]
        mean = sum(scores_list) / len(scores_list) if scores_list else 0.0
        sharpness = max(0.0, best_score - mean)

        # Confidence: base from best score + big bonus for sharp distinct peak
        confidence = min(95.0, 30.0 + (best_score * 40.0) + (sharpness * 60.0) + (peak_clearness * 20.0))

        diag_error = getattr(RectificationEngine, "_last_error", None)
        if hasattr(RectificationEngine, "_last_error"):
            del RectificationEngine._last_error

        prashna_fallback = None
        if confidence < 50.0:
            prashna_fallback = {
                "recommended": True,
                "reason": f"Rectification confidence is low ({round(confidence, 1)}%).",
                "guidance": "In classical Vedic astrology, when natal birth time cannot be calibrated definitively, Prashna Kundli (Horary chart of the exact moment the query is asked) should be used."
            }

        return {
            "original_birth_time": local_dt.strftime("%Y-%m-%d %H:%M %Z"),
            "rectified_birth_time": rectified_dt.strftime("%Y-%m-%d %H:%M %Z"),
            "shift_minutes": best_shift,
            "confidence": round(confidence, 1),
            "best_score": round(best_score, 4),
            "peak_sharpness": round(sharpness, 4),
            "candidate_count": total_steps,
            "event_scores": best_scores_detail,
            "score_curve": curve,
            "prashna_fallback": prashna_fallback,
            "debug_error": diag_error
        }


if __name__ == "__main__":
    print("KP-Correct Rectification Engine loaded.")