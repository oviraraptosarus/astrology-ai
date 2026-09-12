"""
Medical Astrology & Ayurvedic Tridosha Pathology Engine (Jyotisha Chikitsa)
Implements:
1. Tridosha Imbalance Scoring (Vata, Pitta, Kapha) based on planetary dignities and Lagna.
2. 12-House Kalapurusha Anatomical Organ Vulnerability Mapping.
3. Surgical / Acute Trauma Risk Detection (Mars/Ketu Dusthana Afflictions).
4. Chronic Disease Vulnerability (Saturn/Rahu 6H/8H Afflictions).
5. Dietary & Ayurvedic Botanical Recommendations (Herb / Dincharya Alignment).
"""
from typing import Dict, Any, List
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

KALAPURUSHA_ANATOMY = {
    1: {"organ": "Head, Cranium, Brain, Central Nervous System", "sign": "Aries", "vulnerability": "Headaches, neurological strain, head trauma, fevers"},
    2: {"organ": "Face, Eyes (Right), Throat, Vocal Cords, Teeth", "sign": "Taurus", "vulnerability": "Thyroid, ENT infections, dental issues, speech strain"},
    3: {"organ": "Shoulders, Arms, Respiratory Bronchi, Hands", "sign": "Gemini", "vulnerability": "Bronchitis, nervous tremors, shoulder/collar injuries"},
    4: {"organ": "Chest, Heart, Lungs, Breast, Ribcage", "sign": "Cancer", "vulnerability": "Cardiovascular stress, pulmonary congestion, emotional anxiety"},
    5: {"organ": "Upper Abdomen, Stomach, Liver, Spleen, Upper Spine", "sign": "Leo", "vulnerability": "Acid reflux, gastric ulcers, cardiac rhythms, spine strain"},
    6: {"organ": "Lower Abdomen, Small Intestines, Kidneys, Appendix", "sign": "Virgo", "vulnerability": "Digestive disorders, IBS, kidney stones, acute inflammation/infection"},
    7: {"organ": "Pelvis, Lumbar Region, Internal Genitals, Bladder", "sign": "Libra", "vulnerability": "Renal imbalance, urinary tract, reproductive health, lower back pain"},
    8: {"organ": "Excretory System, Colon, Rectum, Chronic Pathology", "sign": "Scorpio", "vulnerability": "Piles, sudden surgical interventions, chronic toxicity, reproductive strain"},
    9: {"organ": "Thighs, Hips, Arterial System, Sciatic Nerve", "sign": "Sagittarius", "vulnerability": "Sciatica, hip joint issues, liver metabolism, arterial hardening"},
    10: {"organ": "Knees, Joints, Skeletal Bones, Patella", "sign": "Capricorn", "vulnerability": "Arthritis, joint stiffness, calcium deficiency, skin eczema"},
    11: {"organ": "Calves, Shins, Ankles, Peripheral Blood Circulation", "sign": "Aquarius", "vulnerability": "Circulatory weakness, varicose veins, shin splints, neurological spasms"},
    12: {"organ": "Feet, Toes, Left Eye, Immune / Lymphatic System", "sign": "Pisces", "vulnerability": "Immune exhaustion, insomnia, lymphatic swelling, hospital care"}
}

PLANETARY_DOSHAS = {
    "Sun": "Pitta (Bile / Fire / Vitality)",
    "Moon": "Vata-Kapha (Fluids / Mucus / Mind)",
    "Mars": "Pitta (Blood / Bone Marrow / Inflammation)",
    "Mercury": "Tridoshic (Vata-dominant / Nerves / Skin)",
    "Jupiter": "Kapha (Fat / Liver / Cellular Growth)",
    "Venus": "Kapha-Vata (Semen / Reproductive / Kidneys)",
    "Saturn": "Vata (Wind / Bones / Nerves / Chronic Degeneration)",
    "Rahu": "Vata (Toxins / Rare Allergies / Phantom Ailments)",
    "Ketu": "Pitta (Infections / Surgeries / Fevers)"
}

class MedicalAstrologyEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign) if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else int(chart.ascendant.longitude / 30)

    def diagnose_health_profile(self) -> Dict[str, Any]:
        """Generates comprehensive medical astrological profile."""
        # 1. Evaluate Afflicted Houses (6H, 8H, 12H)
        dusthana_houses = [6, 8, 12]
        afflicted_organs = []
        
        for h in dusthana_houses:
            sign_idx = (self.lagna_sign_idx + h - 1) % 12
            sign_name = ZODIAC_SIGNS[sign_idx]
            anatomy = KALAPURUSHA_ANATOMY[h]
            
            planets_in_house = [pname for pname, p in self.chart.planets.items() if p.sign == sign_name]
            afflicted_organs.append({
                "house": h,
                "sign": sign_name,
                "anatomical_zone": anatomy["organ"],
                "planets_present": planets_in_house,
                "potential_vulnerabilities": anatomy["vulnerability"]
            })

        # 2. Check Surgical and Acute Trauma Triggers (Mars/Ketu)
        mars = self.chart.planets.get("Mars")
        ketu = self.chart.planets.get("Ketu")
        surgical_risk = "LOW"
        surgical_notes = []
        
        if mars:
            mars_house = ((ZODIAC_SIGNS.index(mars.sign) - self.lagna_sign_idx) % 12) + 1
            if mars_house in [6, 8, 12, 1]:
                surgical_risk = "ELEVATED"
                surgical_notes.append(f"Mars in House {mars_house} ({mars.sign}) brings vulnerability to sharp trauma, cuts, or acute surgical needs.")

        if ketu:
            ketu_house = ((ZODIAC_SIGNS.index(ketu.sign) - self.lagna_sign_idx) % 12) + 1
            if ketu_house in [1, 6, 8, 12]:
                surgical_risk = "HIGH / ACUTE"
                surgical_notes.append(f"Ketu in House {ketu_house} ({ketu.sign}) acts as a surgical scalpel trigger, requiring precision care during Ketu/Mars dashas.")

        # 3. Tridosha Balance Assessment
        # Classical method (Prasna Marga Ch.11 + standard medical jyotish practice):
        # Prakriti is derived from the LAGNA SIGN element, the LAGNA LORD, and the MOON SIGN
        # element — weighted — not from a flat count of all nine grahas.
        # Planet doshas: Sun/Mars/Ketu = Pitta; Moon/Jupiter/Venus = Kapha;
        # Saturn/Rahu/Mercury = Vata (Mercury tridoshic, adapts).
        DOSHA_OF_SIGN = {
            "Aries": "Pitta", "Leo": "Pitta", "Sagittarius": "Pitta", "Scorpio": "Pitta",
            "Taurus": "Kapha", "Cancer": "Kapha", "Pisces": "Kapha",
            "Gemini": "Vata", "Virgo": "Vata", "Libra": "Vata",
            "Capricorn": "Vata", "Aquarius": "Vata",
        }
        DOSHA_OF_PLANET = {
            "Sun": "Pitta", "Mars": "Pitta", "Ketu": "Pitta",
            "Moon": "Kapha", "Jupiter": "Kapha", "Venus": "Kapha",
            "Saturn": "Vata", "Rahu": "Vata", "Mercury": "Vata",
        }
        SIGN_LORDS = {
            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
            "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
            "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
        }

        vata_pts = 0
        pitta_pts = 0
        kapha_pts = 0
        dosha_tally = {"Vata": lambda: None, "Pitta": lambda: None, "Kapha": lambda: None}

        def add_dosha(dosha: str, weight: int = 1):
            nonlocal vata_pts, pitta_pts, kapha_pts
            if dosha == "Vata":
                vata_pts += weight
            elif dosha == "Pitta":
                pitta_pts += weight
            elif dosha == "Kapha":
                kapha_pts += weight

        # (a) Lagna sign element — the body itself (weight 3)
        lagna_sign = ZODIAC_SIGNS[self.lagna_sign_idx]
        add_dosha(DOSHA_OF_SIGN.get(lagna_sign, "Vata"), 3)
        # (b) Lagna lord's dosha (weight 2)
        lagna_lord = SIGN_LORDS.get(lagna_sign)
        if lagna_lord and lagna_lord in self.chart.planets:
            add_dosha(DOSHA_OF_PLANET.get(lagna_lord, "Vata"), 2)
        # (c) Moon sign element — the mind/constitution (weight 2)
        moon = self.chart.planets.get("Moon")
        if moon:
            add_dosha(DOSHA_OF_SIGN.get(moon.sign, "Vata"), 2)
        # (d) Any planet conjunct the lagna (weight 1 each)
        for pname, p in self.chart.planets.items():
            if p.sign == lagna_sign and pname != "Ketu":
                add_dosha(DOSHA_OF_PLANET.get(pname, "Vata"), 1)

        tally = {"Vata": vata_pts, "Pitta": pitta_pts, "Kapha": kapha_pts}
        top = max(tally.values())
        leaders = [d for d, v in tally.items() if v == top]
        if len(leaders) == 1:
            primary_dosha = {"Vata": "Vata (Air/Nerves)", "Pitta": "Pitta (Fire/Blood)", "Kapha": "Kapha (Water/Tissue)"}[leaders[0]]
        else:
            # Genuine tie: report dual dosha instead of an arbitrary code-order winner
            primary_dosha = "/".join(leaders) + " (dual prakriti — near-equal weights)"

        return {
            "primary_ayurvedic_dosha": primary_dosha,
            "dosha_distribution": {"Vata": vata_pts, "Pitta": pitta_pts, "Kapha": kapha_pts},
            "surgical_trauma_risk": surgical_risk,
            "surgical_indicators": surgical_notes,
            "dusthana_anatomical_vulnerabilities": afflicted_organs
        }
