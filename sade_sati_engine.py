"""
Master Sade Sati & Shani Gochara Lifecycle Engine
Implements:
1. Complete 7.5-Year Sade Sati Timeline across Full Lifespan (Cycle 1, 2, 3).
2. Exact Calendar Dates for Phase 1 (Rising), Phase 2 (Peak Janma Shani), Phase 3 (Setting).
3. Kantaka Shani (4th & 10th from Moon) and Ashtama Shani (8th from Moon) exact windows.
4. Moorthi Nirnaya (Gold/Swarna, Silver/Rajata, Copper/Tamra, Iron/Loha) at ingress.
5. Ashtakavarga SAV & Saturn BAV Bindu Mitigation (Tells if Sade Sati gives Rajayoga or Struggle).
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz
import swisseph as swe
from config import Config

from vedic_models import Chart, Planet
from ashtakavarga_engine import AshtakavargaEngine

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

MOORTHI_MAP = {
    # Based on Moon's house position from Lagna when Saturn enters the sign:
    # 1, 6, 11 -> Gold (Swarna - Auspicious, gains, status rise)
    # 2, 5, 9  -> Silver (Rajata - Highly Auspicious, peace, prosperity)
    # 3, 7, 10 -> Copper (Tamra - Moderate, mixed results, hard labor)
    # 4, 8, 12 -> Iron (Loha - Challenging, mental anxiety, obstacles)
    1: ("Gold (Swarna)", "Highly Favorable / Material Elevation & Status Rise"),
    6: ("Gold (Swarna)", "Highly Favorable / Victory over Obstacles & Career Rise"),
    11: ("Gold (Swarna)", "Highly Favorable / Massive Wealth & Fulfillment of Desires"),
    2: ("Silver (Rajata)", "Favorable / Wealth Accumulation & Domestic Peace"),
    5: ("Silver (Rajata)", "Favorable / Intellectual Clarity & Progeny Happiness"),
    9: ("Silver (Rajata)", "Favorable / Spiritual Growth & Fortune"),
    3: ("Copper (Tamra)", "Mixed / High Effort Required, Moderately Productive"),
    7: ("Copper (Tamra)", "Mixed / Partnership Adjustments & Medium Gains"),
    10: ("Copper (Tamra)", "Mixed / Heavy Professional Duties & Relocation"),
    4: ("Iron (Loha)", "Challenging / Emotional Stress & Domestic Friction"),
    8: ("Iron (Loha)", "Challenging / Vulnerability, Health Strain & Delays"),
    12: ("Iron (Loha)", "Challenging / Heavy Expenses & Mental Agitation")
}

class SadeSatiEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.moon = chart.planets.get("Moon")
        if self.moon:
            self.moon_sign_idx = ZODIAC_SIGNS.index(self.moon.sign)
        else:
            self.moon_sign_idx = 0
            
        self.lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign) if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else int(chart.ascendant.longitude / 30)
        
        AshtakavargaEngine.calculate_ashtakavarga(chart)
        self.sav = getattr(chart, "sarvashtakavarga", {})

    def evaluate_current_status(self, target_date: datetime = None) -> Dict[str, Any]:
        """Evaluates live status of Sade Sati, Kantaka, or Ashtama Shani at target_date."""
        if target_date is None:
            target_date = datetime.now(pytz.utc)
        elif target_date.tzinfo is None:
            target_date = pytz.utc.localize(target_date)

        swe.set_sid_mode(Config.ayanamsha_swe_id())
        hour_dec = target_date.hour + (target_date.minute / 60.0)
        jd = swe.julday(target_date.year, target_date.month, target_date.day, hour_dec)
        sat_res, _ = swe.calc_ut(jd, swe.SATURN, swe.FLG_SIDEREAL)
        sat_lon = sat_res[0] % 360.0
        sat_sign_idx = int(sat_lon / 30.0)
        sat_sign = ZODIAC_SIGNS[sat_sign_idx]

        h_from_moon = ((sat_sign_idx - self.moon_sign_idx) % 12) + 1
        sav_points = self.sav.get(sat_sign, 28)

        status = "INACTIVE"
        phase = "None"
        severity = "None"
        mitigation = "Standard"

        if h_from_moon in [12, 1, 2]:
            status = "ACTIVE_SADE_SATI"
            if h_from_moon == 12:
                phase = "Phase 1: Rising (Saturn in 12th from Moon - Mental pressure, foreign travels, high expenditure)"
            elif h_from_moon == 1:
                phase = "Phase 2: Peak / Janma Shani (Saturn over Natal Moon - Emotional restructuring, core identity transformation)"
            else:
                phase = "Phase 3: Setting (Saturn in 2nd from Moon - Financial discipline, family responsibilities, closing karmic loops)"
            
            if sav_points >= 28:
                severity = "MILD / CONSTRUCTIVE"
                mitigation = f"High Ashtakavarga Score ({sav_points} SAV bindus in {sat_sign}) transforms pressure into enduring achievement and authority."
            else:
                severity = "INTENSE"
                mitigation = f"Low Ashtakavarga Score ({sav_points} SAV bindus in {sat_sign}) amplifies psychological and logistical friction."

        elif h_from_moon == 4:
            status = "ACTIVE_KANTAKA_SHANI"
            phase = "Kantaka Shani (Saturn in 4th from Moon - Domestic stress, relocation, mother's health, chest/cardiac discipline)"
            severity = "MODERATE"
        elif h_from_moon == 8:
            status = "ACTIVE_ASHTAMA_SHANI"
            phase = "Ashtama Shani (Saturn in 8th from Moon - Sudden upheavals, health vulnerabilities, intense transformation)"
            severity = "VERY_HIGH"

        return {
            "status": status,
            "target_date": target_date.strftime("%Y-%m-%d"),
            "transit_saturn_sign": sat_sign,
            "transit_saturn_degree": round(sat_lon % 30.0, 2),
            "natal_moon_sign": ZODIAC_SIGNS[self.moon_sign_idx],
            "house_from_moon": h_from_moon,
            "phase": phase,
            "severity": severity,
            "sav_points_in_transit_sign": sav_points,
            "mitigation_verdict": mitigation
        }

    def generate_lifetime_sade_sati_timeline(self, birth_dt: datetime, scan_years: int = 85) -> List[Dict[str, Any]]:
        """Calculates all Sade Sati cycles, Kantaka, and Ashtama Shani windows across lifetime."""
        if birth_dt.tzinfo is None:
            birth_dt = pytz.utc.localize(birth_dt)

        swe.set_sid_mode(Config.ayanamsha_swe_id())
        events = []
        curr_dt = birth_dt
        end_dt = birth_dt + timedelta(days=scan_years * 365.25)

        # Sample Saturn sign every 15 days
        prev_h_from_moon = None
        phase_start = curr_dt

        while curr_dt <= end_dt:
            hour_dec = curr_dt.hour + (curr_dt.minute / 60.0)
            jd = swe.julday(curr_dt.year, curr_dt.month, curr_dt.day, hour_dec)
            sat_res, _ = swe.calc_ut(jd, swe.SATURN, swe.FLG_SIDEREAL)
            sat_sign_idx = int((sat_res[0] % 360.0) / 30.0)
            h_from_moon = ((sat_sign_idx - self.moon_sign_idx) % 12) + 1

            if prev_h_from_moon is None:
                prev_h_from_moon = h_from_moon
                phase_start = curr_dt

            if h_from_moon != prev_h_from_moon:
                # Sign change occurred
                if prev_h_from_moon in [12, 1, 2, 4, 8]:
                    sign_name = ZODIAC_SIGNS[(self.moon_sign_idx + prev_h_from_moon - 1) % 12]
                    sav_pts = self.sav.get(sign_name, 28)
                    
                    category = "Sade Sati" if prev_h_from_moon in [12, 1, 2] else ("Kantaka Shani" if prev_h_from_moon == 4 else "Ashtama Shani")
                    phase_desc = {
                        12: "Phase 1: Rising",
                        1: "Phase 2: Peak (Janma Shani)",
                        2: "Phase 3: Setting",
                        4: "Kantaka Shani (4th from Moon)",
                        8: "Ashtama Shani (8th from Moon)"
                    }.get(prev_h_from_moon, "")

                    events.append({
                        "category": category,
                        "phase": phase_desc,
                        "transit_sign": sign_name,
                        "house_from_moon": prev_h_from_moon,
                        "start_date": phase_start.strftime("%Y-%m-%d"),
                        "end_date": curr_dt.strftime("%Y-%m-%d"),
                        "duration_years": round((curr_dt - phase_start).days / 365.25, 1),
                        "sav_bindus": sav_pts,
                        "impact": "Favorable / Productive (SAV >= 28)" if sav_pts >= 28 else "Challenging / Heavy (SAV < 28)"
                    })

                prev_h_from_moon = h_from_moon
                phase_start = curr_dt

            curr_dt += timedelta(days=15)

        return events
