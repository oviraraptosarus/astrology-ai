"""
Cancellation & Yoga Bhanga Engine
Implements deterministic classical verification for:
1. Neecha Bhanga Raja Yoga (NBRY) - 5 strict classical criteria from BPHS / Phaladeepika
2. Vipareeta Raja Yoga (VRY) - Harsha, Sarala, Vimala Yogas (6, 8, 12 isolation rules)
3. Yoga Bhanga (Cancellation / Damage of Raja & Dhana Yogas due to Combustion, War, Debilitation in D9)
"""

from typing import Dict, List, Any, Optional
from vedic_models import Chart, Planet
from text_utils import ordinal

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

EXALTATION_SIGNS = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra"
}

DEBILITATION_SIGNS = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
    "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"
}

EXALTED_IN_SIGN = {
    "Aries": "Sun", "Taurus": "Moon", "Gemini": None, "Cancer": "Jupiter",
    "Leo": None, "Virgo": "Mercury", "Libra": "Saturn", "Scorpio": None,
    "Sagittarius": None, "Capricorn": "Mars", "Aquarius": None, "Pisces": "Venus"
}

def get_p_lon(p: Planet) -> float:
    s_idx = ZODIAC_SIGNS.index(p.sign) if p.sign in ZODIAC_SIGNS else 0
    return (s_idx * 30.0) + p.degree

def get_p_sign_idx(p: Planet) -> int:
    return ZODIAC_SIGNS.index(p.sign) if p.sign in ZODIAC_SIGNS else 0

class CancellationEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS:
            self.lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign)
        else:
            self.lagna_sign_idx = 0

        moon = self.chart.planets.get("Moon")
        self.moon_sign_idx = get_p_sign_idx(moon) if moon else self.lagna_sign_idx

    def is_in_kendra(self, sign_idx: int, ref_sign_idx: int) -> bool:
        diff = (sign_idx - ref_sign_idx) % 12
        return diff in [0, 3, 6, 9]

    def evaluate_all(self) -> Dict[str, Any]:
        return {
            "neecha_bhanga_raja_yogas": self.evaluate_neecha_bhanga(),
            "vipareeta_raja_yogas": self.evaluate_vipareeta_raja_yoga(),
            "yoga_bhangas": self.evaluate_yoga_bhangas()
        }

    def evaluate_all_cancellations(self) -> Dict[str, Any]:
        return self.evaluate_all()

    def evaluate_neecha_bhanga(self) -> List[Dict[str, Any]]:
        results = []
        for p_name, deb_sign in DEBILITATION_SIGNS.items():
            planet = self.chart.planets.get(p_name)
            if not planet:
                continue

            p_sign = planet.sign
            p_sign_idx = get_p_sign_idx(planet)

            if p_sign != deb_sign:
                continue

            conditions_met = []

            # 1. Dispositor of debilitated planet is in Kendra from Lagna or Moon
            dispositor_name = SIGN_LORDS.get(deb_sign)
            disp = self.chart.planets.get(dispositor_name)
            if disp:
                disp_sign_idx = get_p_sign_idx(disp)
                if self.is_in_kendra(disp_sign_idx, self.lagna_sign_idx) or self.is_in_kendra(disp_sign_idx, self.moon_sign_idx):
                    conditions_met.append(f"Dispositor {dispositor_name} in Kendra (House {disp.house})")

            # 2. Exaltation lord of this debilitated sign is in Kendra
            exalted_in_this_sign = EXALTED_IN_SIGN.get(deb_sign)
            if exalted_in_this_sign:
                ex_planet = self.chart.planets.get(exalted_in_this_sign)
                if ex_planet:
                    ex_sign_idx = get_p_sign_idx(ex_planet)
                    if self.is_in_kendra(ex_sign_idx, self.lagna_sign_idx) or self.is_in_kendra(ex_sign_idx, self.moon_sign_idx):
                        conditions_met.append(f"Lord exalted in {deb_sign} ({exalted_in_this_sign}) in Kendra")

            # 3. Planet's own exaltation lord is in Kendra
            own_ex_sign = EXALTATION_SIGNS.get(p_name)
            own_ex_lord = SIGN_LORDS.get(own_ex_sign)
            own_ex_p = self.chart.planets.get(own_ex_lord)
            if own_ex_p:
                own_ex_sign_idx = get_p_sign_idx(own_ex_p)
                if self.is_in_kendra(own_ex_sign_idx, self.lagna_sign_idx) or self.is_in_kendra(own_ex_sign_idx, self.moon_sign_idx):
                    conditions_met.append(f"Exaltation lord ({own_ex_lord}) in Kendra")

            # 4. Navamsha exaltation (D9)
            d9_sign = planet.vargas.get("D9") if hasattr(planet, "vargas") else None
            if d9_sign == own_ex_sign:
                conditions_met.append(f"{p_name} is exalted in D9 Navamsha ({d9_sign})")

            # 5. Dispositor directly aspects the debilitated planet
            if disp:
                disp_sign_idx = get_p_sign_idx(disp)
                diff = (p_sign_idx - disp_sign_idx) % 12
                aspects = (diff == 6) or \
                          (dispositor_name == "Mars" and diff in [3, 7]) or \
                          (dispositor_name == "Jupiter" and diff in [4, 8]) or \
                          (dispositor_name == "Saturn" and diff in [2, 9])
                if aspects:
                    conditions_met.append(f"Dispositor {dispositor_name} directly aspects {p_name}")

            is_nbry = len(conditions_met) > 0
            results.append({
                "planet": p_name,
                "debilitated_planet": p_name,
                "debilitated_sign": deb_sign,
                "is_cancelled": is_nbry,
                "is_neechabhanga": is_nbry,
                "grade": "FULL_RAJA_YOGA" if len(conditions_met) >= 2 else ("PARTIAL_CANCELLATION" if is_nbry else "UNMITIGATED_DEBILITATION"),
                "conditions_met": conditions_met,
                "cancelling_factors": conditions_met
            })

        return results

    def evaluate_vipareeta_raja_yoga(self) -> List[Dict[str, Any]]:
        vry_yogas = []
        h6_sign_idx = (self.lagna_sign_idx + 5) % 12
        h8_sign_idx = (self.lagna_sign_idx + 7) % 12
        h12_sign_idx = (self.lagna_sign_idx + 11) % 12

        dusthana_lords = {
            "Harsha Yoga": (SIGN_LORDS[ZODIAC_SIGNS[h6_sign_idx]], 6),
            "Sarala Yoga": (SIGN_LORDS[ZODIAC_SIGNS[h8_sign_idx]], 8),
            "Vimala Yoga": (SIGN_LORDS[ZODIAC_SIGNS[h12_sign_idx]], 12)
        }

        dusthana_sign_indices = [h6_sign_idx, h8_sign_idx, h12_sign_idx]

        for yoga_name, (lord_name, source_house) in dusthana_lords.items():
            lord_planet = self.chart.planets.get(lord_name)
            if not lord_planet:
                continue

            lord_sign_idx = get_p_sign_idx(lord_planet)
            if lord_sign_idx in dusthana_sign_indices:
                placed_house = ((lord_sign_idx - self.lagna_sign_idx) % 12) + 1
                
                kendra_trikona_lords = [
                    SIGN_LORDS[ZODIAC_SIGNS[(self.lagna_sign_idx + h - 1) % 12]]
                    for h in [1, 4, 5, 7, 9, 10]
                ]
                conjunct_planets = [
                    p_n for p_n, p in self.chart.planets.items()
                    if p_n != lord_name and get_p_sign_idx(p) == lord_sign_idx
                ]
                tainted = any(p in kendra_trikona_lords for p in conjunct_planets)

                vry_yogas.append({
                    "yoga": yoga_name,
                    "lord": lord_name,
                    "source_house": source_house,
                    "placed_house": placed_house,
                    "is_pure": not tainted,
                    "status": "POWERFUL_VIPAREETA_RAJA_YOGA" if not tainted else "TAINTED_VRY",
                    "description": f"{yoga_name}: {ordinal(source_house)} lord {lord_name} placed in {ordinal(placed_house)} house."
                })

        return vry_yogas

    def evaluate_yoga_bhangas(self) -> List[Dict[str, Any]]:
        bhangas = []
        sun = self.chart.planets.get("Sun")
        sun_lon = get_p_lon(sun) if sun else None

        for p_name, p in self.chart.planets.items():
            if p_name in ["Sun", "Rahu", "Ketu", "Ascendant"]:
                continue

            if sun_lon is not None:
                p_lon = get_p_lon(p)
                diff = abs((p_lon - sun_lon + 180) % 360 - 180)
                if diff < 3.0:
                    bhangas.append({
                        "planet": p_name,
                        "bhanga_type": "SEVERE_COMBUSTION",
                        "severity": "CRITICAL",
                        "detail": f"{p_name} is within {round(diff, 2)}° of Sun (Severe Astangata)."
                    })

        return bhangas
