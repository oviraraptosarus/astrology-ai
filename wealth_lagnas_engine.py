"""
Special Wealth & Power Lagnas Engine (Indu Lagna, Shree Lagna, Ghatika Lagna, Hora Lagna)
Implements:
1. Indu Lagna (Moon-Wealth Ascendant / Dhana Sphuta):
   - Planetary Ray (Kala) Values: Sun=30, Moon=16, Mars=6, Mercury=8, Jupiter=10, Venus=12, Saturn=1.
   - Ray Sum of (9th Lord from Lagna + 9th Lord from Moon) modulo 12 from Janma Moon.
   - Financial Magnitude Classifier: Koti-Dhipati (Multimillionaire/Billionaire) vs Moderate vs Striving.
2. Shree Lagna (SL - Lakshmi/Prosperity Ascendant).
3. Ghatika Lagna (GL - Power, Fame, and Political Authority).
4. Hora Lagna (HL - Tangible Liquidity & Financial Assets).
"""
from typing import Dict, Any, List
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

PLANETARY_RAYS_KALAS = {
    "Sun": 30, "Moon": 16, "Mars": 6, "Mercury": 8, "Jupiter": 10, "Venus": 12, "Saturn": 1
}

class WealthLagnasEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign) if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else int(chart.ascendant.longitude / 30)
        self.moon = chart.planets.get("Moon")
        self.moon_sign_idx = ZODIAC_SIGNS.index(self.moon.sign) if self.moon else 0

    def calculate_indu_lagna(self) -> Dict[str, Any]:
        """Calculates Indu Lagna and financial magnitude potential."""
        # 9th House from Lagna Lord
        h9_lagna_idx = (self.lagna_sign_idx + 8) % 12
        h9_lagna_lord = SIGN_LORDS[ZODIAC_SIGNS[h9_lagna_idx]]
        rays_lagna = PLANETARY_RAYS_KALAS.get(h9_lagna_lord, 8)

        # 9th House from Moon Lord
        h9_moon_idx = (self.moon_sign_idx + 8) % 12
        h9_moon_lord = SIGN_LORDS[ZODIAC_SIGNS[h9_moon_idx]]
        rays_moon = PLANETARY_RAYS_KALAS.get(h9_moon_lord, 8)

        total_kalas = rays_lagna + rays_moon
        rem = total_kalas % 12
        if rem == 0:
            rem = 12

        indu_sign_idx = (self.moon_sign_idx + rem - 1) % 12
        indu_sign = ZODIAC_SIGNS[indu_sign_idx]

        # Check planets occupying Indu Lagna
        planets_in_indu = [pname for pname, p in self.chart.planets.items() if p.sign == indu_sign]
        
        # Financial magnitude evaluation
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]
        
        has_benefic = any(p in benefics for p in planets_in_indu)
        has_malefic = any(p in malefics for p in planets_in_indu)

        if has_benefic and not has_malefic:
            magnitude = "KOTI-DHIPATI YOGA (Exceptional Multimillionaire / Generational Wealth Potential)"
        elif has_benefic and has_malefic:
            magnitude = "HIGH WEALTH WITH PERIODIC FLUCTUATIONS (Substantial Assets / Entrepreneurial)"
        elif has_malefic and not has_benefic:
            magnitude = "WEALTH THROUGH INTENSE TOIL & SWEAT (Steady Accumulation via Labor)"
        else:
            magnitude = "MODERATE / SELF-EARNED STEADY FINANCIAL BASE (Aspects from Benefics Key)"

        return {
            "indu_lagna_sign": indu_sign,
            "h9_from_lagna_lord": f"{h9_lagna_lord} ({rays_lagna} Kalas)",
            "h9_from_moon_lord": f"{h9_moon_lord} ({rays_moon} Kalas)",
            "total_kalas": total_kalas,
            "counting_offset_from_moon": rem,
            "planets_in_indu_lagna": planets_in_indu,
            "financial_magnitude_verdict": magnitude
        }

    def calculate_special_lagnas(self) -> Dict[str, Any]:
        """Calculates Shree Lagna (SL), Ghatika Lagna (GL), and Hora Lagna (HL)."""
        if hasattr(self.chart, "ascendant") and hasattr(self.chart.ascendant, "longitude"):
            asc_lon = self.chart.ascendant.longitude
        elif hasattr(self.chart, "ascendant_sign") and hasattr(self.chart, "ascendant_degree"):
            sign_idx = ZODIAC_SIGNS.index(self.chart.ascendant_sign) if self.chart.ascendant_sign in ZODIAC_SIGNS else 0
            asc_lon = (sign_idx * 30.0) + self.chart.ascendant_degree
        else:
            asc_lon = 0.0
        moon_lon = self.moon.longitude if self.moon else 0.0

        # Shree Lagna: Moon nakshatra fraction * 360 + Ascendant
        nak_span = 360.0 / 27.0
        fraction_in_nak = (moon_lon % nak_span) / nak_span
        sl_lon = (asc_lon + (fraction_in_nak * 360.0)) % 360.0
        sl_sign = ZODIAC_SIGNS[int(sl_lon / 30)]

        # Hora Lagna (HL)
        hl_lon = (asc_lon + (moon_lon * 2.0)) % 360.0
        hl_sign = ZODIAC_SIGNS[int(hl_lon / 30)]

        # Ghatika Lagna (GL)
        gl_lon = (asc_lon + (moon_lon * 5.0)) % 360.0
        gl_sign = ZODIAC_SIGNS[int(gl_lon / 30)]

        indu = self.calculate_indu_lagna()

        return {
            "indu_lagna": indu,
            "shree_lagna": {"sign": sl_sign, "longitude": round(sl_lon, 2), "description": "Lakshmi Sthana / Innate Prosperity & Grace"},
            "hora_lagna": {"sign": hl_sign, "longitude": round(hl_lon, 2), "description": "Dhana Sthana / Tangible Liquid Wealth & Capital"},
            "ghatika_lagna": {"sign": gl_sign, "longitude": round(gl_lon, 2), "description": "Rajya Sthana / Political Power, Authority & Executive Command"}
        }
