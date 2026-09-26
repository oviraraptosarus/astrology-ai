import re

with open('dasha_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We need to replace all datetime + timedelta with JD math
# First, find how birth_datetime is used in calculate_vimshottari_timeline

old_start = """    def calculate_vimshottari_timeline(
        birth_datetime: datetime, 
        moon_longitude: float, 
        num_levels: int = 3
    ) -> List[Dict[str, Any]]:"""

new_start = """    def calculate_vimshottari_timeline(
        birth_datetime: datetime, 
        moon_longitude: float, 
        num_levels: int = 3
    ) -> List[Dict[str, Any]]:
        import swisseph as swe"""

content = content.replace(old_start, new_start)

# Replace the initial date setup
old_setup = """        year_length = Config.dasha_year_length()
        
        current_date = birth_datetime"""

new_setup = """        year_length = Config.dasha_year_length()
        
        # Convert birth_datetime to Julian Day for astronomically safe addition
        utc_dt = birth_datetime.astimezone(pytz.utc) if birth_datetime.tzinfo else pytz.utc.localize(birth_datetime)
        hour_dec = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        start_jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)
        
        current_jd = start_jd"""

if old_setup in content:
    content = content.replace(old_setup, new_setup)
else:
    print("Failed to replace old_setup")

# Replace first MD addition
old_first_md = """        first_md_years = balance_years
        first_md_end = current_date + timedelta(days=first_md_years * year_length)
        
        md_node = {
            "level": 1,
            "lord": first_lord,
            "start": current_date.isoformat(),
            "end": first_md_end.isoformat(),
            "duration_years": round(first_md_years, 4),
            "sub_periods": []
        }"""

new_first_md = """        first_md_years = balance_years
        first_md_end_jd = current_jd + (first_md_years * year_length)
        
        def jd_to_iso(jd: float) -> str:
            y, m, d, h_dec = swe.revjul(jd, swe.GREG_CAL)
            h = int(h_dec)
            min_dec = (h_dec - h) * 60.0
            minute = int(min_dec)
            sec = int((min_dec - minute) * 60.0)
            # Ensure valid bounds
            if sec >= 60: sec = 59
            if minute >= 60: minute = 59
            if h >= 24: h = 23
            return f"{y:04d}-{m:02d}-{d:02d}T{h:02d}:{minute:02d}:{sec:02d}Z"
            
        md_node = {
            "level": 1,
            "lord": first_lord,
            "start": jd_to_iso(current_jd),
            "end": jd_to_iso(first_md_end_jd),
            "duration_years": round(first_md_years, 4),
            "sub_periods": []
        }"""

if old_first_md in content:
    content = content.replace(old_first_md, new_first_md)
else:
    print("Failed to replace old_first_md")

# Replace subsequent MD addition
old_sub_md = """            md_years = DashaEngine.DASHA_YEARS[c_idx]
            md_end = current_date + timedelta(days=md_years * year_length)
            
            md_node = {
                "level": 1,
                "lord": c_lord,
                "start": current_date.isoformat(),
                "end": md_end.isoformat(),
                "duration_years": round(md_years, 4),
                "sub_periods": []
            }"""

new_sub_md = """            md_years = DashaEngine.DASHA_YEARS[c_idx]
            md_end_jd = current_jd + (md_years * year_length)
            
            md_node = {
                "level": 1,
                "lord": c_lord,
                "start": jd_to_iso(current_jd),
                "end": jd_to_iso(md_end_jd),
                "duration_years": round(md_years, 4),
                "sub_periods": []
            }"""

if old_sub_md in content:
    content = content.replace(old_sub_md, new_sub_md)
else:
    print("Failed to replace old_sub_md")

# We also need to fix where current_date is updated for MD
content = content.replace("current_date = first_md_end", "current_jd = first_md_end_jd")
content = content.replace("current_date = md_end", "current_jd = md_end_jd")

# Now for Antardasha:
old_ad_calc = """        ad_start_date = md_start
        for ad_lord, ad_total_years in ad_sequence:
            # If we are in the first MD, the first AD might be partially elapsed.
            if is_first_md:
                # The proportion of the AD we actually experience is based on how much of the MD is left.
                # If AD total is X, but we only have balance_years left, which ADs do we skip?
                pass
                # The implemented logic uses proportional time which handles the exact elapsed duration.
                ad_actual_years = ad_total_years * (balance_years / total_md_years)
            else:
                ad_actual_years = ad_total_years
                
            ad_end = current_date + timedelta(days=ad_actual_years * year_length)
            
            ad_node = {
                "level": 2,
                "lord": ad_lord,
                "start": current_date.isoformat(),
                "end": ad_end.isoformat(),
                "duration_years": round(ad_actual_years, 4),
                "sub_periods": []
            }"""

# Wait, `current_date` in AD loop.
# Let's see the original `dasha_engine.py` for AD loop.
EOF_check = """
import re
with open('dasha_engine.py', 'r', encoding='utf-8') as f:
    print("Found AD loop:", 'ad_end = current_date + timedelta' in f.read())
"""
