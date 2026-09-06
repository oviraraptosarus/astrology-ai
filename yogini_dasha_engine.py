"""
Yogini Dasha Engine (Classical 36-Year Secondary Dasha Cycle)
Implements:
1. 8 Yoginis: Mangala (Moon, 1y), Pingala (Sun, 2y), Dhanya (Jupiter, 3y), 
   Bhramari (Mars, 4y), Bhadrika (Mercury, 5y), Ulka (Saturn, 6y), 
   Siddha (Venus, 7y), Sankata (Rahu/Ketu, 8y). Total = 36 Years.
2. Calculation of starting Yogini based on Janma Nakshatra:
   Starting Yogini Index = (Nakshatra Index + 3) % 8
3. Balance of birth Yogini calculation from Moon longitude.
4. Generation of full lifetime Yogini Dasha timeline (Cycles 1, 2, 3).
5. Cross-verification flags for acute crises (Ulka / Sankata) and prosperity (Dhanya / Siddha).
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import pytz

from vedic_models import Chart, Planet

YOGINI_NAMES = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_LORDS = ["Moon", "Sun", "Jupiter", "Mars", "Mercury", "Saturn", "Venus", "Rahu"]
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]  # Sum = 36
TOTAL_YOGINI_CYCLE = 36.0

YOGINI_ARCHETYPES = {
    "Mangala": {"ruler": "Moon", "nature": "BENEFIC", "impact": "Peace, auspicious beginnings, domestic happiness"},
    "Pingala": {"ruler": "Sun", "nature": "MALEFIC", "impact": "Heart/blood pressure, ego friction, disputes, government friction"},
    "Dhanya": {"ruler": "Jupiter", "nature": "HIGHLY_BENEFIC", "impact": "Wealth, learning, honors, spiritual expansion"},
    "Bhramari": {"ruler": "Mars", "nature": "MALEFIC", "impact": "Wandering, travel displacements, sudden expenses, friction"},
    "Bhadrika": {"ruler": "Mercury", "nature": "BENEFIC", "impact": "Career advancement, business growth, intellect, communication"},
    "Ulka": {"ruler": "Saturn", "nature": "HIGHLY_MALEFIC", "impact": "Obstacles, bone/dental issues, chronic delays, grief, litigation"},
    "Siddha": {"ruler": "Venus", "nature": "HIGHLY_BENEFIC", "impact": "Sensory fulfillment, luxury, marriage, artistic breakthroughs, wealth"},
    "Sankata": {"ruler": "Rahu", "nature": "HIGHLY_MALEFIC", "impact": "Sudden shocks, illusions, chronic health strain, isolation, acute stress"}
}

class YoginiDashaEngine:
    @staticmethod
    def calculate_yogini_timeline(birth_time_utc: datetime, moon_lon: float, cycles: int = 3) -> List[Dict[str, Any]]:
        """Generates the full Yogini Dasha timeline across up to 3 cycles (108 years)."""
        if birth_time_utc.tzinfo is None:
            birth_time_utc = pytz.utc.localize(birth_time_utc)

        nak_span = 360.0 / 27.0
        nak_idx = int(moon_lon / nak_span) % 27
        
        # Classical starting Yogini: (Nakshatra Number + 3) % 8
        # Nakshatra Number is 1-indexed (Ashwini=1) -> nak_idx + 1
        start_yogini_idx = ((nak_idx + 1) + 3) % 8
        if start_yogini_idx == 0:
            start_yogini_idx = 8
        start_yogini_idx -= 1  # 0-indexed: 0 to 7

        fraction_left = (nak_span - (moon_lon % nak_span)) / nak_span
        balance_years = fraction_left * YOGINI_YEARS[start_yogini_idx]

        timeline = []
        curr_dt = birth_time_utc
        c_idx = start_yogini_idx

        # First fractional period
        first_end = curr_dt + timedelta(days=balance_years * 365.25)
        name = YOGINI_NAMES[c_idx]
        arch = YOGINI_ARCHETYPES[name]
        timeline.append({
            "yogini": name,
            "ruler": arch["ruler"],
            "nature": arch["nature"],
            "duration_years": round(balance_years, 2),
            "start": curr_dt.strftime("%Y-%m-%d"),
            "end": first_end.strftime("%Y-%m-%d"),
            "impact_archetype": arch["impact"]
        })
        curr_dt = first_end
        c_idx = (c_idx + 1) % 8

        total_entries = cycles * 8
        for _ in range(total_entries - 1):
            dur = YOGINI_YEARS[c_idx]
            end_dt = curr_dt + timedelta(days=dur * 365.25)
            name = YOGINI_NAMES[c_idx]
            arch = YOGINI_ARCHETYPES[name]

            timeline.append({
                "yogini": name,
                "ruler": arch["ruler"],
                "nature": arch["nature"],
                "duration_years": float(dur),
                "start": curr_dt.strftime("%Y-%m-%d"),
                "end": end_dt.strftime("%Y-%m-%d"),
                "impact_archetype": arch["impact"]
            })
            curr_dt = end_dt
            c_idx = (c_idx + 1) % 8

        return timeline
