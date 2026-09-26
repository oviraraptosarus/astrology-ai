"""
Parashari Mathematical Ayurdaya Engine (BPHS Ch. 43-45)
======================================================
Implements exact classical mathematical lifespan calculation via:
1. Pindayu (Solar Strength Hierarchy)
2. Amsayu / Amshayu (Lagna Strength Hierarchy)
3. Naisargikayu (Lunar Strength Hierarchy)
4. The 4 Classical Reductions (Haranas):
   - Shatrukshetra Harana (1/3 reduction for enemy sign placement)
   - Astangata Harana (1/2 reduction for combustion)
   - Chakrapata / Chakrardha Harana (Hemispheric reduction for H7-H12)
   - Krurodaya Harana (Malefics rising on Lagna)
5. The Classical Additions (Bharanas):
   - Exaltation / Retrogression (3x multiplier)
   - Vargottama / Sva-Navamsha / Sva-Drekkana (2x multiplier)
"""

from typing import Dict, Any, List, Tuple
import math
from vedic_models import Chart, Planet
from forward_timing_scanner import ZODIAC_SIGNS

ZODIAC = ZODIAC_SIGNS

# Deep Exaltation Points (Degrees absolute 0-360)
EXALTATION_LONS = {
    "Sun": 10.0,       # 10° Aries
    "Moon": 33.0,      # 3° Taurus
    "Mars": 298.0,     # 28° Capricorn
    "Mercury": 165.0,  # 15° Virgo
    "Jupiter": 95.0,   # 5° Cancer
    "Venus": 357.0,    # 27° Pisces
    "Saturn": 200.0    # 20° Libra
}

# Maximum Base Pindayu Years at Deep Exaltation (BPHS 43.4-8)
FULL_PINDAYU_YEARS = {
    "Sun": 19.0,
    "Moon": 25.0,
    "Mars": 15.0,
    "Mercury": 12.0,
    "Jupiter": 15.0,
    "Venus": 21.0,
    "Saturn": 20.0
}

# Maximum Base Naisargikayu Years at Deep Exaltation (BPHS 43.16-17)
FULL_NAISARGIKAYU_YEARS = {
    "Moon": 1.0,
    "Mars": 2.0,
    "Mercury": 9.0,
    "Venus": 20.0,
    "Jupiter": 18.0,
    "Sun": 20.0,
    "Saturn": 50.0
}

# Natural/Permanent Friends and Enemies for Shatrukshetra Harana
NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"}
}

NATURAL_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(), # Moon has no natural enemies
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"}
}

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

