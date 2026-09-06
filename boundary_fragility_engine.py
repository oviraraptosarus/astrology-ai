"""
Discrete-Math Boundary Fragility & Perturbation Sensitivity Engine (Phase 3)
=============================================================================
Calculates exact proximity to discrete astrological boundaries and quantifies
numerical fragility across:
1. Rashi / Sign Boundaries (0° / 30°) - Rashi Sandhi (Bhavasandhi)
2. Nakshatra Boundaries (13°20' = 800') - Nakshatra Sandhi / Gandanta
3. Pada / Navamsha Boundaries (3°20' = 200') - Pada/Varga Sandhi
4. Kakshya Boundaries (3°45' = 225') - C.S. Patel Kakshya Sandhi
5. KP Sub-Lord Boundaries - Krishnamurti Sub-Lord Sandhi
6. D60 Shashtiamsha Boundaries (0°30' = 30') - Deep Karmic Micro-Cusp

Outputs explicit fragility classifications:
- HIGHLY_SENSITIVE_TO_INPUT_PRECISION (Proximity < 1 arcminute / 0.01667°)
- BORDERLINE (Proximity < 5 arcminutes / 0.08333°)
- STABLE (Proximity >= 5 arcminutes)
"""
from typing import Dict, Any, List
import math

from vedic_models import Chart, Planet
from kp_engine import KPEngine, VIMSHOTTARI_YEARS, TOTAL_YEARS

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

