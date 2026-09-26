from astronomy_core import ephemeris_lock
import swisseph as swe
from vedic_models import Chart, Planet
from strength_engine import StrengthEngine
import datetime

# Mock chart
chart = Chart("Aries", 0.0)

# Set Sun at 0 Aries
chart.planets["Sun"] = Planet("Sun", "Aries", 0.0, False)
chart.planets["Sun"].house = 1

# Set Moon at 0 Capricorn (270 degrees from Sun) -> Krishna Paksha (waning)
chart.planets["Moon"] = Planet("Moon", "Capricorn", 0.0, False)
chart.planets["Moon"].house = 10

# Set Saturn at 0 Aries
chart.planets["Saturn"] = Planet("Saturn", "Aries", 0.0, False)
chart.planets["Saturn"].house = 1

# Set Venus
chart.planets["Venus"] = Planet("Venus", "Aries", 0.0, False)
chart.planets["Venus"].house = 1

chart.ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
chart.SIGN_LORDS = {}

StrengthEngine._calc_kala_bala(chart)

print("Kala Bala Paksha Bug Output:")
print("Moon Kala Bala:", chart.planets["Moon"].shadbala.get("kala_bala"))
print("Venus Kala Bala:", chart.planets["Venus"].shadbala.get("kala_bala"))
print("Saturn Kala Bala:", chart.planets["Saturn"].shadbala.get("kala_bala"))
print("Sun Kala Bala:", chart.planets["Sun"].shadbala.get("kala_bala"))
