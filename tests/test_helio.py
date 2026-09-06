
import swisseph as swe
from datetime import datetime

# Julian day
jd = swe.julday(1980, 1, 1, 12.0)

# Geocentric 
res_geo_mer, _ = swe.calc_ut(jd, swe.MERCURY, swe.FLG_SWIEPH)
# Heliocentric
res_hel_mer, _ = swe.calc_ut(jd, swe.MERCURY, swe.FLG_SWIEPH | swe.FLG_HELCTR)
res_hel_ven, _ = swe.calc_ut(jd, swe.VENUS, swe.FLG_SWIEPH | swe.FLG_HELCTR)
res_geo_sun, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)

print("Geo Sun:", res_geo_sun[0])
print("Geo Mercury:", res_geo_mer[0])
print("Helio Mercury:", res_hel_mer[0])
