"""
Deterministic Ayurdaya & Longevity Calculation Engine
Implements strict classical mathematical algorithms from:
1. Jaimini Sutras (3-Pair Longevity Method + Kakshya Vriddhi/Hrasa Tier Arithmetic)
2. Parashara (BPHS Ch 44-46 Maraka, Badhaka, Chamara Yoga & Ayur Karaka 8th House Rules)
"""

from typing import Dict, List, Any, Optional
from vedic_models import Chart, Planet

ZODIAC = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

SIGN_MODALITY = {
    "Aries": "Movable", "Taurus": "Fixed", "Gemini": "Dual",
    "Cancer": "Movable", "Leo": "Fixed", "Virgo": "Dual",
    "Libra": "Movable", "Scorpio": "Fixed", "Sagittarius": "Dual",
    "Capricorn": "Movable", "Aquarius": "Fixed", "Pisces": "Dual"
}

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Jaimini 3-Pair Matrix (Jaimini Sutras 2.1.15-25)
PAIR_MATRIX = {
    ("Movable", "Movable"): "Deerghayu (Long: 66-100+)",
    ("Movable", "Fixed"):   "Madhyayu (Medium: 33-66)",
    ("Movable", "Dual"):    "Alpayu (Short: 0-33)",
    ("Fixed", "Movable"):   "Madhyayu (Medium: 33-66)",
    ("Fixed", "Fixed"):     "Alpayu (Short: 0-33)",
    ("Fixed", "Dual"):      "Deerghayu (Long: 66-100+)",
    ("Dual", "Movable"):    "Alpayu (Short: 0-33)",
    ("Dual", "Fixed"):      "Deerghayu (Long: 66-100+)",
    ("Dual", "Dual"):       "Madhyayu (Medium: 33-66)",
}

RANGE_BY_CATEGORY = {
    "Deerghayu": "66 to 100+ Years",
    "Madhyayu":  "33 to 66 Years",
    "Alpayu":    "0 to 33 Years"
}

TIER_ORDER = ["Alpayu", "Madhyayu", "Deerghayu"]

