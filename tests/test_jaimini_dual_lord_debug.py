import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine

# 2008 User Chart: Scorpio Lagna / Aquarius / Scorpio
chart_user, _ = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata", "User")

# Let's inspect Mars vs Ketu (Scorpio) and Saturn vs Rahu (Aquarius)
# Mars in Leo (House 8), Ketu in Cancer (House 7 with Sun, Moon, Mercury)
# Saturn in Leo (House 8), Rahu in Capricorn (House 1)

print("Ketu conjunctions:", len(chart_user.planets['Ketu'].conjunct_with), "Planets:", chart_user.planets['Ketu'].conjunct_with)
print("Mars conjunctions:", len(chart_user.planets['Mars'].conjunct_with), "Planets:", chart_user.planets['Mars'].conjunct_with)

print("Saturn conjunctions:", len(chart_user.planets['Saturn'].conjunct_with), "Planets:", chart_user.planets['Saturn'].conjunct_with)
print("Rahu conjunctions:", len(chart_user.planets['Rahu'].conjunct_with), "Planets:", chart_user.planets['Rahu'].conjunct_with)
