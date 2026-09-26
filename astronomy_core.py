import threading
import swisseph as swe

class AstronomyCore:
    """
    Thread-safe wrapper for the pyswisseph C-extension.
    Because pyswisseph maintains global state (specifically for ayanamsha via set_sid_mode),
    concurrent web requests requiring different modes (e.g. Lahiri vs Krishnamurti)
    can corrupt each other. This lock ensures atomic access to the ephemeris.
    """
    _lock = threading.RLock()

    @classmethod
    def set_sid_mode(cls, mode):
        # We don't lock here alone, because we need the lock to persist across the calc_ut calls.
        # Instead, we should use a context manager to lock a whole block of calculations.
        pass
    
    @classmethod
    def get_lock(cls):
        return cls._lock

    @classmethod
    def calculate_nakshatra(cls, longitude: float):
        """
        Canonical mathematical calculation of Nakshatra from a 360-degree longitude.
        Provides the 0-indexed nakshatra index, the pada (1-4), and the fractional traversal.
        """
        NAK_SPAN = 360.0 / 27.0
        PADA_SPAN = NAK_SPAN / 4.0
        
        nak_index = int(longitude / NAK_SPAN)
        rem = longitude % NAK_SPAN
        pada = int(rem / PADA_SPAN) + 1
        fraction = rem / NAK_SPAN
        return nak_index, pada, fraction

# Global singleton lock for the application to import
ephemeris_lock = AstronomyCore.get_lock()

# Canonical Nakshatra data to avoid duplication across engines
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
