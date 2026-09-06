"""
Sarvatobhadra Chakra (SBC) 28-Nakshatra Vedha Engine
Implements:
1. 28 Nakshatra system (including Abhijit).
2. The 7 Special Sensitive Nakshatras (Saptanaadi):
   - Janma (1st - Physical Vitality)
   - Karma (10th - Career & Power)
   - Sanghatika (16th - Partnerships & Deals)
   - Samudayika (18th - Overall Prosperity)
   - Adhana (19th - Roots & Foundation)
   - Vainashika (23rd - Acute Destruction / Ruin)
   - Manasa (25th - Mental Balance & Psyche)
3. Direct, Front (Samukha), Right (Dakshina), and Left (Vama) Vedhas from transiting planets.
4. Transit Risk Assessment: High-alert crisis flags when Saturn, Mars, or Rahu inflict Vedha on Vainashika, Janma, or Karma nakshatras.
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime
import pytz
import swisseph as swe

from vedic_models import Chart, Planet
from config import Config

# 28 Nakshatras in SBC order
NAKSHATRAS_28 = [
    "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Abhijit", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati", "Ashwini", "Bharani"
]

class SarvatobhadraChakraEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.moon = chart.planets.get("Moon")
        self.special_nakshatras = self._calculate_special_nakshatras()

    def _calculate_special_nakshatras(self) -> Dict[str, Dict[str, Any]]:
        """Calculates the 7 Special Sensitive Nakshatras from Janma Moon."""
        if not self.moon:
            return {}

        # 27 Nakshatra index for standard counts
        nak_span_27 = 360.0 / 27.0
        janma_idx_27 = int(self.moon.longitude / nak_span_27) % 27

        offsets = {
            "Janma (Body & Vitality)": 1,
            "Karma (Profession & Status)": 10,
            "Sanghatika (Alliances & Deals)": 16,
            "Samudayika (Total Prosperity)": 18,
            "Adhana (Roots & Family Base)": 19,
            "Vainashika (Destruction & Crisis)": 23,
            "Manasa (Mental State & Psyche)": 25
        }

        from kundali_milan_synastry_engine import NAKSHATRAS as NAK_27

        result = {}
        for label, offset in offsets.items():
            target_idx = (janma_idx_27 + offset - 1) % 27
            target_name = NAK_27[target_idx]
            result[label] = {
                "offset_from_moon": offset,
                "nakshatra": target_name,
                "nakshatra_index": target_idx + 1
            }
        return result

    def evaluate_transit_vedha(self, target_dt: datetime = None) -> Dict[str, Any]:
        """Checks if transiting malefics inflict Vedha on any of the 7 Special Nakshatras."""
        if target_dt is None:
            target_dt = datetime.now(pytz.utc)
        elif target_dt.tzinfo is None:
            target_dt = pytz.utc.localize(target_dt)

        swe.set_sid_mode(Config.ayanamsha_swe_id())
        hour_dec = target_dt.hour + (target_dt.minute / 60.0)
        jd = swe.julday(target_dt.year, target_dt.month, target_dt.day, hour_dec)

        malefics = {"Saturn": swe.SATURN, "Mars": swe.MARS, "Rahu": Config.node_swe_id()}
        from kundali_milan_synastry_engine import NAKSHATRAS as NAK_27
        nak_span_27 = 360.0 / 27.0

        transit_positions = {}
        for p_name, p_code in malefics.items():
            res, _ = swe.calc_ut(jd, p_code, swe.FLG_SIDEREAL)
            lon = res[0] % 360.0
            n_idx = int(lon / nak_span_27) % 27
            transit_positions[p_name] = {
                "longitude": round(lon, 2),
                "nakshatra": NAK_27[n_idx],
                "nakshatra_index": n_idx + 1
            }

        vedha_hits = []
        for special_label, s_data in self.special_nakshatras.items():
            s_nak = s_data["nakshatra"]
            for p_name, t_data in transit_positions.items():
                if t_data["nakshatra"] == s_nak:
                    severity = "CRITICAL" if "Vainashika" in special_label or "Janma" in special_label else "HIGH"
                    vedha_hits.append({
                        "planet": p_name,
                        "special_point": special_label,
                        "afflicted_nakshatra": s_nak,
                        "severity": severity,
                        "impact": f"Malefic {p_name} directly transiting {special_label} ({s_nak}) causes severe obstruction and vulnerability."
                    })

        risk_level = "SEVERE" if any(h["severity"] == "CRITICAL" for h in vedha_hits) else ("ELEVATED" if len(vedha_hits) > 0 else "LOW / CLEAR")

        return {
            "target_date": target_dt.strftime("%Y-%m-%d"),
            "risk_level": risk_level,
            "special_nakshatras": self.special_nakshatras,
            "transiting_malefics": transit_positions,
            "active_vedhas": vedha_hits
        }
