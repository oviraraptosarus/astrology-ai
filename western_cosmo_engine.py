"""
Western Harmonic, Cosmobiology & Primary Directions Engine
Implements 90° Graphic Dial (4th Harmonic), Planetary Midpoint Trees (A/B = C),
and Primary Directions (1° Right Ascension = 1 Solar Year) for institutional milestones.
"""

from typing import Dict, List, Any, Tuple
from vedic_models import Chart, Planet

class WesternCosmoEngine:
    """
    Cosmobiology (Ebertin / Witte) and Harmonic Western Astro Engine.
    """

    @staticmethod
    def calculate_90_deg_dial(chart: Chart) -> Dict[str, Any]:
        """
        Maps all planetary positions onto the 90° Graphic Dial (4th Harmonic: Conjunctions, Squares, Oppositions).
        """
        dial_positions = {}
        for name, planet in chart.planets.items():
            if name == "Ascendant":
                continue
            # Full longitude (0-360)
            from varga_engine import VargaEngine
            s_idx = VargaEngine.get_sign_index(planet.sign)
            lon = (s_idx * 30.0) + planet.degree
            dial_deg = lon % 90.0
            dial_positions[name] = {
                "sign": planet.sign,
                "degree": planet.degree,
                "full_longitude": round(lon, 4),
                "dial_90_degree": round(dial_deg, 4),
                "dial_formatted": f"{int(dial_deg)}°{int((dial_deg % 1) * 60):02d}'"
            }

        # Calculate Midpoint Trees (A/B = C within <= 1.0 deg orb on 90° dial)
        midpoints = []
        p_names = list(dial_positions.keys())

        for i in range(len(p_names)):
            for j in range(i, len(p_names)):
                p1 = p_names[i]
                p2 = p_names[j]
                d1 = dial_positions[p1]["dial_90_degree"]
                d2 = dial_positions[p2]["dial_90_degree"]
                
                # Midpoint on 90 dial
                diff = abs(d1 - d2)
                if diff > 45.0:
                    mid = ((d1 + d2 + 90.0) / 2.0) % 90.0
                else:
                    mid = (d1 + d2) / 2.0

                # Check if any third planet occupies this midpoint
                for k_name in p_names:
                    k_deg = dial_positions[k_name]["dial_90_degree"]
                    orb = abs(k_deg - mid)
                    if orb > 45.0:
                        orb = 90.0 - orb
                    
                    if orb <= 1.0 and (k_name != p1 or p1 == p2):
                        midpoints.append({
                            "pair": f"{p1}/{p2}",
                            "direct_planet": k_name,
                            "midpoint_dial_deg": round(mid, 2),
                            "orb": round(orb, 3),
                            "configuration": f"{p1}/{p2} = {k_name}"
                        })

        return {
            "dial_90_positions": dial_positions,
            "active_midpoint_pictures": midpoints
        }

    @staticmethod
    def calculate_primary_directions(natal_ascendant_deg: float, age_years: float) -> Dict[str, Any]:
        """
        Computes Primary Directions (Ptolemy / Placidus):
        Key: 1° Arc of Direction = 1 Solar Year.
        """
        directed_asc_deg = (natal_ascendant_deg + age_years) % 360.0
        return {
            "current_age": age_years,
            "arc_of_direction_degrees": round(age_years, 2),
            "directed_ascendant_longitude": round(directed_asc_deg, 2)
        }
