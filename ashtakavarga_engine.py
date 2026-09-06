"""
Ashtakavarga & Kakshya Micro-Transit Timing Engine
Implements Bhinnashtakavarga (BAV), Samudayashtakavarga (SAV),
3°45' Kakshya Micro-Transit Windows, and Trikona/Ekadhipatya Shodhana Reductions.
"""

from typing import Dict, List, Any
from vedic_models import Chart

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# 8 Kakshya Lords in fixed classical order of orbital speed
KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Ascendant"]
KAKSHYA_SPAN = 3.75  # 3 degrees 45 minutes

class AshtakavargaEngine:
    """
    Complete Ashtakavarga calculation, Kakshya micro-timing, and Shodhana reductions.
    """

    BAV_RULES = {
        "Sun": {
            "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
            "Moon": [3, 6, 10, 11],
            "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "Mercury": [3, 5, 6, 9, 10, 11, 12],
            "Jupiter": [5, 6, 9, 11],
            "Venus": [6, 7, 12],
            "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
            "Ascendant": [3, 4, 6, 10, 11, 12]
        },
        "Moon": {
            "Sun": [3, 6, 7, 8, 10, 11],
            "Moon": [1, 3, 6, 7, 10, 11],
            "Mars": [2, 3, 5, 6, 9, 10, 11],
            "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
            "Jupiter": [1, 4, 7, 8, 10, 11, 12],
            "Venus": [3, 4, 5, 7, 9, 10, 11],
            "Saturn": [3, 5, 6, 11],
            "Ascendant": [3, 6, 10, 11]
        },
        "Mars": {
            "Sun": [3, 5, 6, 10, 11],
            "Moon": [3, 6, 11],
            "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "Mercury": [3, 5, 6, 11],
            "Jupiter": [6, 10, 11, 12],
            "Venus": [6, 8, 11, 12],
            "Saturn": [1, 4, 7, 8, 9, 10, 11],
            "Ascendant": [1, 3, 6, 10, 11]
        },
        "Mercury": {
            "Sun": [5, 6, 9, 11, 12],
            "Moon": [2, 4, 6, 8, 10, 11],
            "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
            "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
            "Jupiter": [6, 8, 11, 12],
            "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
            "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
            "Ascendant": [1, 2, 4, 6, 8, 10, 11]
        },
        "Jupiter": {
            "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
            "Moon": [2, 5, 7, 9, 11],
            "Mars": [1, 2, 4, 7, 8, 10, 11],
            "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
            "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
            "Venus": [2, 5, 6, 9, 10, 11],
            "Saturn": [3, 5, 6, 12],
            "Ascendant": [1, 2, 4, 5, 6, 9, 10, 11]
        },
        "Venus": {
            "Sun": [8, 11, 12],
            "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
            "Mars": [3, 5, 6, 9, 11, 12],
            "Mercury": [3, 5, 6, 9, 11],
            "Jupiter": [5, 8, 9, 10, 11],
            "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
            "Saturn": [3, 4, 5, 8, 9, 10, 11],
            "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11]
        },
        "Saturn": {
            "Sun": [1, 2, 4, 7, 8, 10, 11],
            "Moon": [3, 6, 11],
            "Mars": [3, 5, 6, 10, 11, 12],
            "Mercury": [6, 8, 9, 10, 11, 12],
            "Jupiter": [5, 6, 11, 12],
            "Venus": [6, 11, 12],
            "Saturn": [3, 5, 6, 11],
            "Ascendant": [1, 3, 4, 6, 10, 11]
        }
    }

    @staticmethod
    def calculate_ashtakavarga(chart: Chart):
        """
        Calculates full Bhinnashtakavarga (BAV), Sarvashtakavarga (SAV), and Prastarashtakavarga.
        """
        chart.bhinna_ashtakavarga = {}
        chart.sarvashtakavarga = {i: 0 for i in range(1, 13)}
        chart.prastara_ashtakavarga = {}  # {target_planet: {house: {kakshya_lord: 0 or 1}}}

        reference_points = {"Ascendant": chart.ascendant_sign}
        for p_name, p in chart.planets.items():
            if p_name not in ["Rahu", "Ketu"]:
                reference_points[p_name] = p.sign

        asc_idx = chart.get_sign_index(chart.ascendant_sign)

        for target_planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            chart.bhinna_ashtakavarga[target_planet] = {i: 0 for i in range(1, 13)}
            chart.prastara_ashtakavarga[target_planet] = {
                i: {kl: 0 for kl in KAKSHYA_LORDS} for i in range(1, 13)
            }
            rules = AshtakavargaEngine.BAV_RULES.get(target_planet, {})

            for provider_name, provider_sign in reference_points.items():
                if provider_name not in rules:
                    continue

                provider_sign_idx = chart.get_sign_index(provider_sign)
                provider_house = ((provider_sign_idx - asc_idx) % 12) + 1

                for offset in rules[provider_name]:
                    target_house = ((provider_house - 1 + offset - 1) % 12) + 1
                    chart.bhinna_ashtakavarga[target_planet][target_house] += 1
                    chart.sarvashtakavarga[target_house] += 1
                    chart.prastara_ashtakavarga[target_planet][target_house][provider_name] = 1

        chart.ashtakavarga_is_partial = False

    @staticmethod
    def evaluate_kakshya_transit(chart: Chart, transiting_planet: str, transit_sign: str, degree_in_sign: float) -> Dict[str, Any]:
        """
        Evaluates the exact 3°45' Kakshya zone for a transiting planet.
        Returns whether the specific 3–5 day window is ACTIVATED by a natal bindu.
        """
        if not hasattr(chart, "prastara_ashtakavarga") or not chart.prastara_ashtakavarga:
            AshtakavargaEngine.calculate_ashtakavarga(chart)

        # 1. Determine active Kakshya (0 to 7)
        k_idx = int(degree_in_sign / KAKSHYA_SPAN)
        if k_idx >= 8:
            k_idx = 7
        kakshya_lord = KAKSHYA_LORDS[k_idx]
        k_start = k_idx * KAKSHYA_SPAN
        k_end = (k_idx + 1) * KAKSHYA_SPAN

        # 2. Find house from Ascendant
        asc_idx = chart.get_sign_index(chart.ascendant_sign)
        t_sign_idx = ZODIAC_SIGNS.index(transit_sign)
        house = ((t_sign_idx - asc_idx) % 12) + 1

        # 3. Check if Kakshya lord contributed a bindu in this house
        prastara = chart.prastara_ashtakavarga.get(transiting_planet, {}).get(house, {})
        has_bindu = prastara.get(kakshya_lord, 0) == 1

        bav_points = chart.bhinna_ashtakavarga.get(transiting_planet, {}).get(house, 0)
        sav_points = chart.sarvashtakavarga.get(house, 0)

        status = "KAKSHYA_ACTIVATED_HIGH_FRUCTIFICATION" if has_bindu else "KAKSHYA_DORMANT_REDUCTION"
        verdict = (
            f"Transiting {transiting_planet} is in {transit_sign} ({degree_in_sign:.2f}°) traversing the Kakshya of {kakshya_lord} "
            f"({k_start:.2f}° - {k_end:.2f}°). Natal Bindu is {'PRESENT (1)' if has_bindu else 'ABSENT (0)'}. "
            f"Total BAV in house {house} is {bav_points} bindus, SAV is {sav_points} bindus."
        )

        return {
            "transiting_planet": transiting_planet,
            "transit_sign": transit_sign,
            "degree_in_sign": round(degree_in_sign, 2),
            "house": house,
            "kakshya_index": k_idx + 1,
            "kakshya_lord": kakshya_lord,
            "kakshya_degree_range": f"{k_start:.2f}° - {k_end:.2f}°",
            "has_bindu": has_bindu,
            "total_bav": bav_points,
            "total_sav": sav_points,
            "status": status,
            "verdict": verdict
        }

    @staticmethod
    def calculate_trikona_shodhana(bav_array: List[int]) -> List[int]:
        """
        Executes Trikona Shodhana (Reduction 1: 1-5-9 sign trine elimination).
        bav_array has 12 integers representing signs Aries through Pisces.
        """
        reduced = list(bav_array)
        trines = [
            [0, 4, 8],   # Fire: Aries, Leo, Sagittarius
            [1, 5, 9],   # Earth: Taurus, Virgo, Capricorn
            [2, 6, 10],  # Air: Gemini, Libra, Aquarius
            [3, 7, 11]   # Water: Cancer, Scorpio, Pisces
        ]

        for trine in trines:
            min_val = min(reduced[i] for i in trine)
            for i in trine:
                reduced[i] -= min_val

        return reduced

    @staticmethod
    def calculate_ekadhipatya_shodhana(bav_trikona: List[int], chart) -> List[int]:
        """
        Executes Ekadhipatya Shodhana (Reduction 2: Dual sign lordship elimination)
        according to Brihat Parashara Hora Shastra (BPHS Ch. 68).
        Only applies to Mars (Aries/Scorpio), Mercury (Gemini/Virgo), 
        Jupiter (Sagittarius/Pisces), Venus (Taurus/Libra), and Saturn (Capricorn/Aquarius).
        Cancer (Moon) and Leo (Sun) do not have dual lordships.
        """
        reduced = list(bav_trikona)
        
        # Dual lordship sign index pairs: (Sign1, Sign2, Lord)
        dual_pairs = [
            (0, 7, "Mars"),        # Aries (0), Scorpio (7)
            (1, 6, "Venus"),       # Taurus (1), Libra (6)
            (2, 5, "Mercury"),     # Gemini (2), Virgo (5)
            (8, 11, "Jupiter"),    # Sagittarius (8), Pisces (11)
            (9, 10, "Saturn")      # Capricorn (9), Aquarius (10)
        ]
        
        # Determine planet occupation per sign index (0-11)
        occupied = {i: [] for i in range(12)}
        if chart and hasattr(chart, "planets"):
            for p_name, p_obj in chart.planets.items():
                if p_name not in ["Rahu", "Ketu", "Ascendant"]:
                    sign_idx = chart.get_sign_index(p_obj.sign)
                    occupied[sign_idx].append(p_name)
                    
        for s1, s2, lord in dual_pairs:
            b1 = reduced[s1]
            b2 = reduced[s2]
            p1_occ = len(occupied[s1]) > 0
            p2_occ = len(occupied[s2]) > 0
            
            # Rule A: If both signs have 0 bindus, no reduction
            if b1 == 0 and b2 == 0:
                continue
                
            # Rule B: Both signs occupied by planets -> no reduction
            if p1_occ and p2_occ:
                continue
                
            # Rule C: Neither sign occupied
            if not p1_occ and not p2_occ:
                if b1 == b2:
                    # Both equal: reduce both to 0
                    reduced[s1] = 0
                    reduced[s2] = 0
                elif b1 > b2:
                    # Unequal: smaller becomes 0, larger reduced to smaller value
                    if b2 == 0:
                        reduced[s1] = 0
                    else:
                        reduced[s1] = b2
                        reduced[s2] = 0
                else:
                    if b1 == 0:
                        reduced[s2] = 0
                    else:
                        reduced[s2] = b1
                        reduced[s1] = 0
            # Rule D: One sign occupied, one vacant
            elif p1_occ and not p2_occ:
                if b2 > b1:
                    # Vacant has more bindus than occupied: vacant reduced to occupied value
                    reduced[s2] = b1
                else:
                    # Vacant has less or equal bindus: vacant becomes 0
                    reduced[s2] = 0
            elif p2_occ and not p1_occ:
                if b1 > b2:
                    reduced[s1] = b2
                else:
                    reduced[s1] = 0
                    
        return reduced

    @staticmethod
    def calculate_shodhya_pinda(bav_reduced: List[int], chart, planet_name: str) -> Dict[str, Any]:
        """
        Calculates Rashi Pinda, Graha Pinda, and Shodhya Pinda (Total Pinda)
        according to classical BPHS multiplication constants.
        """
        # BPHS Classical Rashi Multipliers (Rashi Gunaka)
        RASHI_GUNAKAS = [7, 10, 8, 4, 10, 5, 7, 8, 9, 5, 11, 12]
        
        # BPHS Classical Graha Multipliers (Graha Gunaka)
        GRAHA_GUNAKAS = {
            "Sun": 5, "Moon": 5, "Mars": 8, "Mercury": 5,
            "Jupiter": 10, "Venus": 7, "Saturn": 5
        }
        
        # 1. Rashi Pinda = Sum(reduced_bindu[i] * Rashi_Gunaka[i])
        rashi_pinda = sum(bav_reduced[i] * RASHI_GUNAKAS[i] for i in range(12))
        
        # 2. Graha Pinda = Sum of bindus in signs occupied by planets * Graha_Gunaka
        graha_pinda = 0
        if chart and hasattr(chart, "planets"):
            for p, p_obj in chart.planets.items():
                if p in GRAHA_GUNAKAS:
                    s_idx = chart.get_sign_index(p_obj.sign)
                    graha_pinda += bav_reduced[s_idx] * GRAHA_GUNAKAS[p]
                    
        shodhya_pinda = rashi_pinda + graha_pinda
        
        return {
            "planet": planet_name,
            "reduced_bindus": bav_reduced,
            "rashi_pinda": rashi_pinda,
            "graha_pinda": graha_pinda,
            "shodhya_pinda": shodhya_pinda
        }
