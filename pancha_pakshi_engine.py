"""
Pancha Pakshi Shastra Engine (Tamil Siddha 5-Bird Bio-Timing)
Determines birth bird from Nakshatra/Paksha and computes intraday
activity windows: Ruling (Arasu), Eating (Oon), Walking (Nadai), Sleeping (Thuyil), Dying (Saavu).
"""

from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any

BIRDS = ["Vulture", "Owl", "Crow", "Cock", "Peacock"]
ACTIVITIES = ["Ruling", "Eating", "Walking", "Sleeping", "Dying"]

# Nakshatra assignment for Shukla Paksha (Waxing / Valarpirai)
# 27 Nakshatras divided among 5 birds (5, 6, 5, 6, 5 pattern)
SHUKLA_NAKSHATRA_BIRDS = {
    # 1-5 (Ashwini, Bharani, Krittika, Rohini, Mrigashira) -> Vulture
    0: "Vulture", 1: "Vulture", 2: "Vulture", 3: "Vulture", 4: "Vulture",
    # 6-11 (Ardra, Punarvasu, Pushya, Ashlesha, Magha, Purva Phalguni) -> Owl
    5: "Owl", 6: "Owl", 7: "Owl", 8: "Owl", 9: "Owl", 10: "Owl",
    # 12-16 (Uttara Phalguni, Hasta, Chitra, Swati, Vishakha) -> Crow
    11: "Crow", 12: "Crow", 13: "Crow", 14: "Crow", 15: "Crow",
    # 17-22 (Anuradha, Jyeshtha, Mula, Purva Ashadha, Uttara Ashadha, Shravana) -> Cock
    16: "Cock", 17: "Cock", 18: "Cock", 19: "Cock", 20: "Cock", 21: "Cock",
    # 23-27 (Dhanishta, Shatabhisha, Purva Bhadrapada, Uttara Bhadrapada, Revati) -> Peacock
    22: "Peacock", 23: "Peacock", 24: "Peacock", 25: "Peacock", 26: "Peacock"
}

# Nakshatra assignment for Krishna Paksha (Waning / Theipirai)
KRISHNA_NAKSHATRA_BIRDS = {
    0: "Peacock", 1: "Peacock", 2: "Peacock", 3: "Peacock", 4: "Peacock",
    5: "Cock", 6: "Cock", 7: "Cock", 8: "Cock", 9: "Cock", 10: "Cock",
    11: "Crow", 12: "Crow", 13: "Crow", 14: "Crow", 15: "Crow",
    16: "Owl", 17: "Owl", 18: "Owl", 19: "Owl", 20: "Owl", 21: "Owl",
    22: "Vulture", 23: "Vulture", 24: "Vulture", 25: "Vulture", 26: "Vulture"
}

# Major Jamam (2 hr 24 min) Activity sequence in Shukla Daytime
# Order of birds for Shukla Daytime based on weekday
SHUKLA_DAY_BIRD_ORDER = {
    0: ["Vulture", "Owl", "Crow", "Cock", "Peacock"], # Sunday
    1: ["Owl", "Crow", "Cock", "Peacock", "Vulture"], # Monday
    2: ["Crow", "Cock", "Peacock", "Vulture", "Owl"], # Tuesday
    3: ["Cock", "Peacock", "Vulture", "Owl", "Crow"], # Wednesday
    4: ["Peacock", "Vulture", "Owl", "Crow", "Cock"], # Thursday
    5: ["Vulture", "Owl", "Crow", "Cock", "Peacock"], # Friday
    6: ["Owl", "Crow", "Cock", "Peacock", "Vulture"]  # Saturday
}

class PanchaPakshiEngine:
    """
    Bio-rhythmic decision support for high-stakes timing.
    """

    @staticmethod
    def get_birth_bird(moon_longitude: float, sun_longitude: float) -> Dict[str, str]:
        """
        Calculates the native's Birth Bird based on Moon's Nakshatra and Paksha.
        """
        # Determine Paksha: Tithi (0-180 deg diff = Shukla, 180-360 = Krishna)
        diff = (moon_longitude - sun_longitude) % 360.0
        is_shukla = diff < 180.0
        paksha = "Shukla (Waxing)" if is_shukla else "Krishna (Waning)"

        # Nakshatra Index (0 to 26)
        nak_span = 360.0 / 27.0
        nak_idx = int(moon_longitude / nak_span)

        if is_shukla:
            bird = SHUKLA_NAKSHATRA_BIRDS.get(nak_idx, "Vulture")
        else:
            bird = KRISHNA_NAKSHATRA_BIRDS.get(nak_idx, "Peacock")

        return {
            "birth_bird": bird,
            "paksha": paksha,
            "nakshatra_index": nak_idx + 1
        }

    @staticmethod
    def calculate_current_activity(birth_bird: str, dt_local: datetime) -> Dict[str, Any]:
        """
        Calculates the active bio-state (Ruling, Eating, Walking, Sleeping, Dying) for the given moment.
        """
        # 5 major Jamams per day (each 2h 24m = 144 mins) starting from approx 6:00 AM
        mins_from_6am = ((dt_local.hour - 6) * 60 + dt_local.minute) % (12 * 60)
        jamam_idx = int(mins_from_6am / 144.0) % 5

        # Within the Jamam, 5 Apana sub-periods (each 28.8 minutes)
        sub_mins = mins_from_6am % 144.0
        sub_activity_idx = int(sub_mins / 28.8) % 5

        # Map to activity potency
        activity = ACTIVITIES[(jamam_idx + sub_activity_idx) % 5]
        
        potency_map = {
            "Ruling": {"score": 100, "status": "MAXIMUM_POWER", "verdict": "Auspicious for critical decisions, contracts, and capital deployment."},
            "Eating": {"score": 80, "status": "NOURISHING_PROGRESS", "verdict": "Favorable for strategic intake, meetings, and constructive tasks."},
            "Walking": {"score": 50, "status": "MODERATE_MOVEMENT", "verdict": "Suitable for routine travel, exploratory talks, and preliminary steps."},
            "Sleeping": {"score": 20, "status": "PASSIVE_REST", "verdict": "Unfavorable for launches; focus on internal work, analysis, and rest."},
            "Dying": {"score": 0, "status": "CRITICAL_AVOIDANCE", "verdict": "Strictly avoid high-stakes actions, disputes, signing contracts, or major risks."}
        }

        meta = potency_map.get(activity, {})
        return {
            "birth_bird": birth_bird,
            "timestamp": dt_local.strftime("%Y-%m-%d %H:%M:%S"),
            "active_activity": activity,
            "potency_score": meta.get("score", 50),
            "tactical_status": meta.get("status", "MODERATE"),
            "action_guidance": meta.get("verdict", "")
        }

    @staticmethod
    def get_pakshi_reading(natal_chart, dt_local: datetime) -> Dict[str, Any]:
        moon = natal_chart.planets.get("Moon") if hasattr(natal_chart, "planets") else None
        sun = natal_chart.planets.get("Sun") if hasattr(natal_chart, "planets") else None
        m_lon = moon.longitude if moon else 0.0
        s_lon = sun.longitude if sun else 0.0
        b_data = PanchaPakshiEngine.get_birth_bird(m_lon, s_lon)
        act_data = PanchaPakshiEngine.calculate_current_activity(b_data["birth_bird"], dt_local)
        act_data["paksha"] = b_data["paksha"]
        act_data["nakshatra_index"] = b_data["nakshatra_index"]
        return act_data
