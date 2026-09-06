import swisseph as swe
from config import Config
from datetime import datetime
import pytz

swe.set_sid_mode(Config.ayanamsha_swe_id())
tz = pytz.timezone("Asia/Kolkata")
dt = tz.localize(datetime(2008, 8, 1, 18, 25))
udt = dt.astimezone(pytz.utc)

hour_dec = udt.hour + udt.minute/60.0 + udt.second/3600.0
jd = swe.julday(udt.year, udt.month, udt.day, hour_dec)

flags = swe.FLG_SIDEREAL
moon_absolute_lon = swe.calc_ut(jd, swe.MOON, flags)[0][0]
print("Moon absolute lon:", moon_absolute_lon)

dasha_lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
        
nakshatra_span = 360 / 27
moon_nak_index = int(moon_absolute_lon / nakshatra_span)
lord_index = moon_nak_index % 9
        
# Balance of Dasha at birth
fraction_left = (nakshatra_span - (moon_absolute_lon % nakshatra_span)) / nakshatra_span
balance_years = fraction_left * dasha_years[lord_index]
print("Starting Dasha:", dasha_lords[lord_index], "Balance Years:", balance_years)

def dt_to_dec(dt_obj):
    return dt_obj.year + (dt_obj.timetuple().tm_yday - 1) / 365.25

birth_dec = dt_to_dec(dt)
current_dec = dt_to_dec(datetime.now())
print("Age:", current_dec - birth_dec)

age_in_years = current_dec - birth_dec
elapsed = balance_years
current_dasha = dasha_lords[lord_index]
if age_in_years > balance_years:
    curr_idx = (lord_index + 1) % 9
    while True:
        if elapsed + dasha_years[curr_idx] > age_in_years:
            current_dasha = dasha_lords[curr_idx]
            break
        elapsed += dasha_years[curr_idx]
        curr_idx = (curr_idx + 1) % 9

print("Current Dasha:", current_dasha)