class LongevityEngine:
    @staticmethod
    def calculate_jaimini_3_pairs(chart: Chart) -> Dict[str, Any]:
        """
        Calculates Jaimini 3-Pair Longevity and applies classical Kakshya Vriddhi/Hrasa:
        Pair 1: Lagna Lord Sign vs 8th Lord Sign
        Pair 2: Lagna Sign vs Moon Sign
        Pair 3: Lagna Sign vs Saturn Sign (Ayush Karaka)
        """
        lagna_sign = chart.ascendant_sign
        lagna_mod = SIGN_MODALITY.get(lagna_sign, "Movable")

        # Lagna Lord
        lagna_lord_name = SIGN_LORDS.get(lagna_sign)
        lagna_lord_p = chart.planets.get(lagna_lord_name)
        lagna_lord_sign = lagna_lord_p.sign if lagna_lord_p else lagna_sign
        lagna_lord_mod = SIGN_MODALITY.get(lagna_lord_sign, "Movable")

        # 8th House & 8th Lord
        l_idx = ZODIAC.index(lagna_sign)
        h8_sign = ZODIAC[(l_idx + 7) % 12]
        h8_lord_name = SIGN_LORDS.get(h8_sign)
        h8_lord_p = chart.planets.get(h8_lord_name)
        h8_lord_sign = h8_lord_p.sign if h8_lord_p else h8_sign
        h8_lord_mod = SIGN_MODALITY.get(h8_lord_sign, "Movable")

        # Moon Sign
        moon_p = chart.planets.get("Moon")
        moon_sign = moon_p.sign if moon_p else lagna_sign
        moon_mod = SIGN_MODALITY.get(moon_sign, "Movable")

        # Ayush Karaka Saturn Sign
        saturn_p = chart.planets.get("Saturn")
        sat_sign = saturn_p.sign if saturn_p else lagna_sign
        sat_mod = SIGN_MODALITY.get(sat_sign, "Movable")

        # Evaluate 3 Pairs
        p1_res = PAIR_MATRIX.get((lagna_lord_mod, h8_lord_mod), "Madhyayu")
        p2_res = PAIR_MATRIX.get((lagna_mod, moon_mod), "Madhyayu")
        p3_res = PAIR_MATRIX.get((lagna_mod, sat_mod), "Madhyayu")

        votes = [p1_res.split()[0], p2_res.split()[0], p3_res.split()[0]]

        counts = {cat: votes.count(cat) for cat in ["Alpayu", "Madhyayu", "Deerghayu"]}
        raw_winner = "Madhyayu"
        for cat, c in counts.items():
            if c >= 2:
                raw_winner = cat
                break
        else:
            raw_winner = votes[0]

        # -------------------------------------------------------------
        # Classical Kakshya Vriddhi (Increases) & Hrasa (Reductions)
        # -------------------------------------------------------------
        vriddhi_points = 0
        hrasa_points = 0
        adjustments = []

        # 1. Ayur Karaka Saturn in the 8th House (Jaimini Sutra 2.1.28 & BPHS):
        # Saturn in the 8th house gives supreme longevity preservation (+1 Kakshya Vriddhi)
        if saturn_p and saturn_p.house == 8:
            vriddhi_points += 1
            adjustments.append("Ayur Karaka Saturn in 8th House (+1 Kakshya Vriddhi - Jaimini Sutra 2.1.28)")

        # 2. Jupiter in Own Sign / Moolatrikona / Exalted (BPHS Ch 44):
        jup = chart.planets.get("Jupiter")
        if jup and (jup.dignity in ["Own House", "Moolatrikona", "Exalted"]):
            vriddhi_points += 1
            adjustments.append(f"Jupiter {jup.dignity} in {jup.sign} (House {jup.house}) (+1 Kakshya Vriddhi - Protective Grace)")

        # 3. Benefics in Kendra (Moon & Mercury in 7th - Chamara Yoga influence):
        mer = chart.planets.get("Mercury")
        if moon_p and mer and moon_p.house in [1, 4, 7, 10] and mer.house in [1, 4, 7, 10]:
            vriddhi_points += 1
            adjustments.append("Benefics in Kendra / Chamara Yoga configuration (+1 Kakshya Vriddhi - BPHS 35.15)")

        # 4. Check Hrasa (Severe uncancelled 8th house afflictions):
        h8_occupants = [name for name, p in chart.planets.items() if p.house == 8 and name in ["Mars", "Sun", "Rahu", "Ketu"]]
        if len(h8_occupants) >= 2 and not (saturn_p and saturn_p.house == 8):
            hrasa_points += 1
            adjustments.append(f"Multiple Malefics in 8th House ({', '.join(h8_occupants)}) (-1 Kakshya Hrasa)")

        # Apply net tier upgrade
        curr_tier_idx = TIER_ORDER.index(raw_winner)
        net_shift = vriddhi_points - hrasa_points
        final_tier_idx = min(2, max(0, curr_tier_idx + (1 if net_shift > 0 else (-1 if net_shift < 0 else 0))))
        final_category = TIER_ORDER[final_tier_idx]

        pair_evals = {
            "Pair 1 (Lagna Lord vs 8th Lord)": f"{lagna_lord_name} in {lagna_lord_sign} ({lagna_lord_mod}) vs {h8_lord_name} in {h8_lord_sign} ({h8_lord_mod}) -> {p1_res}",
            "Pair 2 (Lagna vs Moon)": f"{lagna_sign} ({lagna_mod}) vs {moon_sign} ({moon_mod}) -> {p2_res}",
            "Pair 3 (Lagna vs Saturn)": f"{lagna_sign} ({lagna_mod}) vs {sat_sign} ({sat_mod}) -> {p3_res}"
        }

        return {
            "bracket": final_category,
            "raw_mathematical_baseline": raw_winner,
            "final_adjusted_category": final_category,
            "estimated_range": RANGE_BY_CATEGORY.get(final_category, "66 to 100+ Years"),
            "pair_evaluations": pair_evals,
            "pair_1_lagna_lord_vs_8th_lord": {
                "lagna_lord": f"{lagna_lord_name} in {lagna_lord_sign} ({lagna_lord_mod})",
                "8th_lord": f"{h8_lord_name} in {h8_lord_sign} ({h8_lord_mod})",
                "result": p1_res
            },
            "pair_2_lagna_vs_moon": {
                "lagna": f"{lagna_sign} ({lagna_mod})",
                "moon": f"{moon_sign} ({moon_mod})",
                "result": p2_res
            },
            "pair_3_lagna_vs_saturn": {
                "lagna": f"{lagna_sign} ({lagna_mod})",
                "saturn": f"{sat_sign} ({sat_mod})",
                "result": p3_res
            },
            "raw_votes": votes,
            "jaimini_consensus_category": raw_winner,
            "kakshya_adjustments": adjustments
        }

    @staticmethod
    def calculate_jaimini_longevity_span(chart: Chart) -> Dict[str, Any]:
        """Backward-compatible alias for unit test suites."""
        return LongevityEngine.calculate_jaimini_3_pairs(chart)

    @staticmethod
    def identify_marakas(chart: Chart) -> Dict[str, Any]:
        """Identifies 2nd & 7th Maraka Lords, 11th Badhaka Lord, and occupants."""
        asc_sign = chart.ascendant_sign
        asc_idx = ZODIAC.index(asc_sign) if asc_sign in ZODIAC else 0

        h2_sign = ZODIAC[(asc_idx + 1) % 12]
        h7_sign = ZODIAC[(asc_idx + 6) % 12]
        h8_sign = ZODIAC[(asc_idx + 7) % 12]

        h2_lord = SIGN_LORDS.get(h2_sign)
        h7_lord = SIGN_LORDS.get(h7_sign)
        h8_lord = SIGN_LORDS.get(h8_sign)

        modality = SIGN_MODALITY.get(asc_sign, "Movable")
        if modality == "Movable":
            badhaka_house = 11
        elif modality == "Fixed":
            badhaka_house = 9
        else:
            badhaka_house = 7

        badhaka_sign = ZODIAC[(asc_idx + badhaka_house - 1) % 12]
        badhaka_lord = SIGN_LORDS.get(badhaka_sign)

        h2_occupants = [name for name, p in chart.planets.items() if p.house == 2]
        h7_occupants = [name for name, p in chart.planets.items() if p.house == 7]
        h8_occupants = [name for name, p in chart.planets.items() if p.house == 8]

        return {
            "2nd_maraka_lord": f"{h2_lord} ({h2_sign})",
            "7th_maraka_lord": f"{h7_lord} ({h7_sign})",
            "8th_longevity_lord": f"{h8_lord} ({h8_sign})",
            "badhaka_lord": f"{badhaka_lord} (House {badhaka_house} - {badhaka_sign})",
            "2nd_house_occupants": h2_occupants,
            "7th_house_occupants": h7_occupants,
            "8th_house_occupants": h8_occupants
        }
