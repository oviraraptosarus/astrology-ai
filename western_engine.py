import swisseph as swe
from typing import Dict, Any, List

class WesternEngine:
    ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
                    
    PLANETS = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }

    @classmethod
    def get_sign(cls, lon: float) -> str:
        idx = int(lon // 30)
        return cls.ZODIAC_SIGNS[idx]

    @classmethod
    def get_aspect(cls, dist: float) -> str:
        orb = 8.0
        if dist <= orb or dist >= 360 - orb:
            return "Conjunction"
        if abs(dist - 60) <= orb:
            return "Sextile"
        if abs(dist - 90) <= orb:
            return "Square"
        if abs(dist - 120) <= orb:
            return "Trine"
        if abs(dist - 180) <= orb:
            return "Opposition"
        return None

    @classmethod
    def calculate_chart(cls, year: int, month: int, day: int, hour: float, lat: float, lon: float) -> dict:
        """Calculates a Western Tropical Chart with Placidus houses."""
        swe.set_ephe_path('ephe')
        
        # Calculate UTC Julian Day
        jd = swe.julday(year, month, day, hour)
        
        # Calculate Placidus Houses (Tropical) with High-Latitude Polar Fallback
        # b'P' for Placidus, b'E' for Equal House fallback
        try:
            cusps, ascmc = swe.houses(jd, lat, lon, b'P')
        except Exception:
            cusps, ascmc = swe.houses(jd, lat, lon, b'E')
        
        ascendant_lon = ascmc[0]
        mc_lon = ascmc[1]
        
        houses = {}
        for i in range(12):
            houses[i+1] = {
                "sign": cls.get_sign(cusps[i]),
                "degree": round(cusps[i] % 30, 2),
                "absolute_degree": round(cusps[i], 2)
            }
            
        planets = {}
        for name, p_id in cls.PLANETS.items():
            res, _ = swe.calc_ut(jd, p_id, swe.FLG_SWIEPH)
            p_lon = res[0]
            speed = res[3]
            
            # Determine which house the planet falls in
            house_placed = 12
            for i in range(11):
                h1 = cusps[i]
                h2 = cusps[i+1]
                if h1 < h2:
                    if h1 <= p_lon < h2:
                        house_placed = i + 1
                        break
                else: # crosses Aries point
                    if p_lon >= h1 or p_lon < h2:
                        house_placed = i + 1
                        break
            # Check 12th house wrap
            h1 = cusps[11]
            h2 = cusps[0]
            if house_placed == 12:
                if h1 < h2:
                    if h1 <= p_lon < h2:
                        house_placed = 12
                else:
                    if p_lon >= h1 or p_lon < h2:
                        house_placed = 12
            
            planets[name] = {
                "sign": cls.get_sign(p_lon),
                "degree": round(p_lon % 30, 2),
                "absolute_degree": round(p_lon, 2),
                "retrograde": speed < 0 if name not in ["Sun", "Moon"] else False,
                "house": house_placed
            }
            
        # Calculate Aspects
        aspects = []
        planet_names = list(planets.keys())
        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                p1 = planet_names[i]
                p2 = planet_names[j]
                d1 = planets[p1]["absolute_degree"]
                d2 = planets[p2]["absolute_degree"]
                
                dist = abs(d1 - d2)
                if dist > 180:
                    dist = 360 - dist
                    
                aspect_name = cls.get_aspect(dist)
                if aspect_name:
                    aspects.append({
                        "planet1": p1,
                        "planet2": p2,
                        "aspect": aspect_name,
                        "orb": round(abs(dist - {"Conjunction":0, "Sextile":60, "Square":90, "Trine":120, "Opposition":180}[aspect_name]), 2)
                    })
                    
        return {
            "Ascendant": {
                "sign": cls.get_sign(ascendant_lon),
                "degree": round(ascendant_lon % 30, 2)
            },
            "Midheaven": {
                "sign": cls.get_sign(mc_lon),
                "degree": round(mc_lon % 30, 2)
            },
            "Planets": planets,
            "Houses": houses,
            "Aspects": aspects
        }