class BoundaryFragilityEngine:
    """Evaluates discrete mathematical fragility for any longitude or natal chart."""

    ARCSEC_DEG = 1.0 / 3600.0
    ARCMIN_DEG = 1.0 / 60.0

    @staticmethod
    def evaluate_longitude_fragility(longitude: float) -> Dict[str, Any]:
        lon = longitude % 360.0

        # 1. Rashi / Sign Boundary (every 30.0 deg)
        deg_in_sign = lon % 30.0
        dist_sign = min(deg_in_sign, 30.0 - deg_in_sign)

        # 2. Nakshatra Boundary (every 13.333333333333334 deg = 13°20')
        nak_span = 360.0 / 27.0
        deg_in_nak = lon % nak_span
        dist_nak = min(deg_in_nak, nak_span - deg_in_nak)

        # 3. Pada / Navamsha Boundary (every 3.3333333333333335 deg = 3°20')
        pada_span = nak_span / 4.0
        deg_in_pada = lon % pada_span
        dist_pada = min(deg_in_pada, pada_span - deg_in_pada)

        # 4. Kakshya Boundary (every 3.75 deg = 3°45')
        kakshya_span = 3.75
        deg_in_kakshya = lon % kakshya_span
        dist_kakshya = min(deg_in_kakshya, kakshya_span - deg_in_kakshya)

        # 5. D60 Shashtiamsha Boundary (every 0.5 deg = 30')
        d60_span = 0.5
        deg_in_d60 = lon % d60_span
        dist_d60 = min(deg_in_d60, d60_span - deg_in_d60)

        # 6. KP Sub-Lord Boundary
        nak_idx = int(lon / nak_span)
        fraction_in_nak = lon % nak_span
        degrees_per_year = nak_span / TOTAL_YEARS
        sl_idx = nak_idx % 9
        accumulated = 0.0
        sl_start = 0.0
        sl_end = 0.0
        for _ in range(9):
            span = VIMSHOTTARI_YEARS[sl_idx] * degrees_per_year
            if fraction_in_nak < (accumulated + span):
                sl_start = accumulated
                sl_end = accumulated + span
                break
            accumulated += span
            sl_idx = (sl_idx + 1) % 9
        dist_kp_sublord = min(fraction_in_nak - sl_start, sl_end - fraction_in_nak)

        # Find minimum distance across macro boundaries (Sign, Nakshatra, Pada)
        min_macro_dist = min(dist_sign, dist_nak, dist_pada)
        min_micro_dist = min(dist_kakshya, dist_kp_sublord, dist_d60)

        # Classify Fragility
        if min_macro_dist <= (1.0 * BoundaryFragilityEngine.ARCMIN_DEG):
            status = "HIGHLY_SENSITIVE_TO_INPUT_PRECISION"
            severity = "CRITICAL"
        elif min_macro_dist <= (5.0 * BoundaryFragilityEngine.ARCMIN_DEG):
            status = "BORDERLINE"
            severity = "HIGH"
        elif min_micro_dist <= (1.0 * BoundaryFragilityEngine.ARCMIN_DEG):
            status = "MICRO_BORDERLINE"
            severity = "MODERATE"
        else:
            status = "STABLE"
            severity = "LOW"

        # Check Gandanta (Junction of Water & Fire signs: Pisces-Aries, Cancer-Leo, Scorpio-Sagittarius)
        is_gandanta = False
        gandanta_zone = ""
        for g_deg, g_label in [(0.0, "Revati-Ashwini (Pisces-Aries)"), (120.0, "Ashlesha-Magha (Cancer-Leo)"), (240.0, "Jyeshtha-Mula (Scorpio-Sagittarius)")]:
            g_dist = min(abs(lon - g_deg), 360.0 - abs(lon - g_deg))
            if g_dist <= 0.8:
                is_gandanta = True
                gandanta_zone = f"{g_label} (Distance: {g_dist*60.0:.1f} arcmin)"
                break

        return {
            "longitude": round(lon, 4),
            "fragility_status": status,
            "severity": severity,
            "is_gandanta": is_gandanta,
            "gandanta_details": gandanta_zone if is_gandanta else "None",
            "boundary_distances_arcmin": {
                "sign_boundary_dist": round(dist_sign * 60.0, 2),
                "nakshatra_boundary_dist": round(dist_nak * 60.0, 2),
                "pada_boundary_dist": round(dist_pada * 60.0, 2),
                "kakshya_boundary_dist": round(dist_kakshya * 60.0, 2),
                "kp_sublord_boundary_dist": round(dist_kp_sublord * 60.0, 2),
                "d60_shashtiamsha_dist": round(dist_d60 * 60.0, 2)
            }
        }

    @staticmethod
    def evaluate_chart_fragility(chart: Chart) -> Dict[str, Any]:
        """Audits boundary fragility for all planets and Ascendant in the chart."""
        asc_lon = (ZODIAC_SIGNS.index(chart.ascendant_sign) * 30.0) + chart.ascendant_degree
        evaluations = {
            "Ascendant": BoundaryFragilityEngine.evaluate_longitude_fragility(asc_lon)
        }

        fragile_entities = []
        gandanta_entities = []

        for pname, p in chart.planets.items():
            res = BoundaryFragilityEngine.evaluate_longitude_fragility(p.longitude)
            evaluations[pname] = res
            if res["fragility_status"] in ["HIGHLY_SENSITIVE_TO_INPUT_PRECISION", "BORDERLINE"]:
                fragile_entities.append({
                    "entity": pname,
                    "status": res["fragility_status"],
                    "min_boundary_arcmin": min(res["boundary_distances_arcmin"].values())
                })
            if res["is_gandanta"]:
                gandanta_entities.append({
                    "entity": pname,
                    "details": res["gandanta_details"]
                })

        overall_rating = "HIGHLY_SENSITIVE" if any(f["status"] == "HIGHLY_SENSITIVE_TO_INPUT_PRECISION" for f in fragile_entities) else ("BORDERLINE" if len(fragile_entities) > 0 else "ROBUST_STABLE")

        return {
            "chart_boundary_fragility_rating": overall_rating,
            "fragile_entities_count": len(fragile_entities),
            "fragile_entities": fragile_entities,
            "gandanta_entities": gandanta_entities,
            "detailed_evaluations": evaluations
        }
