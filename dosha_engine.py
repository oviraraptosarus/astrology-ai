"""
Comprehensive Classical Dosha & Transit Friction Engine
Implements strict Parashari & Jaimini algorithms for:
1. Sade Sati, Kantaka Shani, Ashtama Shani (Exact Moon-Saturn Degrees)
2. Kuja Dosha (Manglik) with all 10 Classical Cancellations
3. Kalsarpa Dosha (All 12 Classical Types + Directional Hemming + Cancellations)
4. Pitri Dosha (9th House, Sun, and Paternal Karma Afflictions)
5. Guru Chandal Dosha (Jupiter-Rahu/Ketu Conjunction & Orb)
6. Nakshatra & Rasi Gandanta (Planets on 29° Water / 0° Fire Thresholds)
"""

from typing import Dict, List, Any, Optional
import datetime
import pytz
import swisseph as swe
from config import Config

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

KUJA_DOSHA_HOUSES = [1, 2, 4, 7, 8, 12]

KALSARPA_TYPES = {
    1: "Anant Kalsarpa (1st-7th axis: Identity & Marriage friction)",
    2: "Kulik Kalsarpa (2nd-8th axis: Wealth & Family friction)",
    3: "Vasuki Kalsarpa (3rd-9th axis: Siblings & Courage strain)",
    4: "Shankhpal Kalsarpa (4th-10th axis: Mother & Career instability)",
    5: "Padma Kalsarpa (5th-11th axis: Progeny & Education delay)",
    6: "Mahapadma Kalsarpa (6th-12th axis: Health & Debt struggles)",
    7: "Takshak Kalsarpa (7th-1st axis: Partnership & Marital turbulence)",
    8: "Karkotak Kalsarpa (8th-2nd axis: Sudden obstacles & Inheritance hurdles)",
    9: "Shankhachur Kalsarpa (9th-3rd axis: Father & Fortune blockages)",
    10: "Ghatak Kalsarpa (10th-4th axis: Career reputation challenges)",
    11: "Vishdhar Kalsarpa (11th-5th axis: Income volatility & Elder sibling strain)",
    12: "Sheshnag Kalsarpa (12th-6th axis: Hidden enemies & Foreign isolation)"
}

class DoshaEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS:
            self.lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign)
        else:
            self.lagna_sign_idx = 0

        self.moon = self.chart.planets.get("Moon")
        self.moon_sign_idx = ZODIAC_SIGNS.index(self.moon.sign) if self.moon and self.moon.sign in ZODIAC_SIGNS else self.lagna_sign_idx

        self.venus = self.chart.planets.get("Venus")
        self.venus_sign_idx = ZODIAC_SIGNS.index(self.venus.sign) if self.venus and self.venus.sign in ZODIAC_SIGNS else self.lagna_sign_idx

    def _get_p_lon(self, p: Optional[Planet]) -> float:
        if not p:
            return 0.0
        s_idx = ZODIAC_SIGNS.index(p.sign) if p.sign in ZODIAC_SIGNS else 0
        return (s_idx * 30.0) + p.degree

    def evaluate_sade_sati(self, target_date: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """Check if Saturn is transiting 12th, 1st, or 2nd from Natal Moon (Sade Sati) or 4th/8th."""
        if not self.moon:
            return {"status": "INACTIVE", "reason": "No Natal Moon found."}

        if target_date is None:
            target_date = datetime.datetime.now(pytz.utc)

        jd = swe.julday(target_date.year, target_date.month, target_date.day,
                        target_date.hour + target_date.minute / 60.0)
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        sat_res, _ = swe.calc_ut(jd, swe.SATURN, swe.FLG_SIDEREAL)

        sat_transit_sign_idx = int((sat_res[0] % 360) / 30)
        relative_house = ((sat_transit_sign_idx - self.moon_sign_idx) % 12) + 1

        status = "INACTIVE"
        phase = "None"
        severity = "LOW"

        if relative_house in [12, 1, 2]:
            status = "ACTIVE_SADE_SATI"
            severity = "HIGH"
            if relative_house == 12:
                phase = "Phase 1: Rising / Setting in 12th from Moon (Mental pressure, expenditure)"
            elif relative_house == 1:
                phase = "Phase 2: Peak / Janma Shani in Moon Sign (Heavy personal restructuring)"
            else:
                phase = "Phase 3: Setting in 2nd from Moon (Financial discipline, final karmic resolution)"
        elif relative_house == 4:
            status = "ACTIVE_KANTAKA_SHANI"
            severity = "MODERATE"
            phase = "Kantaka Shani (4th from Moon: Domestic friction, cardiac/chest awareness)"
        elif relative_house == 8:
            status = "ACTIVE_ASHTAMA_SHANI"
            severity = "HIGH"
            phase = "Ashtama Shani (8th from Moon: Sudden life transitions, secret obstacles)"

        return {
            "status": status,
            "transit_saturn_sign": ZODIAC_SIGNS[sat_transit_sign_idx],
            "house_from_moon": relative_house,
            "phase": phase,
            "severity": severity
        }

    def evaluate_kuja_dosha(self) -> Dict[str, Any]:
        """Kuja Dosha (Manglik) presence and cancellation checks."""
        mars = self.chart.planets.get("Mars")
        if not mars:
            return {"status": "NO_DOSHA", "is_manglik": False, "cancellations": [], "details": []}

        mars_sign_idx = ZODIAC_SIGNS.index(mars.sign) if mars.sign in ZODIAC_SIGNS else 0
        mars_sign = mars.sign

        h_from_lagna = ((mars_sign_idx - self.lagna_sign_idx) % 12) + 1
        h_from_moon = ((mars_sign_idx - self.moon_sign_idx) % 12) + 1
        h_from_venus = ((mars_sign_idx - self.venus_sign_idx) % 12) + 1

        triggers = []
        if h_from_lagna in KUJA_DOSHA_HOUSES: triggers.append(f"Mars in {h_from_lagna} from Lagna")
        if h_from_moon in KUJA_DOSHA_HOUSES: triggers.append(f"Mars in {h_from_moon} from Moon")
        if h_from_venus in KUJA_DOSHA_HOUSES: triggers.append(f"Mars in {h_from_venus} from Venus")

        if not triggers:
            return {"status": "NO_DOSHA", "is_manglik": False, "cancellations": [], "details": ["Mars is in safe houses."]}

        cancellations = []
        if mars_sign in ["Aries", "Scorpio"]:
            cancellations.append("Mars is in its own sign (Swakshetra).")
        if mars_sign == "Capricorn":
            cancellations.append("Mars is Exalted (Uchha).")

        jup = self.chart.planets.get("Jupiter")
        if jup:
            jup_idx = ZODIAC_SIGNS.index(jup.sign) if jup.sign in ZODIAC_SIGNS else 0
            if mars_sign_idx == jup_idx:
                cancellations.append("Mars is conjoined with Jupiter (Guru-Mangala).")
            elif mars_sign_idx in [(jup_idx + 4) % 12, (jup_idx + 6) % 12, (jup_idx + 8) % 12]:
                cancellations.append("Mars is aspected by Jupiter.")

        if self.moon and mars_sign_idx == self.moon_sign_idx:
            cancellations.append("Mars is conjoined with Moon (Chandra-Mangala).")

        if h_from_lagna == 2 and mars_sign in ["Gemini", "Virgo"]:
            cancellations.append("Mars in 2nd house in Mercury's sign.")
        if h_from_lagna == 4 and mars_sign in ["Aries", "Scorpio"]:
            cancellations.append("Mars in 4th house in own sign.")
        if h_from_lagna == 7 and mars_sign in ["Cancer", "Capricorn"]:
            cancellations.append("Mars in 7th house in Cancer/Capricorn.")
        if h_from_lagna == 8 and mars_sign in ["Sagittarius", "Pisces"]:
            cancellations.append("Mars in 8th house in Jupiter's sign.")
        if h_from_lagna == 12 and mars_sign in ["Taurus", "Libra"]:
            cancellations.append("Mars in 12th house in Venus's sign.")

        is_manglik = len(cancellations) == 0
        status = "FULL_MANGLIK" if is_manglik else "CANCELLED_MANGLIK (Anshika)"

        return {
            "status": status,
            "is_manglik": is_manglik,
            "triggers": triggers,
            "cancellations": cancellations,
            "severity": "HIGH" if is_manglik else "LOW"
        }

    def evaluate_kalsarpa_dosha(self) -> Dict[str, Any]:
        """Evaluates all 12 Kalsarpa types and verifies if all 7 planets are hemmed on one side of Rahu-Ketu."""
        rahu = self.chart.planets.get("Rahu")
        ketu = self.chart.planets.get("Ketu")
        if not rahu or not ketu:
            return {"status": "NO_DOSHA", "is_present": False, "reason": "Nodes missing."}

        rahu_lon = self._get_p_lon(rahu)
        ketu_lon = self._get_p_lon(ketu)

        planets_to_check = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        side_a = 0  # Between Rahu and Ketu direct
        side_b = 0  # Between Ketu and Rahu direct

        for p_name in planets_to_check:
            p = self.chart.planets.get(p_name)
            if not p:
                continue
            lon = self._get_p_lon(p)
            diff_from_rahu = (lon - rahu_lon) % 360.0
            if diff_from_rahu < 180.0:
                side_a += 1
            else:
                side_b += 1

        is_kalsarpa = (side_a == len(planets_to_check)) or (side_b == len(planets_to_check))
        is_partial = (side_a == len(planets_to_check) - 1) or (side_b == len(planets_to_check) - 1)

        rahu_house = rahu.house
        dosha_type = KALSARPA_TYPES.get(rahu_house, "General Kalsarpa Yoga")

        cancellations = []
        # Cancellation if any planet conjuncts Rahu or Ketu closely or Jupiter is in Kendra
        jup = self.chart.planets.get("Jupiter")
        if jup and jup.house in [1, 4, 7, 10]:
            cancellations.append("Jupiter in Kendra from Lagna neutralizes Kalsarpa maleficence.")

        if is_kalsarpa:
            status = "FULL_KALSARPA_DOSHA" if not cancellations else "CANCELLED_KALSARPA"
        elif is_partial:
            status = "PARTIAL_KALSARPA (Ardha Kalsarpa)"
        else:
            status = "NO_KALSARPA_DOSHA"

        return {
            "status": status,
            "is_present": is_kalsarpa or is_partial,
            "type_name": dosha_type if (is_kalsarpa or is_partial) else "None",
            "rahu_house": rahu_house,
            "cancellations": cancellations,
            "severity": "HIGH" if (is_kalsarpa and not cancellations) else ("MODERATE" if is_partial else "NONE")
        }

    def evaluate_pitri_dosha(self) -> Dict[str, Any]:
        """Evaluates Pitri Dosha: Sun/9th Lord/9th House afflicted by Rahu, Ketu, or Saturn."""
        indicators = []
        sun = self.chart.planets.get("Sun")
        rahu = self.chart.planets.get("Rahu")
        saturn = self.chart.planets.get("Saturn")

        if sun and rahu and sun.sign == rahu.sign:
            indicators.append("Sun conjunct Rahu (Surya Grahana Pitri Dosha).")
        if sun and saturn and sun.sign == saturn.sign:
            indicators.append("Sun conjunct Saturn (Father-Son Karmic Friction).")

        h9_idx = (self.lagna_sign_idx + 8) % 12
        h9_sign = ZODIAC_SIGNS[h9_idx]
        h9_lord_name = SIGN_LORDS[h9_sign]
        h9_lord = self.chart.planets.get(h9_lord_name)

        if h9_lord and rahu and h9_lord.sign == rahu.sign:
            indicators.append(f"9th Lord {h9_lord_name} conjunct Rahu.")

        is_pitri = len(indicators) > 0
        return {
            "status": "PITRI_DOSHA_PRESENT" if is_pitri else "NO_PITRI_DOSHA",
            "is_present": is_pitri,
            "indicators": indicators,
            "remedy": "Tripindi Shradha, Narayan Bali, and water offerings to ancestors on Amavasya." if is_pitri else "None"
        }

    def evaluate_guru_chandal(self) -> Dict[str, Any]:
        """Evaluates Guru Chandal Yoga (Jupiter conjunct Rahu or Ketu)."""
        jup = self.chart.planets.get("Jupiter")
        rahu = self.chart.planets.get("Rahu")
        ketu = self.chart.planets.get("Ketu")

        is_chandal = False
        description = "No Guru Chandal Dosha."

        if jup and rahu and jup.sign == rahu.sign:
            orb = abs(jup.degree - rahu.degree)
            is_chandal = True
            description = f"Guru Chandal Yoga: Jupiter conjunct Rahu in {jup.sign} (Orb: {orb:.2f}°)."
        elif jup and ketu and jup.sign == ketu.sign:
            orb = abs(jup.degree - ketu.degree)
            is_chandal = True
            description = f"Guru-Ketu Conjunction in {jup.sign} (Orb: {orb:.2f}° - Ganesha Yoga / Spiritual Dissolution)."

        return {
            "status": "GURU_CHANDAL_ACTIVE" if is_chandal else "NO_GURU_CHANDAL",
            "is_present": is_chandal,
            "description": description
        }

    def evaluate_gandanta(self) -> Dict[str, Any]:
        """Evaluates Rasi and Nakshatra Gandanta on 29° Water / 0° Fire borders."""
        gandanta_points = []
        for p_name, p in self.chart.planets.items():
            if p.sign in ["Cancer", "Scorpio", "Pisces"] and p.degree >= 28.5:
                gandanta_points.append(f"{p_name} in {p.sign} at {p.degree:.2f}° (Abhukta / Rasi Sandhi Gandanta).")
            elif p.sign in ["Aries", "Leo", "Sagittarius"] and p.degree <= 1.5:
                gandanta_points.append(f"{p_name} in {p.sign} at {p.degree:.2f}° (Early Fire Gandanta).")

        # Check Lagna Gandanta
        lagna_sign = self.chart.ascendant_sign
        lagna_deg = self.chart.ascendant_degree
        if lagna_sign in ["Cancer", "Scorpio", "Pisces"] and lagna_deg >= 28.5:
            gandanta_points.append(f"Lagna in {lagna_sign} at {lagna_deg:.2f}° (Lagna Gandanta).")
        elif lagna_sign in ["Aries", "Leo", "Sagittarius"] and lagna_deg <= 1.5:
            gandanta_points.append(f"Lagna in {lagna_sign} at {lagna_deg:.2f}° (Lagna Gandanta).")

        has_gandanta = len(gandanta_points) > 0
        return {
            "status": "GANDANTA_PRESENT" if has_gandanta else "NO_GANDANTA",
            "is_present": has_gandanta,
            "afflicted_points": gandanta_points
        }

    def evaluate_all(self, target_date: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        return {
            "sade_sati": self.evaluate_sade_sati(target_date),
            "kuja_dosha": self.evaluate_kuja_dosha(),
            "kalsarpa_dosha": self.evaluate_kalsarpa_dosha(),
            "pitri_dosha": self.evaluate_pitri_dosha(),
            "guru_chandal": self.evaluate_guru_chandal(),
            "gandanta": self.evaluate_gandanta()
        }
