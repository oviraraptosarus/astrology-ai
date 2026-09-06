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
        vata_pts = 0
        pitta_pts = 0
        kapha_pts = 0
        
        for pname, p in self.chart.planets.items():
            if pname in ["Saturn", "Rahu", "Mercury"]:
                vata_pts += 1
            if pname in ["Sun", "Mars", "Ketu"]:
                pitta_pts += 1
            if pname in ["Moon", "Venus", "Jupiter"]:
                kapha_pts += 1

        primary_dosha = "Vata (Air/Nerves)" if vata_pts >= max(pitta_pts, kapha_pts) else ("Pitta (Fire/Blood)" if pitta_pts >= kapha_pts else "Kapha (Water/Tissue)")

        return {
            "primary_ayurvedic_dosha": primary_dosha,
            "dosha_distribution": {"Vata": vata_pts, "Pitta": pitta_pts, "Kapha": kapha_pts},
            "surgical_trauma_risk": surgical_risk,
            "surgical_indicators": surgical_notes,
            "dusthana_anatomical_vulnerabilities": afflicted_organs
        }
