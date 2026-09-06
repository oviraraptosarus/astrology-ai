import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from datetime import datetime, timedelta
import pytz
import swisseph as swe
from vedic_models import Chart, Planet
from panchangam_engine import PanchangamEngine
from forward_timing_scanner import ForwardTimingScanner
from sensitive_points import SensitivePointsEngine
from numerology_engine import NumerologyEngine
from institutional_chakra_engine import InstitutionalChakraEngine
from financial_astro_engine import FinancialAstroEngine
from pancha_pakshi_engine import PanchaPakshiEngine
from remedy_engine import RemedyEngine
from realtime_engine import RealtimeEngine

# Test instantiation with mock chart
chart = Chart(ascendant_sign="Capricorn", ascendant_degree=14.21)
chart.add_planet(Planet("Moon", "Cancer", 17.17, False))
chart.add_planet(Planet("Sun", "Cancer", 15.66, False))
chart.build_relational_graph()

pe = PanchangamEngine()
pan = pe.calculate_full_panchang(datetime.now(pytz.timezone("Asia/Kolkata")), 28.6139, 77.2090, "Asia/Kolkata")
print("Panchang tool works! Sunrise:", pan["sun_metrics"]["sunrise"])

gann_deg = FinancialAstroEngine.price_to_degree(65000.0)
print("Gann tool works! Angle for 65000:", gann_deg)

now = datetime.now(pytz.utc)
jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
live_planets = RealtimeEngine.get_live_planets(jd)
kota = InstitutionalChakraEngine.calculate_kota_chakra(chart, live_planets)
print("Kota chakra works! Fort Lord:", kota["kota_lord_king"])

num = NumerologyEngine.generate_full_profile(1, 8, 2008, "Rahul")
print("Numerology works! Moolank:", num["moolank"])

rem = RemedyEngine().get_remedy_for_planet("Saturn", is_benefic=True, is_afflicted=False)
print("Remedies work! Saturn Gemstone:", rem["gemstone_verdict"]["recommendation"])
