"""
Prescriptive Remedial Engineering Engine
Implements Vedic Beeja Mantras, Count-based Japa, Astronomically Timed Daana (Hora/Day),
Lal Kitab Symbolic Upayas, Ayurvedic Lifestyle Prescriptions, and Strict Gemstone Safety.
"""

from typing import Dict, List, Any, Optional
from vedic_models import Chart, Planet

class RemedyEngine:
    """
    Comprehensive multi-tradition remedial matrix.
    """

    REMEDY_DATABASE = {
        "Sun": {
            "gemstone": "Ruby (Manikya)",
            "metal": "Gold or Copper",
            "finger": "Ring Finger",
            "vedic_mantra": "Om Hram Hreem Hroum Sah Suryaya Namah",
            "gayatri_mantra": "Om Bhaskaraya Vidmahe Divakaraya Dheemahi Tanno Suryah Prachodayat",
            "japa_count": "7,000 recitations at dawn",
            "charity_items": ["Wheat", "Jaggery (Gur)", "Copper vessel", "Ruby red flowers", "Gold"],
            "charity_day": "Sunday",
            "charity_hora": "Sun Hora (Sunrise or 1st/8th hour after sunrise)",
            "receiving_entity": "Temple priests, father figures, or visually impaired persons",
            "lal_kitab_upayas": [
                "Offer water in a copper vessel to the rising Sun daily.",
                "Serve and take blessings from father and paternal elders.",
                "Avoid wearing dark blue or black caps/headgear."
            ],
            "ayurvedic_dosha": "Pitta (Fire/Vitality)",
            "lifestyle": "Wake before sunrise, practice Surya Namaskar, avoid excessive pride and arrogance."
        },
        "Moon": {
            "gemstone": "Pearl (Moti) or Moonstone",
            "metal": "Pure Silver",
            "finger": "Little Finger",
            "vedic_mantra": "Om Shram Shreem Shroum Sah Chandraya Namah",
            "gayatri_mantra": "Om Ksheeraputraya Vidmahe Amrutatatvaya Dheemahi Tanno Chandrah Prachodayat",
            "japa_count": "11,000 recitations in the evening",
            "charity_items": ["Rice", "Cow milk", "White sweets", "Silver coin", "White conch shell"],
            "charity_day": "Monday",
            "charity_hora": "Moon Hora (Evening or Monday morning)",
            "receiving_entity": "Mother figures, elderly women, or orphanages",
            "lal_kitab_upayas": [
                "Keep a square silver piece in your wallet or pocket.",
                "Take blessings from your mother by touching her feet daily.",
                "Avoid drinking milk directly at night if Moon is afflicted."
            ],
            "ayurvedic_dosha": "Kapha / Pitta (Fluid Balance & Mind)",
            "lifestyle": "Maintain emotional stillness through Pranayama, drink water stored in silver vessels."
        },
        "Mars": {
            "gemstone": "Red Coral (Moonga)",
            "metal": "Copper or Gold",
            "finger": "Ring Finger",
            "vedic_mantra": "Om Kram Kreem Kroum Sah Bhaumaya Namah",
            "gayatri_mantra": "Om Angarakaya Vidmahe Shaktihastaya Dheemahi Tanno Bhaumah Prachodayat",
            "japa_count": "10,000 recitations on Tuesdays",
            "charity_items": ["Red lentils (Masoor Dal)", "Jaggery", "Red cloth", "Copper utensils", "Sweets"],
            "charity_day": "Tuesday",
            "charity_hora": "Mars Hora (Tuesday morning)",
            "receiving_entity": "Soldiers, athletes, younger brothers, or emergency workers",
            "lal_kitab_upayas": [
                "Recite Hanuman Chalisa daily and apply orange Sindoor on forehead.",
                "Feed sweet rotis to stray dogs or birds.",
                "Keep good relations with younger brothers and avoid aggressive outbursts."
            ],
            "ayurvedic_dosha": "Pitta (Blood, Muscles, Marrow)",
            "lifestyle": "Engage in disciplined physical training/gym, avoid non-vegetarian food on Tuesdays."
        },
        "Mercury": {
            "gemstone": "Emerald (Panna) or Green Tourmaline",
            "metal": "Gold or Bronze",
            "finger": "Little Finger",
            "vedic_mantra": "Om Bram Breem Broum Sah Budhaya Namah",
            "gayatri_mantra": "Om Saumyarupaya Vidmahe Vaneshaya Dheemahi Tanno Budhah Prachodayat",
            "japa_count": "9,000 recitations at noon",
            "charity_items": ["Green Moong Dal", "Green vegetables", "Spinach", "Green cloth", "Bronze items"],
            "charity_day": "Wednesday",
            "charity_hora": "Mercury Hora (Wednesday)",
            "receiving_entity": "Students, scholars, small children, or animal shelters (cows)",
            "lal_kitab_upayas": [
                "Feed fresh green grass or spinach to cows on Wednesday mornings.",
                "Clean your teeth with alum (Fitkari) powder.",
                "Keep all commercial and financial agreements written and verified."
            ],
            "ayurvedic_dosha": "Vata / Pitta (Nervous System, Speech, Skin)",
            "lifestyle": "Practice vocal recitation, chanting, and maintain clarity in financial documentation."
        },
        "Jupiter": {
            "gemstone": "Yellow Sapphire (Pukhraj) or Topaz",
            "metal": "Gold or Brass",
            "finger": "Index Finger",
            "vedic_mantra": "Om Gram Greem Groum Sah Gurave Namah",
            "gayatri_mantra": "Om Gurudevaya Vidmahe Parabrahmane Dheemahi Tanno Guruh Prachodayat",
            "japa_count": "19,000 recitations in the morning",
            "charity_items": ["Chana Dal (Bengal gram)", "Turmeric (Haldi)", "Bananas", "Yellow cloth", "Gold/Brass"],
            "charity_day": "Thursday",
            "charity_hora": "Jupiter Hora (Thursday morning)",
            "receiving_entity": "Gurus, mentors, Vedic scholars, educational institutions",
            "lal_kitab_upayas": [
                "Apply yellow saffron or turmeric tilak on the forehead and navel daily.",
                "Water a Peepal tree without touching it on Thursdays.",
                "Never insult or disrespect teachers, elders, or spiritual guides."
            ],
            "ayurvedic_dosha": "Kapha (Liver, Fat, Wisdom)",
            "lifestyle": "Pursue continuous philosophical study, mentor others, and maintain righteous conduct."
        },
        "Venus": {
            "gemstone": "Diamond (Heera) or White Zircon",
            "metal": "Platinum, White Gold, or Silver",
            "finger": "Middle or Little Finger",
            "vedic_mantra": "Om Dram Dreem Droum Sah Shukraya Namah",
            "gayatri_mantra": "Om Bhrigujaya Vidmahe Divyadehaya Dheemahi Tanno Shukrah Prachodayat",
            "japa_count": "16,000 recitations in the evening",
            "charity_items": ["White sugar", "Ghee", "Curd (Yogurt)", "White silk cloth", "Cosmetics/Perfumes"],
            "charity_day": "Friday",
            "charity_hora": "Venus Hora (Friday morning/evening)",
            "receiving_entity": "Artists, women in need, or charitable marriage trusts",
            "lal_kitab_upayas": [
                "Keep your living spaces, clothing, and vehicles impeccably clean and fragrant.",
                "Feed sweet white rice/kheer to young girls (Kanya Puja).",
                "Maintain fidelity in partnerships and treat spouse with supreme respect."
            ],
            "ayurvedic_dosha": "Kapha / Vata (Reproductive System, Eyes, Hormones)",
            "lifestyle": "Appreciate classical arts, avoid wearing unwashed or torn clothing."
        },
        "Saturn": {
            "gemstone": "Blue Sapphire (Neelam) or Amethyst",
            "metal": "Iron or Panchadhatu",
            "finger": "Middle Finger",
            "vedic_mantra": "Om Pram Preem Proum Sah Shanaischaraya Namah",
            "gayatri_mantra": "Om Nilanjanaya Vidmahe Chhayamartandaya Dheemahi Tanno Mandah Prachodayat",
            "japa_count": "23,000 recitations after sunset",
            "charity_items": ["Black sesame seeds (Til)", "Mustard oil", "Iron items", "Black blankets", "Urad Dal"],
            "charity_day": "Saturday",
            "charity_hora": "Saturn Hora (Saturday evening)",
            "receiving_entity": "Laborers, elderly persons, sanitation workers, or disabled individuals",
            "lal_kitab_upayas": [
                "Donate mustard oil after seeing your face reflection in it (*Chhaya Daan*).",
                "Serve food or biscuits to black dogs, crows, and laborers on Saturdays.",
                "Avoid alcohol, non-vegetarian food, and laziness on Saturdays."
            ],
            "ayurvedic_dosha": "Vata (Bones, Joints, Longevity)",
            "lifestyle": "Practice punctuality, maintain rigorous discipline, and assist the working class."
        },
        "Rahu": {
            "gemstone": "Hessonite (Gomed) or Spessartite",
            "metal": "Silver or Ashtadhatu",
            "finger": "Middle Finger",
            "vedic_mantra": "Om Bhram Bhreem Bhroum Sah Rahave Namah",
            "gayatri_mantra": "Om Nagadhwajaya Vidmahe Padmahastaya Dheemahi Tanno Rahuh Prachodayat",
            "japa_count": "18,000 recitations at midnight",
            "charity_items": ["Seven grains (Sapta Dhanya)", "Black blankets", "Lead items", "Blue cloth", "Coconut"],
            "charity_day": "Saturday (or Wednesday evening)",
            "charity_hora": "Rahu Kaal or Saturn Hora",
            "receiving_entity": "Lepers, sweepers, or stray animal shelters",
            "lal_kitab_upayas": [
                "Immerse raw dry coconuts in flowing water on Saturdays (*Jal Pravah*).",
                "Keep electrical appliances and electronic devices in your home fully functional.",
                "Avoid gambling, speculative greed, and ungrounded obsessions."
            ],
            "ayurvedic_dosha": "Vata (Psychological surges, Toxins, Illusions)",
            "lifestyle": "Practice grounding meditation in nature, maintain clean toilets and roof terraces."
        },
        "Ketu": {
            "gemstone": "Cat's Eye (Lehsuniya) or Chrysoberyl",
            "metal": "Silver or Gold",
            "finger": "Ring or Middle Finger",
            "vedic_mantra": "Om Sram Sreem Sroum Sah Ketave Namah",
            "gayatri_mantra": "Om Ashwadhwajaya Vidmahe Shoolahastaya Dheemahi Tanno Ketuh Prachodayat",
            "japa_count": "17,000 recitations in the evening",
            "charity_items": ["Two-colored blanket (Black & White)", "Sesame seeds", "Warm clothing", "Sour foods"],
            "charity_day": "Tuesday or Thursday",
            "charity_hora": "Mars/Jupiter Hora",
            "receiving_entity": "Monks, spiritual seekers, temples, or stray dogs",
            "lal_kitab_upayas": [
                "Feed multi-colored or black-and-white stray dogs daily.",
                "Donate a two-colored blanket to a temple or ascetic.",
                "Establish a daily routine of silent meditation and non-attachment."
            ],
            "ayurvedic_dosha": "Pitta (Spine, Karmic blocks, Hidden roots)",
            "lifestyle": "Engage in silent solitary walks, Pranayama, and study of sacred scriptures."
        }
    }

    def __init__(self):
        pass

    def get_remedy_for_planet(self, planet_name: str, is_benefic: bool = False, is_afflicted: bool = False) -> Dict[str, Any]:
        planet = planet_name.capitalize()
        if planet not in self.REMEDY_DATABASE:
            return {}

        data = self.REMEDY_DATABASE[planet]
        
        # Gemstone Safety Protocol:
        # Never wear gemstones for afflicted, combust, or dusthana lords.
        recommend_gemstone = is_benefic and not is_afflicted

        return {
            "planet": planet,
            "vedic_mantra": data["vedic_mantra"],
            "gayatri_mantra": data["gayatri_mantra"],
            "japa_count": data["japa_count"],
            "daana_charity": {
                "items": data["charity_items"],
                "prescribed_day": data["charity_day"],
                "astronomical_timing": data["charity_hora"],
                "receiving_entity": data["receiving_entity"]
            },
            "lal_kitab_upayas": data["lal_kitab_upayas"],
            "ayurvedic_lifestyle": {
                "dosha": data["ayurvedic_dosha"],
                "protocol": data["lifestyle"]
            },
            "gemstone_verdict": {
                "recommendation": f"Wear {data['gemstone']} set in {data['metal']} on the {data['finger']}." if recommend_gemstone else f"Do NOT wear {data['gemstone']}.",
                "status": "APPROVED_BENEFIC" if recommend_gemstone else "CONTRAINDICATED_AFFLICTED",
                "reason": "Planet is an unafflicted functional benefic." if recommend_gemstone else f"{planet} is afflicted, combust, or ruling a Dusthana. Gemstone would amplify negative radiation."
            }
        }

    def generate_dasha_remedies(self, mahadasha_lord: str, antardasha_lord: str) -> List[Dict[str, Any]]:
        remedies = []
        if mahadasha_lord:
            md_rem = self.get_remedy_for_planet(mahadasha_lord, is_benefic=False, is_afflicted=True)
            if md_rem:
                md_rem["dasha_context"] = f"Primary Propitiation for Mahadasha Lord ({mahadasha_lord})"
                remedies.append(md_rem)

        if antardasha_lord and antardasha_lord != mahadasha_lord:
            ad_rem = self.get_remedy_for_planet(antardasha_lord, is_benefic=False, is_afflicted=True)
            if ad_rem:
                ad_rem["dasha_context"] = f"Secondary Propitiation for Antardasha Lord ({antardasha_lord})"
                remedies.append(ad_rem)

        return remedies