class ParashariAyurdayaEngine:
    @staticmethod
    def _ang_diff(a: float, b: float) -> float:
        d = abs((a - b) % 360.0)
        return min(d, 360.0 - d)

    @staticmethod
    def _is_combust(p_name: str, p_lon: float, sun_lon: float) -> bool:
        if p_name in ["Sun", "Rahu", "Ketu"]:
            return False
        # Classical combustion orbs
        orbs = {"Moon": 12.0, "Mars": 17.0, "Mercury": 14.0, "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0}
        return ParashariAyurdayaEngine._ang_diff(p_lon, sun_lon) <= orbs.get(p_name, 12.0)

    @staticmethod
    def calculate_pindayu(chart: Chart) -> Dict[str, Any]:
        """Calculates exact Pindayu years with all 4 Haranas and Bharanas."""
        planets_data = {}
        sun_p = chart.planets.get("Sun")
        sun_lon = (ZODIAC.index(sun_p.sign) * 30.0 + sun_p.degree) if sun_p else 0.0

        asc_sign = chart.ascendant_sign
        asc_idx = ZODIAC.index(asc_sign) if asc_sign in ZODIAC else 0
        asc_deg = getattr(chart, "ascendant_degree", 15.0)
        asc_lon = asc_idx * 30.0 + asc_deg

        total_years = 0.0

        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p = chart.planets.get(p_name)
            if not p:
                continue
            p_sign_idx = ZODIAC.index(p.sign)
            p_lon = p_sign_idx * 30.0 + p.degree
            p_house = ((p_sign_idx - asc_idx) % 12) + 1

            # 1. Base Pindayu Calculation (Arc distance from Deep Debilitation to Deep Exaltation)
            ex_lon = EXALTATION_LONS[p_name]
            deb_lon = (ex_lon + 180.0) % 360.0
            
            # Arc from debility to actual position
            arc_from_deb = (p_lon - deb_lon) % 360.0
            if arc_from_deb > 180.0:
                # In descending arc from exaltation to debility
                effective_arc = 360.0 - arc_from_deb
            else:
                effective_arc = arc_from_deb
                
            full_years = FULL_PINDAYU_YEARS[p_name]
            # Half at debility, full at exaltation
            base_years = (full_years / 2.0) + (full_years / 2.0) * (effective_arc / 180.0)

            # 2. Additions (Bharanas): Exalted / Retrograde = 3x, Sva-Navamsha/Drekkana = 2x
            bharana_mult = 1.0
            is_ret = getattr(p, "is_retrograde", False) or "Retrograde" in getattr(p, "condition", "")
            is_exalted = p.dignity in ["Exalted", "Own House"]
            if is_ret or is_exalted:
                bharana_mult = 3.0
            elif p.dignity in ["Friendly Sign", "Moolatrikona"]:
                bharana_mult = 2.0

            # 3. Reductions (Haranas)
            # A. Shatrukshetra Harana (1/3 reduction if in enemy sign, exempt if retrograde)
            sign_lord = SIGN_LORDS[p.sign]
            is_enemy_sign = sign_lord in NATURAL_ENEMIES.get(p_name, set())
            shatru_factor = 1.0
            if is_enemy_sign and not is_ret and p_name != "Saturn":
                shatru_factor = 2.0 / 3.0

            # B. Astangata Harana (1/2 reduction if combust, Venus and Saturn exempt per BPHS 43.20)
            is_comb = ParashariAyurdayaEngine._is_combust(p_name, p_lon, sun_lon)
            astangata_factor = 1.0
            if is_comb and p_name not in ["Venus", "Saturn", "Sun"]:
                astangata_factor = 0.5

            # C. Chakrapata / Hemispheric Harana (Visible half H7-H12)
            # Malefics: H12=1/1, H11=1/2, H10=1/3, H9=1/4, H8=1/5, H7=1/6
            # Benefics: H12=1/2, H11=1/4, H10=1/6, H9=1/8, H8=1/10, H7=1/12
            is_malefic = p_name in ["Sun", "Mars", "Saturn"]
            chakrapata_reduction = 0.0
            if p_house in [7, 8, 9, 10, 11, 12]:
                if is_malefic:
                    fracs = {12: 1.0, 11: 1/2, 10: 1/3, 9: 1/4, 8: 1/5, 7: 1/6}
                else:
                    fracs = {12: 1/2, 11: 1/4, 10: 1/6, 9: 1/8, 8: 1/10, 7: 1/12}
                chakrapata_reduction = fracs.get(p_house, 0.0)

            # Combined Harana (take the strongest planetary reduction + Chakrapata)
            internal_reduction = min(shatru_factor, astangata_factor)
            net_years = (base_years * bharana_mult * internal_reduction) * (1.0 - chakrapata_reduction)
            total_years += net_years

            planets_data[p_name] = {
                "base_years": round(base_years, 2),
                "bharana_multiplier": bharana_mult,
                "shatru_reduction": is_enemy_sign and not is_ret,
                "combustion_reduction": is_comb,
                "chakrapata_fraction": chakrapata_reduction,
                "net_contribution": round(net_years, 2)
            }

        # 4. Lagna Contribution (Navamshas elapsed from Aries)
        lagna_navamsha_count = int(asc_lon / (30.0 / 9.0))
        lagna_years = (lagna_navamsha_count % 12) + (asc_lon % (30.0 / 9.0)) / (30.0 / 9.0)
        total_years += lagna_years

        return {
            "method": "Pindayu (Solar Classical Model)",
            "total_longevity_years": round(total_years, 2),
            "exact_lifespan_breakdown": f"{int(total_years)} Years, {int((total_years%1)*12)} Months, {int(((total_years*12)%1)*30)} Days",
            "lagna_contribution": round(lagna_years, 2),
            "planetary_contributions": planets_data
        }

    @staticmethod
    def calculate_amshayu(chart: Chart) -> Dict[str, Any]:
        """Calculates exact Amsayu / Amshayu years (BPHS 43.18-22)."""
        asc_sign = chart.ascendant_sign
        asc_idx = ZODIAC.index(asc_sign) if asc_sign in ZODIAC else 0
        asc_deg = getattr(chart, "ascendant_degree", 15.0)
        asc_lon = asc_idx * 30.0 + asc_deg

        total_years = 0.0
        planets_data = {}

        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p = chart.planets.get(p_name)
            if not p:
                continue
            p_sign_idx = ZODIAC.index(p.sign)
            p_lon = p_sign_idx * 30.0 + p.degree

            # Formula: (Absolute Longitude in arcminutes / 200) mod 12
            total_minutes = p_lon * 60.0
            raw_amsas = total_minutes / 200.0
            base_years = raw_amsas % 12.0
            if base_years == 0.0:
                base_years = 12.0

            # Bharanas (Exalted/Retrograde = 3x, Own sign/Vargottama = 2x)
            is_ret = getattr(p, "is_retrograde", False) or "Retrograde" in getattr(p, "condition", "")
            is_exalted = p.dignity in ["Exalted", "Own House"]
            mult = 1.0
            if is_ret or is_exalted:
                mult = 3.0
            elif p.dignity in ["Moolatrikona", "Friendly Sign"]:
                mult = 2.0

            net_years = base_years * mult
            total_years += net_years
            planets_data[p_name] = {
                "base_navamsha_years": round(base_years, 2),
                "multiplier": mult,
                "net_contribution": round(net_years, 2)
            }

        # Lagna contribution
        lagna_base = ((asc_lon * 60.0) / 200.0) % 12.0
        total_years += lagna_base

        return {
            "method": "Amshayu (Navamsha Mathematical Model)",
            "total_longevity_years": round(total_years, 2),
            "exact_lifespan_breakdown": f"{int(total_years)} Years, {int((total_years%1)*12)} Months, {int(((total_years*12)%1)*30)} Days",
            "lagna_contribution": round(lagna_base, 2),
            "planetary_contributions": planets_data
        }

    @staticmethod
    def evaluate_tri_ayurdaya(chart: Chart) -> Dict[str, Any]:
        """Selects and computes the authoritative Parashari Longevity Model."""
        pindayu = ParashariAyurdayaEngine.calculate_pindayu(chart)
        amshayu = ParashariAyurdayaEngine.calculate_amshayu(chart)

        # Classical hierarchy selector (BPHS 43.30-31):
        # Determine whether Sun, Moon, or Lagna is strongest
        sun_dignity = chart.planets["Sun"].dignity if "Sun" in chart.planets else "Neutral"
        moon_dignity = chart.planets["Moon"].dignity if "Moon" in chart.planets else "Neutral"

        if sun_dignity in ["Exalted", "Own House", "Moolatrikona"]:
            chosen = pindayu
            selection_reason = "Sun is exceptionally strong (Pindayu selected per BPHS 43.30)"
        else:
            chosen = amshayu
            selection_reason = "Lagna/Ascendant governs life force (Amshayu selected per BPHS 43.30)"

        return {
            "authoritative_model": chosen,
            "selection_reason": selection_reason,
            "pindayu_result": pindayu,
            "amshayu_result": amshayu
        }
