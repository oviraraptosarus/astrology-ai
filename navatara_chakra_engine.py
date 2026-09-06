"""
Navatara Chakra & 27-Nakshatra Tara Bala Engine (Classical Vedic Timing)
Implements:
1. 9-Fold Tara Classification across 3 Cycles (Janma, Anujanma, Trijanma):
   - 1. Janma (Body/Self) [1, 10, 19]
   - 2. Sampat (Wealth/Gains) [2, 11, 20] - Highly Auspicious
   - 3. Vipat (Peril/Loss) [3, 12, 21] - Inauspicious
   - 4. Kshema (Well-being/Security) [4, 13, 22] - Auspicious
   - 5. Pratyak (Obstacles/Resistance) [5, 14, 23] - Inauspicious
   - 6. Sadhana (Accomplishment/Achievement) [6, 15, 24] - Highly Auspicious
   - 7. Naidhana / Vadh (Severance/Danger) [7, 16, 25] - Critically Inauspicious
   - 8. Mitra (Friendship/Support) [8, 17, 26] - Auspicious
   - 9. Parama Mitra (Supreme Fortune) [9, 18, 27] - Highly Auspicious
2. Tara Bala scoring for natal planets and live transits.
3. Daily Muhurtha / Action Timing: Flags auspicious action stars vs danger stars.
"""
from typing import Dict, Any, List
from datetime import datetime
import pytz
import swisseph as swe
from config import Config

from vedic_models import Chart, Planet
from kundali_milan_synastry_engine import NAKSHATRAS

TARA_NAMES = [
    ("Janma", "Body / Mixed / Karmic Baseline", "NEUTRAL"),
    ("Sampat", "Wealth, Prosperity & Inflow of Resources", "HIGHLY_AUSPICIOUS"),
    ("Vipat", "Accidents, Perils, Financial Losses & Sudden Setbacks", "INAUSPICIOUS"),
    ("Kshema", "Well-being, Safety, Healing & Protection", "AUSPICIOUS"),
    ("Pratyak", "Opposition, Resistance, Obstacles & Foes", "INAUSPICIOUS"),
    ("Sadhana", "Accomplishment, Goal Fruition & Success", "HIGHLY_AUSPICIOUS"),
    ("Naidhana", "Critical Vulnerability, Severance & Danger", "CRITICALLY_INAUSPICIOUS"),
    ("Mitra", "Friendship, Alliances, Cooperation & Harmony", "AUSPICIOUS"),
    ("Parama Mitra", "Supreme Victory, Ultimate Grace & Fortunes", "HIGHLY_AUSPICIOUS")
]

class NavataraChakraEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.moon = chart.planets.get("Moon")
        nak_span = 360.0 / 27.0
        self.janma_nak_idx = int(self.moon.longitude / nak_span) % 27 if self.moon else 0

    def get_tara_for_nakshatra(self, target_nak_idx: int) -> Dict[str, Any]:
        """Determines the Tara name, category, and nature for any given Nakshatra index (0-26)."""
        diff = (target_nak_idx - self.janma_nak_idx) % 27
        tara_idx = diff % 9
        cycle_idx = (diff // 9) + 1  # 1: Janma, 2: Anujanma, 3: Trijanma

        tara_name, desc, nature = TARA_NAMES[tara_idx]
        cycle_name = ["Janma (Physical/Immediate)", "Anujanma (Intermediate/Mental)", "Trijanma (Spiritual/Karmic)"][cycle_idx - 1]

        return {
            "nakshatra": NAKSHATRAS[target_nak_idx],
            "nakshatra_number": target_nak_idx + 1,
            "tara_name": tara_name,
            "tara_index": tara_idx + 1,
            "cycle": cycle_name,
            "nature": nature,
            "significance": desc
        }

    def evaluate_natal_planets_tara_bala(self) -> Dict[str, Any]:
        """Evaluates which Tara each natal planet sits in relative to Moon."""
        nak_span = 360.0 / 27.0
        evaluations = {}
        for pname, p in self.chart.planets.items():
            n_idx = int(p.longitude / nak_span) % 27
            evaluations[pname] = self.get_tara_for_nakshatra(n_idx)
        return evaluations

    def evaluate_transit_moon_tara(self, target_dt: datetime = None) -> Dict[str, Any]:
        """Evaluates current transiting Moon Tara Bala for daily action timing."""
        if target_dt is None:
            target_dt = datetime.now(pytz.utc)
        elif target_dt.tzinfo is None:
            target_dt = pytz.utc.localize(target_dt)

        swe.set_sid_mode(Config.ayanamsha_swe_id())
        hour_dec = target_dt.hour + (target_dt.minute / 60.0)
        jd = swe.julday(target_dt.year, target_dt.month, target_dt.day, hour_dec)
        res, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL)
        m_lon = res[0] % 360.0

        nak_span = 360.0 / 27.0
        n_idx = int(m_lon / nak_span) % 27
        tara_info = self.get_tara_for_nakshatra(n_idx)

        verdict = "FAVORABLE FOR INITIATIVES" if "AUSPICIOUS" in tara_info["nature"] else "AVOID MAJOR HIGH-STAKES ACTIONS"

        return {
            "target_date": target_dt.strftime("%Y-%m-%d %H:%M UTC"),
            "transit_moon_nakshatra": NAKSHATRAS[n_idx],
            "tara_details": tara_info,
            "action_timing_verdict": verdict
        }
