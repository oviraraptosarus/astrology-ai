import re

with open('astrology_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace local NAKSHATRAS and calculate_nakshatra
old_nak_block = """NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", 
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", 
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", 
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", 
    "Uttara Bhadrapada", "Revati"
]

def calculate_nakshatra(longitude: float) -> tuple:
    \"\"\"Returns (nakshatra_name, pada, lord_name)\"\"\"
    # 27 Nakshatras spread across 360 degrees. Each is 13 degrees 20 minutes (13.333...)
    nakshatra_span = 360.0 / 27.0
    pada_span = nakshatra_span / 4.0
    
    nak_index = int(longitude / nakshatra_span)
    nak_name = NAKSHATRAS[nak_index]
    
    # Calculate Pada (1 to 4)
    remainder = longitude % nakshatra_span
    pada = int(remainder / pada_span) + 1
    
    # Calculate Lord
    lords = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    lord_name = lords[nak_index % 9]
    
    return nak_name, pada, lord_name"""

new_nak_block = """from astronomy_core import AstronomyCore, NAKSHATRAS as CORE_NAK, DASHA_LORDS

def calculate_nakshatra(longitude: float) -> tuple:
    \"\"\"Returns (nakshatra_name, pada, lord_name)\"\"\"
    nak_index, pada, _ = AstronomyCore.calculate_nakshatra(longitude)
    return CORE_NAK[nak_index], pada, DASHA_LORDS[nak_index % 9]"""

if old_nak_block in content:
    content = content.replace(old_nak_block, new_nak_block)
else:
    print("Could not find calculate_nakshatra block")

with open('astrology_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("astrology_engine.py patched.")
