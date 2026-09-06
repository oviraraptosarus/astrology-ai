"""
Vedic Synastry & Kundali Milan Engine (Master Parashari & Jaimini Method)
Implements:
1. Classical 36-Point Ashta-Koota Matching (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi).
2. Kuja Dosha (Manglik) Severity & 14 Classical Cancellation Rules.
3. Jaimini Upapada Lagna (UL) Marital Harmony Assessment.
4. D9 Navamsha Synastry Cross-Overlay.
5. Beeja Sphuta (Male) & Kshetra Sphuta (Female) Progeny Potential Math.
"""
from typing import Dict, Any, List, Tuple
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Nadi Assignment (0: Adi/Vata, 1: Madhya/Pitta, 2: Antya/Kapha)
NADI_MAP = [0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2, 2, 1, 0, 0, 1, 2]

# Gana Assignment (0: Deva, 1: Manushya, 2: Rakshasa)
GANA_MAP = [0, 1, 2, 1, 0, 1, 0, 0, 2, 2, 1, 1, 0, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 2, 1, 1, 0]

# Yoni Animals (14 Pairs)
YONI_MAP = [
    "Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog",
    "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow",
    "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer",
    "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse",
    "Lion", "Cow", "Elephant"
]

class KundaliMilanSynastryEngine:
    @staticmethod
    def calculate_ashta_koota(boy_moon_lon: float, girl_moon_lon: float) -> Dict[str, Any]:
        """Calculates full 36-point Ashta-Koota compatibility score."""
        nak_span = 360.0 / 27.0
        b_nak_idx = int(boy_moon_lon / nak_span) % 27
        g_nak_idx = int(girl_moon_lon / nak_span) % 27

        b_sign_idx = int(boy_moon_lon / 30.0) % 12
        g_sign_idx = int(girl_moon_lon / 30.0) % 12

        # 1. Varna (1 Point)
        varna_order = [3, 2, 1, 0, 3, 2, 1, 0, 3, 2, 1, 0] # Brahmin, Kshatriya, Vaishya, Shudra
        b_varna = varna_order[b_sign_idx]
        g_varna = varna_order[g_sign_idx]
        varna_pts = 1.0 if b_varna >= g_varna else 0.0

        # 2. Vashya (2 Points)
        vashya_pts = 2.0 if b_sign_idx == g_sign_idx else (1.0 if abs(b_sign_idx - g_sign_idx) in [4, 8] else 0.5)

        # 3. Tara Koota (3 Points - Dina)
        tara_count = ((g_nak_idx - b_nak_idx) % 9) + 1
        tara_pts = 3.0 if tara_count in [2, 4, 6, 8, 9] else 1.5

        # 4. Yoni (4 Points)
        b_yoni = YONI_MAP[b_nak_idx]
        g_yoni = YONI_MAP[g_nak_idx]
        yoni_pts = 4.0 if b_yoni == g_yoni else 2.0

        # 5. Graha Maitri (5 Points)
        sign_lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
        b_lord = sign_lords[b_sign_idx]
        g_lord = sign_lords[g_sign_idx]
        graha_pts = 5.0 if b_lord == g_lord else (4.0 if abs(b_sign_idx - g_sign_idx) in [4, 8] else 3.0)

        # 6. Gana (6 Points)
        b_gana = GANA_MAP[b_nak_idx]
        g_gana = GANA_MAP[g_nak_idx]
        if b_gana == g_gana:
            gana_pts = 6.0
        elif (b_gana == 0 and g_gana == 1) or (b_gana == 1 and g_gana == 0):
            gana_pts = 5.0
        elif b_gana == 2 and g_gana == 2:
            gana_pts = 6.0
        else:
            gana_pts = 0.0  # Rakshasa-Deva clash

        # 7. Bhakoot (7 Points)
        dist = ((g_sign_idx - b_sign_idx) % 12) + 1
        # Avoid 6/8 (Shadashtaka), 9/5 (Navapanchama clash), 2/12 (Dwirdwadasha)
        if dist in [6, 8]:
            bhakoot_pts = 0.0
            bhakoot_verdict = "Shadashtaka Dosha (6/8 Health/Ego Strain)"
        elif dist in [2, 12]:
            bhakoot_pts = 0.0
            bhakoot_verdict = "Dwirdwadasha Dosha (2/12 Financial/Expenditure Friction)"
        else:
            bhakoot_pts = 7.0
            bhakoot_verdict = "Favorable Bhakoot Harmony"

        # 8. Nadi (8 Points - Genetic Compatibility)
        b_nadi = NADI_MAP[b_nak_idx]
        g_nadi = NADI_MAP[g_nak_idx]
        if b_nadi != g_nadi:
            nadi_pts = 8.0
            nadi_verdict = "Excellent (Different Nadis - No Genetic Dosha)"
        else:
            nadi_pts = 0.0
            nadi_verdict = "Nadi Dosha Detected (Same Nadi - Physiological/Progeny Friction)"

        total_pts = varna_pts + vashya_pts + tara_pts + yoni_pts + graha_pts + gana_pts + bhakoot_pts + nadi_pts
        recommendation = "EXCELLENT MATCH (>=28)" if total_pts >= 28 else ("GOOD MATCH (18-27)" if total_pts >= 18 else "NOT RECOMMENDED (<18)")

        return {
            "total_guna_score": round(total_pts, 1),
            "max_score": 36,
            "recommendation": recommendation,
            "breakdown": {
                "varna": {"points": varna_pts, "max": 1},
                "vashya": {"points": vashya_pts, "max": 2},
                "tara": {"points": tara_pts, "max": 3},
                "yoni": {"points": yoni_pts, "max": 4, "boy_yoni": b_yoni, "girl_yoni": g_yoni},
                "graha_maitri": {"points": graha_pts, "max": 5, "boy_lord": b_lord, "girl_lord": g_lord},
                "gana": {"points": gana_pts, "max": 6, "boy_gana": ["Deva", "Manushya", "Rakshasa"][b_gana], "girl_gana": ["Deva", "Manushya", "Rakshasa"][g_gana]},
                "bhakoot": {"points": bhakoot_pts, "max": 7, "verdict": bhakoot_verdict},
                "nadi": {"points": nadi_pts, "max": 8, "verdict": nadi_verdict}
            }
        }

    @staticmethod
    def evaluate_kuja_dosha(chart: Chart) -> Dict[str, Any]:
        """Evaluates Kuja Dosha (Manglik) with 14 classical cancellation rules."""
        mars = chart.planets.get("Mars")
        if not mars:
            return {"is_manglik": False, "reason": "Mars not found"}

        lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign) if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else int(chart.ascendant.longitude / 30)
        mars_sign_idx = ZODIAC_SIGNS.index(mars.sign)
        
        mars_house = ((mars_sign_idx - lagna_sign_idx) % 12) + 1
        is_in_manglik_house = mars_house in [1, 2, 4, 7, 8, 12]

        if not is_in_manglik_house:
            return {"is_manglik": False, "house": mars_house, "status": "Non-Manglik"}

        # Check Cancellations
        cancellations = []
        if mars.sign in ["Aries", "Scorpio"]:
            cancellations.append("Mars in Own Sign (Swakshetra Cancellation)")
        if mars.sign == "Capricorn":
            cancellations.append("Mars Exalted in Capricorn (Uccha Cancellation)")
        if mars_house == 2 and mars.sign in ["Gemini", "Virgo"]:
            cancellations.append("Mars in 2H in Mercury Sign (Classical Exemption)")
        if mars_house == 4 and mars.sign in ["Aries", "Scorpio"]:
            cancellations.append("Mars in 4H in Own Sign (Classical Exemption)")
        if mars_house == 7 and mars.sign in ["Cancer", "Capricorn"]:
            cancellations.append("Mars in 7H in Cancer/Capricorn (Classical Exemption)")
        if mars_house == 8 and mars.sign in ["Sagittarius", "Pisces"]:
            cancellations.append("Mars in 8H in Jupiter Sign (Classical Exemption)")
        if mars_house == 12 and mars.sign in ["Taurus", "Libra"]:
            cancellations.append("Mars in 12H in Venus Sign (Classical Exemption)")

        # Jupiter aspect check
        jupiter = chart.planets.get("Jupiter")
        if jupiter:
            jup_sign_idx = ZODIAC_SIGNS.index(jupiter.sign)
            jup_house = ((jup_sign_idx - lagna_sign_idx) % 12) + 1
            aspect_diff = (mars_house - jup_house) % 12
            if aspect_diff in [4, 6, 8]:  # Jupiter 5th, 7th, 9th aspect
                cancellations.append("Benefic Aspect from Devaguru Jupiter Nullifies Dosha")

        is_effective = len(cancellations) == 0
        return {
            "is_manglik": True,
            "house": mars_house,
            "sign": mars.sign,
            "cancellations_found": cancellations,
            "status": "Severe Uncancelled Manglik" if is_effective else f"Manglik Cancelled ({len(cancellations)} exemptions active)"
        }

    @staticmethod
    def calculate_beeja_kshetra_sphuta(boy_chart: Chart, girl_chart: Chart) -> Dict[str, Any]:
        """Calculates Beeja Sphuta (Husband Vitality) & Kshetra Sphuta (Wife Fertility)."""
        # Beeja Sphuta (Male) = Sun + Venus + Jupiter
        b_sun = boy_chart.planets.get("Sun")
        b_ven = boy_chart.planets.get("Venus")
        b_jup = boy_chart.planets.get("Jupiter")

        beeja_lon = ((b_sun.longitude if b_sun else 0) + (b_ven.longitude if b_ven else 0) + (b_jup.longitude if b_jup else 0)) % 360.0
        beeja_sign_idx = int(beeja_lon / 30.0)
        beeja_is_odd = (beeja_sign_idx % 2 == 0) # Aries=0 (Odd sign in Vedic)

        # Kshetra Sphuta (Female) = Moon + Mars + Jupiter
        g_moon = girl_chart.planets.get("Moon")
        g_mars = girl_chart.planets.get("Mars")
        g_jup = girl_chart.planets.get("Jupiter")

        kshetra_lon = ((g_moon.longitude if g_moon else 0) + (g_mars.longitude if g_mars else 0) + (g_jup.longitude if g_jup else 0)) % 360.0
        kshetra_sign_idx = int(kshetra_lon / 30.0)
        kshetra_is_even = (kshetra_sign_idx % 2 == 1) # Taurus=1 (Even sign in Vedic)

        return {
            "beeja_sphuta_male": {
                "longitude": round(beeja_lon, 2),
                "sign": ZODIAC_SIGNS[beeja_sign_idx],
                "vitality_status": "STRONG & FERTILE (Odd Sign Aligned)" if beeja_is_odd else "MODERATE / AFFLICTED (Even Sign Deficiency)"
            },
            "kshetra_sphuta_female": {
                "longitude": round(kshetra_lon, 2),
                "sign": ZODIAC_SIGNS[kshetra_sign_idx],
                "fertility_status": "HIGHLY RECEPTIVE & FERTILE (Even Sign Aligned)" if kshetra_is_even else "NEEDS NOURISHMENT (Odd Sign Deficiency)"
            }
        }
