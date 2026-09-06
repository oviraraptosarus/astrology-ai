"""
Financial Astrological Analysis Engine
Implements W.D. Gann Square of 9 (Price-to-Angle Conversion & Time Squaring),
Harmonic Support/Resistance Levels, and Donald Bradley Siderograph Composite Vectors.
"""

import math
from typing import Dict, List, Any, Tuple
import swisseph as swe

class FinancialAstroEngine:
    """
    Institutional market forecasting, price-degree harmonics, and Gann wheel calculations.
    """

    @staticmethod
    def price_to_degree(price: float) -> float:
        """
        Converts asset price to degree on the 360° circle using classical Gann Square of 9:
        Degree = (sqrt(Price) * 180 - 225) % 360
        """
        if price <= 0:
            return 0.0
        root = math.sqrt(price)
        deg = (root * 180.0 - 225.0) % 360.0
        return round(deg, 4)

    @staticmethod
    def degree_to_prices(base_price: float) -> Dict[str, float]:
        """
        Calculates Gann harmonic price levels corresponding to 45°, 90°, 180°, 270°, and 360° squaring.
        """
        if base_price <= 0:
            return {}
        root = math.sqrt(base_price)
        
        # 1 circle = 360 deg = root + 2.0
        # 45 deg = root + 0.25
        # 90 deg = root + 0.50
        # 180 deg = root + 1.00
        levels = {
            "Resistance_45_deg": round((root + 0.25) ** 2, 2),
            "Resistance_90_deg (Square)": round((root + 0.50) ** 2, 2),
            "Resistance_180_deg (Opposition)": round((root + 1.00) ** 2, 2),
            "Resistance_360_deg (Full Cycle)": round((root + 2.00) ** 2, 2),
            "Support_45_deg": round((max(0.1, root - 0.25)) ** 2, 2),
            "Support_90_deg (Square)": round((max(0.1, root - 0.50)) ** 2, 2),
            "Support_180_deg (Opposition)": round((max(0.1, root - 1.00)) ** 2, 2)
        }
        return levels

    @staticmethod
    def calculate_gann_squaring(price: float, live_planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates Gann Price-Time Squaring against current planetary positions.
        """
        price_deg = FinancialAstroEngine.price_to_degree(price)
        harmonic_levels = FinancialAstroEngine.degree_to_prices(price)

        aspect_squarings = []
        for p_name, p_data in live_planets.items():
            p_lon = p_data.get("longitude", 0.0)
            diff = abs(price_deg - p_lon) % 360.0
            if diff > 180.0:
                diff = 360.0 - diff

            match_type = None
            orb = 2.5
            if abs(diff - 0.0) <= orb:
                match_type = "GANN_CONJUNCTION (Price Squares Planet)"
            elif abs(diff - 90.0) <= orb:
                match_type = "GANN_SQUARE (90° Pivot Turn)"
            elif abs(diff - 180.0) <= orb:
                match_type = "GANN_OPPOSITION (180° Major Polarity Reversal)"
            elif abs(diff - 120.0) <= orb:
                match_type = "GANN_TRINE (120° Harmonic Trend Continuation)"

            if match_type:
                aspect_squarings.append({
                    "planet": p_name,
                    "planet_longitude": round(p_lon, 2),
                    "squaring_type": match_type,
                    "orb": round(abs(diff - (0.0 if "CONJUNCTION" in match_type else 180.0 if "OPPOSITION" in match_type else 90.0 if "SQUARE" in match_type else 120.0)), 2)
                })

        return {
            "asset_price": price,
            "gann_wheel_degree": price_deg,
            "active_squarings": aspect_squarings,
            "gann_harmonic_price_levels": harmonic_levels,
            "market_state": "MAJOR_GANN_TIME_PRICE_PIVOT" if aspect_squarings else "NORMAL_HARMONIC_EXPANSION"
        }
