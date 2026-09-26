import re

with open('strength_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_paksha = """            # Paksha Bala (Fortnight Strength, max 60 virupas)
            # Benefics (Moon, Mercury, Jupiter, Venus) gain in Shukla Paksha
            # Malefics (Sun, Mars, Saturn) gain in Krishna Paksha
            paksha = 0.0
            moon_dist_from_full = abs(moon_sun_dist - 180)  # 0 at new moon, 180 at full moon
            waxing_phase = moon_sun_dist / 180.0  # 0..1 (new to full)
            
            benefics = ["Moon", "Mercury", "Jupiter", "Venus"]
            if p_name in benefics:
                if is_shukla_paksha:
                    paksha = 60.0 * waxing_phase  # Gains with waxing
            elif p_name in ["Sun", "Mars", "Saturn"]:
                if not is_shukla_paksha:
                    paksha = 60.0 * (1.0 - waxing_phase)  # Gains with waning"""

new_paksha = """            # Paksha Bala (Fortnight Strength, max 60 virupas)
            # Benefic strength = (Distance from New Moon) / 3 if <= 180, else (360 - Distance) / 3
            # Malefic strength = 60 - Benefic strength
            d_val = moon_sun_dist if moon_sun_dist <= 180.0 else 360.0 - moon_sun_dist
            benefic_paksha = d_val / 3.0
            malefic_paksha = 60.0 - benefic_paksha
            
            benefics = ["Moon", "Mercury", "Jupiter", "Venus"]
            if p_name in benefics:
                paksha = benefic_paksha
            elif p_name in ["Sun", "Mars", "Saturn"]:
                paksha = malefic_paksha
            else:
                paksha = 0.0"""

if old_paksha in content:
    content = content.replace(old_paksha, new_paksha)
else:
    print("Failed to replace paksha")

with open('strength_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("strength_engine patched.")
