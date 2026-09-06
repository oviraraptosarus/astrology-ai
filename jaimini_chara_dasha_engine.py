"""
Jaimini Chara Dasha Engine (Classical K.N. Rao Method)
Calculates:
1. Chara Karakas (AK, AmK, BK, MK, PK, GK, DK) based on descending degrees.
2. Direct vs Indirect Dasha progression order based on Lagna sign.
3. Sign Dasha years (1 to 12 years) based on lord count and exaltation/debilitation.
4. Upapada Lagna (UL) and Arudha Lagna (AL).
5. Cross-validation timeline with Karaka activation.
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import pytz

from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Direct signs move Aries->Taurus->... ; Indirect move reverse
DIRECT_SIGNS = {"Aries", "Taurus", "Gemini", "Libra", "Scorpio", "Sagittarius"}

EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"
}

DEBILITATION_SIGNS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
    "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"
}

class JaiminiCharaDashaEngine:
    @staticmethod
    def calculate_chara_karakas(chart: Chart) -> Dict[str, Dict[str, Any]]:
        """Calculates 7 Chara Karakas: AK, AmK, BK, MK, PK, GK, DK by longitude within sign."""
        candidate_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        degrees = []
        for name in candidate_planets:
            p = chart.planets.get(name)
            if p:
                deg_in_sign = p.longitude % 30.0
                degrees.append((name, deg_in_sign, p.sign, p.longitude))

        degrees.sort(key=lambda x: x[1], reverse=True)
        karaka_names = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
        karaka_full = [
            "Atma Karaka (Self/Soul)",
            "Amatya Karaka (Career/Mind)",
            "Bhratri Karaka (Siblings/Guru)",
            "Matri Karaka (Mother/Emotions)",
            "Putra Karaka (Children/Intelligence)",
            "Gnati Karaka (Obstacles/Competition)",
            "Dara Karaka (Spouse/Partner)"
        ]

        result = {}
        for i, k in enumerate(karaka_names):
            if i < len(degrees):
                name, deg_in_sign, sign, lon = degrees[i]
                result[k] = {
                    "planet": name,
                    "degree_in_sign": round(deg_in_sign, 2),
                    "sign": sign,
                    "longitude": round(lon, 2),
                    "description": karaka_full[i]
                }
        return result

    @staticmethod
    def calculate_arudhas(chart: Chart) -> Dict[str, str]:
        """Calculates Arudha Lagna (AL) and Upapada Lagna (UL - Arudha of 12th house)."""
        lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign) if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else int(chart.ascendant.longitude / 30)
        
        # Arudha Lagna (AL)
        lagna_lord = SIGN_LORDS[ZODIAC_SIGNS[lagna_sign_idx]]
        lagna_lord_p = chart.planets.get(lagna_lord)
        lord_sign_idx = ZODIAC_SIGNS.index(lagna_lord_p.sign) if lagna_lord_p else lagna_sign_idx
        dist = (lord_sign_idx - lagna_sign_idx) % 12
        al_idx = (lord_sign_idx + dist) % 12
        # Exception: If AL falls in 1st or 7th from source, add 10 signs
        if al_idx == lagna_sign_idx or al_idx == (lagna_sign_idx + 6) % 12:
            al_idx = (al_idx + 9) % 12

        # Upapada Lagna (UL - 12th House Arudha)
        h12_idx = (lagna_sign_idx + 11) % 12
        h12_lord = SIGN_LORDS[ZODIAC_SIGNS[h12_idx]]
        h12_lord_p = chart.planets.get(h12_lord)
        h12_lord_sign_idx = ZODIAC_SIGNS.index(h12_lord_p.sign) if h12_lord_p else h12_idx
        dist_12 = (h12_lord_sign_idx - h12_idx) % 12
        ul_idx = (h12_lord_sign_idx + dist_12) % 12
        if ul_idx == h12_idx or ul_idx == (h12_idx + 6) % 12:
            ul_idx = (ul_idx + 9) % 12

        return {
            "Arudha_Lagna": ZODIAC_SIGNS[al_idx],
            "Upapada_Lagna": ZODIAC_SIGNS[ul_idx]
        }

    @staticmethod
    def resolve_jaimini_lord(sign: str, chart: Chart) -> Tuple[str, Planet]:
        """
        Resolves the presiding ruler for a sign in Jaimini Chara Dasha.
        Implements classical dual-lordship resolution for Scorpio (Mars vs Ketu)
        and Aquarius (Saturn vs Rahu) per Jaimini Sutras & K.N. Rao.
        """
        if sign not in ["Scorpio", "Aquarius"]:
            lord_name = SIGN_LORDS[sign]
            return lord_name, chart.planets.get(lord_name)

        if sign == "Scorpio":
            c1_name, c2_name = "Mars", "Ketu"
        else: # Aquarius
            c1_name, c2_name = "Saturn", "Rahu"

        p1 = chart.planets.get(c1_name)
        p2 = chart.planets.get(c2_name)

        if not p1 and not p2:
            return SIGN_LORDS[sign], None
        if not p1: return c2_name, p2
        if not p2: return c1_name, p1

        # Rule 1: If one co-lord is in the sign itself and the other is outside,
        # the outside lord determines the period (BPHS / K.N. Rao Rule 1)
        if p1.sign == sign and p2.sign != sign:
            return c2_name, p2
        if p2.sign == sign and p1.sign != sign:
            return c1_name, p1
        if p1.sign == sign and p2.sign == sign:
            return c1_name, p1

        # Rule 2: Conjunction with more planets gives greater strength
        conj1 = len(getattr(p1, "conjunct_with", []))
        conj2 = len(getattr(p2, "conjunct_with", []))
        if conj1 > conj2:
            return c1_name, p1
        elif conj2 > conj1:
            return c2_name, p2

        # Rule 3: Dignity strength (Exaltation > Own > Others)
        exalt1 = EXALTATION_SIGNS.get(c1_name) == p1.sign
        exalt2 = EXALTATION_SIGNS.get(c2_name) == p2.sign
        if exalt1 and not exalt2:
            return c1_name, p1
        if exalt2 and not exalt1:
            return c2_name, p2

        # Rule 4: Longitude within sign (Higher degree wins)
        deg1 = p1.longitude % 30.0
        deg2 = p2.longitude % 30.0
        if deg1 >= deg2:
            return c1_name, p1
        else:
            return c2_name, p2

    @staticmethod
    def calculate_sign_dasha_years(sign: str, chart: Chart) -> int:
        """Calculates Jaimini Chara Dasha duration (1-12 years) for a given sign (K.N. Rao method)."""
        sign_idx = ZODIAC_SIGNS.index(sign)
        lord, lord_p = JaiminiCharaDashaEngine.resolve_jaimini_lord(sign, chart)
        if not lord_p:
            return 7

        lord_sign_idx = ZODIAC_SIGNS.index(lord_p.sign)
        is_direct = sign in DIRECT_SIGNS

        if is_direct:
            years = (lord_sign_idx - sign_idx) % 12
        else:
            years = (sign_idx - lord_sign_idx) % 12

        if years == 0:
            years = 12

        # Exaltation (+1 year, max 12) / Debilitation (-1 year, min 1)
        if EXALTATION_SIGNS.get(lord) == lord_p.sign and years < 12:
            years += 1
        elif DEBILITATION_SIGNS.get(lord) == lord_p.sign and years > 1:
            years -= 1

        return years

    @classmethod
    def calculate_chara_dasha_timeline(cls, chart: Chart, birth_time_utc: datetime, cycles: int = 1) -> List[Dict[str, Any]]:
        """Generates the full Jaimini Chara Dasha timeline."""
        lagna_sign = chart.ascendant_sign if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else ZODIAC_SIGNS[int(chart.ascendant.longitude / 30)]
        lagna_idx = ZODIAC_SIGNS.index(lagna_sign)
        
        is_direct = lagna_sign in DIRECT_SIGNS
        karakas = cls.calculate_chara_karakas(chart)
        arudhas = cls.calculate_arudhas(chart)

        # Build 12-sign sequence
        if is_direct:
            sign_seq = [ZODIAC_SIGNS[(lagna_idx + i) % 12] for i in range(12)]
        else:
            sign_seq = [ZODIAC_SIGNS[(lagna_idx - i) % 12] for i in range(12)]

        timeline = []
        curr_dt = birth_time_utc
        if curr_dt.tzinfo is None:
            curr_dt = pytz.utc.localize(curr_dt)

        for cycle in range(cycles):
            for sign in sign_seq:
                duration_years = cls.calculate_sign_dasha_years(sign, chart)
                end_dt = curr_dt + timedelta(days=duration_years * 365.25)
                
                # Identify planets and Karakas present in this sign
                planets_in_sign = [pname for pname, p in chart.planets.items() if p.sign == sign]
                karakas_in_sign = [k for k, v in karakas.items() if v["sign"] == sign]
                
                flags = []
                if sign == arudhas["Arudha_Lagna"]:
                    flags.append("Arudha Lagna (AL) Activated")
                if sign == arudhas["Upapada_Lagna"]:
                    flags.append("Upapada Lagna (UL) Activated [Marriage/Spouse]")
                if "DK" in karakas_in_sign:
                    flags.append("Dara Karaka (DK) Present [Marriage/Partnership]")
                if "AK" in karakas_in_sign:
                    flags.append("Atma Karaka (AK) Present [Soul Purpose/Health]")
                if "AmK" in karakas_in_sign:
                    flags.append("Amatya Karaka (AmK) Present [Career Rise]")

                timeline.append({
                    "sign": sign,
                    "duration_years": duration_years,
                    "start": curr_dt.strftime("%Y-%m-%d"),
                    "end": end_dt.strftime("%Y-%m-%d"),
                    "planets": planets_in_sign,
                    "karakas": karakas_in_sign,
                    "special_activations": flags
                })
                curr_dt = end_dt

        return timeline
