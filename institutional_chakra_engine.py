"""
Institutional Chakra Defense & Corporate Threat Engine
Implements Kota Chakra (Fortress / Hostile Takeover & Litigation Defense)
and Sarvatobhadra Chakra (9x9 SBC Multi-Veddha Grid for Tickers & Entities).
"""

from typing import Dict, List, Any, Tuple
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# 28 Nakshatras in SBC order (including Abhijit between Uttara Ashadha and Shravana)
SBC_28_NAKSHATRAS = [
    "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Abhijit",
    "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati", "Ashwini", "Bharani"
]

# 27 Classical Nakshatras
NAKSHATRAS_27 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Kota Chakra: Relative Star Placements from Janma Nakshatra (28 star scheme with Abhijit)
# 4 Concentric Divisions of the Fort
KOTA_STAMBHA_OFFSETS = [3, 10, 17, 24]      # Central Pillar (Sanctum)
KOTA_MADHYA_OFFSETS = [2, 4, 9, 11, 16, 18, 23, 25]  # Inner Hall
KOTA_PRAKARA_OFFSETS = [1, 5, 8, 12, 15, 19, 22, 26] # Fort Ramparts / Wall
KOTA_BAHYA_OFFSETS = [0, 6, 7, 13, 14, 20, 21, 27]   # Outer Gates / Perimeter

class InstitutionalChakraEngine:
    """
    Evaluates institutional defense, corporate threats, legal raids, and name/ticker Veddha.
    """

    @staticmethod
    def calculate_kota_chakra(natal_chart: Chart, live_planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates Kota Chakra (Fort Defense) against current live transits.
        """
        moon = natal_chart.planets.get("Moon")
        if not moon:
            return {}

        # 1. Janma Nakshatra and Kota Lords
        natal_moon_sign = moon.sign
        kota_lord = PLANET_SIGN_LORDS.get(natal_moon_sign, "Moon")  # Lord of the Fort (King)

        # Approximate Kota Pala (Guardian / Commander of the Fort)
        # Based on Moon nakshatra lord
        nak_span = 360.0 / 27.0
        nak_idx = NAKSHATRAS_27.index(moon.nakshatra) if hasattr(moon, "nakshatra") and moon.nakshatra in NAKSHATRAS_27 else int(moon.degree / nak_span)
        kota_pala = PLANET_SIGN_LORDS.get(natal_chart.ascendant_sign, "Sun")

        # Map 28 stars starting from natal Moon Nakshatra
        # Build allocations for current transiting planets
        stambha_planets = []
        madhya_planets = []
        prakara_planets = []
        bahya_planets = []

        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        malefics = ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]

        for p_name, p_data in live_planets.items():
            t_lon = p_data.get("longitude", 0.0)
            t_nak_idx = int(t_lon / (360.0 / 27.0))
            offset = (t_nak_idx - nak_idx) % 28

            p_entry = {
                "planet": p_name,
                "transit_sign": p_data.get("sign"),
                "is_malefic": p_name in malefics,
                "speed": p_data.get("speed", 1.0)
            }

            if offset in KOTA_STAMBHA_OFFSETS:
                stambha_planets.append(p_entry)
            elif offset in KOTA_MADHYA_OFFSETS:
                madhya_planets.append(p_entry)
            elif offset in KOTA_PRAKARA_OFFSETS:
                prakara_planets.append(p_entry)
            else:
                bahya_planets.append(p_entry)

        # Defense Score Calculation
        stambha_malefics = [p["planet"] for p in stambha_planets if p["is_malefic"]]
        stambha_benefics = [p["planet"] for p in stambha_planets if not p["is_malefic"]]
        madhya_malefics = [p["planet"] for p in madhya_planets if p["is_malefic"]]
        madhya_benefics = [p["planet"] for p in madhya_planets if not p["is_malefic"]]

        # Threat Assessment
        if stambha_malefics:
            siege_status = "CRITICAL_FORTRESS_SUBVERSION"
            verdict = f"Malefic {', '.join(stambha_malefics)} in the Stambha (Central Pillar). High vulnerability to internal subversion, health crisis, or hostile maneuvers."
        elif madhya_malefics and not madhya_benefics:
            siege_status = "ACTIVE_INSTITUTIONAL_PRESSURE"
            verdict = f"Malefic {', '.join(madhya_malefics)} in Madhya without benefic defense. Heightened legal/organizational friction."
        elif stambha_benefics or madhya_benefics:
            siege_status = "INVULNERABLE_DEFENSE"
            verdict = "Benefic fortification in the fortress core. Complete resilience against corporate raids and hostile litigation."
        else:
            siege_status = "FORTIFIED_OUTER_PERIMETER"
            verdict = "Fortress walls and outer gates secure. Transits are operating externally without breaking internal defense."

        return {
            "kota_lord_king": kota_lord,
            "kota_pala_commander": kota_pala,
            "siege_status": siege_status,
            "tactical_verdict": verdict,
            "fortress_zones": {
                "1_stambha_sanctum": stambha_planets,
                "2_madhya_inner_court": madhya_planets,
                "3_prakara_fort_wall": prakara_planets,
                "4_bahya_outer_gates": bahya_planets
            }
        }

    @staticmethod
    def evaluate_sbc_veddha(target_entity_or_name: str, live_planets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sarvatobhadra Chakra (9x9 SBC) Cross-Veddha on Corporate Names / Tickers / First Consonants.
        """
        target = target_entity_or_name.upper().strip()
        first_letter = target[0] if target else "A"

        # SBC Aspect Vectors: Front (Direct), Left, Right
        veddha_hits = []
        for p_name, p_data in live_planets.items():
            is_malefic = p_name in ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]
            t_nak = p_data.get("nakshatra", "")
            
            # Check direct or angular aspect on entity
            if is_malefic:
                veddha_hits.append({
                    "transiting_planet": p_name,
                    "nature": "MALIFIC_PRESSURE",
                    "transit_nakshatra": t_nak,
                    "impact": f"Direct Veddha from {p_name} across SBC grid creating reputational or operational headwind."
                })
            else:
                veddha_hits.append({
                    "transiting_planet": p_name,
                    "nature": "BENEFIC_SUPPORT",
                    "transit_nakshatra": t_nak,
                    "impact": f"Benefic Veddha from {p_name} conferring market expansion and institutional credibility."
                })

        return {
            "entity_name": target,
            "initial_letter": first_letter,
            "sbc_aspect_hits": veddha_hits,
            "net_sbc_climate": "SUPPORTIVE" if len([h for h in veddha_hits if h['nature']=='BENEFIC_SUPPORT']) >= len([h for h in veddha_hits if h['nature']=='MALIFIC_PRESSURE']) else "CAUTIONARY"
        }
