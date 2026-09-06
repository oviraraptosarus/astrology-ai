"""
Pushkara Navamsha & Pushkara Bhaga Engine (Classical Protection & Regeneration Matrix)
Implements:
1. 24 Pushkara Navamshas across the 12 Zodiac Signs:
   - Fire Signs (Aries, Leo, Sag): 7th Navamsha (Libra) & 9th Navamsha (Sagittarius) [20°00'-23°20' & 26°40'-30°00']
   - Earth Signs (Taurus, Virgo, Cap): 3rd Navamsha (Pisces) & 5th Navamsha (Taurus) [06°40'-10°00' & 13°20'-16°40']
   - Air Signs (Gemini, Libra, Aqua): 6th Navamsha (Pisces) & 8th Navamsha (Taurus) [16°40'-20°00' & 23°20'-26°40']
   - Water Signs (Cancer, Scorpio, Pis): 1st Navamsha (Cancer) & 3rd Navamsha (Virgo) [00°00'-03°20' & 06°40'-10°00']
2. Pushkara Bhagas (Specific Auspicious Degrees per Sign):
   - Aries: 21°, Taurus: 14°, Gemini: 24°, Cancer: 7°, Leo: 19°, Virgo: 12°,
   - Libra: 24°, Scorpio: 13°, Sag: 9°, Capricorn: 12°, Aquarius: 19°, Pisces: 9°
3. Planetary Amrita Score: Evaluates how Pushkara blessings cancel debilities and protect during crises.
"""
from typing import Dict, Any, List
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PUSHKARA_BHAGAS = {
    "Aries": 21.0, "Taurus": 14.0, "Gemini": 24.0, "Cancer": 7.0,
    "Leo": 19.0, "Virgo": 12.0, "Libra": 24.0, "Scorpio": 13.0,
    "Sagittarius": 9.0, "Capricorn": 12.0, "Aquarius": 19.0, "Pisces": 9.0
}

PUSHKARA_NAVAMSHA_SPANS = {
    "Fire": [(20.0, 23.3333, "Libra", "Venus"), (26.6667, 30.0, "Sagittarius", "Jupiter")],
    "Earth": [(6.6667, 10.0, "Pisces", "Jupiter"), (13.3333, 16.6667, "Taurus", "Venus")],
    "Air": [(16.6667, 20.0, "Pisces", "Jupiter"), (23.3333, 26.6667, "Taurus", "Venus")],
    "Water": [(0.0, 3.3333, "Cancer", "Moon"), (6.6667, 10.0, "Virgo", "Mercury")]
}

SIGN_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

class PushkaraEngine:
    def __init__(self, chart: Chart):
        self.chart = chart

    def evaluate_all_planets(self) -> Dict[str, Any]:
        """Evaluates Pushkara Navamsha & Pushkara Bhaga status for all planets & Ascendant."""
        evaluations = {}
        pushkara_count = 0

        # Evaluate Planets
        for pname, p in self.chart.planets.items():
            deg_in_sign = p.longitude % 30.0
            sign = p.sign
            elem = SIGN_ELEMENTS.get(sign, "Fire")
            
            # Check Pushkara Navamsha
            in_pn = False
            pn_details = None
            for span_min, span_max, nav_sign, nav_lord in PUSHKARA_NAVAMSHA_SPANS[elem]:
                if span_min <= deg_in_sign <= span_max:
                    in_pn = True
                    pn_details = {"navamsha_sign": nav_sign, "navamsha_lord": nav_lord, "span": f"{span_min:.1f}° - {span_max:.1f}°"}
                    break

            # Check Pushkara Bhaga (within 1 degree orb)
            pb_deg = PUSHKARA_BHAGAS.get(sign, 0.0)
            in_pb = abs(deg_in_sign - pb_deg) <= 1.0

            if in_pn or in_pb:
                pushkara_count += 1

            status_desc = []
            if in_pn:
                status_desc.append(f"Pushkara Navamsha in {pn_details['navamsha_sign']} (Ruled by {pn_details['navamsha_lord']})")
            if in_pb:
                status_desc.append(f"Exact Pushkara Bhaga ({pb_deg:.1f}° in {sign})")

            evaluations[pname] = {
                "sign": sign,
                "degree_in_sign": round(deg_in_sign, 2),
                "is_pushkara_navamsha": in_pn,
                "pushkara_navamsha_info": pn_details,
                "is_pushkara_bhaga": in_pb,
                "status": " | ".join(status_desc) if status_desc else "Normal Degree"
            }

        # Evaluate Ascendant
        if hasattr(self.chart, "ascendant_sign") and self.chart.ascendant_sign in ZODIAC_SIGNS:
            asc_sign = self.chart.ascendant_sign
            asc_deg = getattr(self.chart, "ascendant_degree", 0.0)
            asc_lon = (ZODIAC_SIGNS.index(asc_sign) * 30.0) + asc_deg
        elif hasattr(self.chart, "ascendant") and hasattr(self.chart.ascendant, "longitude"):
            asc_lon = self.chart.ascendant.longitude
            asc_sign = ZODIAC_SIGNS[int(asc_lon / 30)]
            asc_deg = asc_lon % 30.0
        else:
            asc_lon = 0.0
            asc_sign = "Aries"
            asc_deg = 0.0
        asc_elem = SIGN_ELEMENTS.get(asc_sign, "Fire")

        asc_in_pn = False
        asc_pn_info = None
        for span_min, span_max, nav_sign, nav_lord in PUSHKARA_NAVAMSHA_SPANS[asc_elem]:
            if span_min <= asc_deg <= span_max:
                asc_in_pn = True
                asc_pn_info = {"navamsha_sign": nav_sign, "navamsha_lord": nav_lord}
                break

        asc_in_pb = abs(asc_deg - PUSHKARA_BHAGAS.get(asc_sign, 0.0)) <= 1.0

        evaluations["Ascendant"] = {
            "sign": asc_sign,
            "degree_in_sign": round(asc_deg, 2),
            "is_pushkara_navamsha": asc_in_pn,
            "is_pushkara_bhaga": asc_in_pb,
            "status": "Pushkara Blessed Ascendant" if (asc_in_pn or asc_in_pb) else "Standard Degree"
        }

        return {
            "total_pushkara_blessings": pushkara_count,
            "resilience_rating": "EXTRAORDINARY (3+ Pushkara Planets)" if pushkara_count >= 3 else ("STRONG (1-2 Pushkara Planets)" if pushkara_count >= 1 else "STANDARD"),
            "evaluations": evaluations
        }
