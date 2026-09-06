from vedic_models import Chart, Planet
from typing import Dict, Any, List

class PlanetEngine:
    @staticmethod
    def analyze_planet(chart: Chart, planet_name: str) -> Dict[str, Any]:
        planet = chart.planets.get(planet_name)
        if not planet:
            return {"error": f"Planet {planet_name} not found."}
            
        # 1. Base Attributes
        base = {
            "sign": planet.sign,
            "house": planet.house,
            "degree": planet.degree,
            "retrograde": planet.retrograde,
            "dignity": planet.dignity
        }
        
        # 2. Strength Profile
        strength = {
            "shadbala_total": planet.shadbala.get("total", 0),
            "sthana_bala": planet.shadbala.get("sthana_bala", 0),
            "dig_bala": planet.shadbala.get("dig_bala", 0),
            "kala_bala": planet.shadbala.get("kala_bala", 0),
            "cheshta_bala": planet.shadbala.get("cheshta_bala", 0)
        }
        
        # 3. Dispositor Profile
        dispositor_info = {
            "lord": planet.dispositor,
            "chain": planet.dispositor_chain,
            "is_parivartana": planet.is_parivartana
        }
        
        # 4. Conditions
        conditions = {
            "combust": planet.combustion.get("status", False),
            "avastha": planet.avasthas.get("balaadi", "Unknown")
        }
        
        # 5. Influence (Aspects & Conjunctions)
        influence = {
            "aspects_houses": planet.aspects_houses,
            "aspected_by": planet.aspected_by,
            "conjunct_with": planet.conjunct_with
        }
        
        # 6. Karaka Roles
        karakas = {
            "natural": planet.natural_karakas,
            "chara": planet.chara_karaka
        }
        
        # 7. Ownership
        ownership = {
            "owns_houses": planet.owns_houses
        }
        
        return {
            "planet": planet_name,
            "base": base,
            "strength": strength,
            "dispositor": dispositor_info,
            "conditions": conditions,
            "influence": influence,
            "karakas": karakas,
            "ownership": ownership,
            "functional_role": getattr(planet, "functional_role", ""),
            "compound_friendships": getattr(planet, "compound_friendships", {})
        }
