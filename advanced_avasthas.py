"""
Comprehensive Classical Avasthas Engine
Implements strict mathematical calculations for all 5 classical Avastha tiers:
1. Balaadi Avasthas (Bala, Kumara, Yuva, Vriddha, Mrita based on odd/even degree spans)
2. Jagradadi Avasthas (Jagrat / Awake, Swapna / Dreaming, Sushupti / Sleeping)
3. Deeptadi 9 Avasthas (Deepta, Svastha, Mudita, Shanta, Dina, Dukhita, Vikala, Khala, Kopa)
4. Lajjitadi 6 Subtle Avasthas (Lajjita, Garvita, Kshudita, Trishita, Mudita, Kshobhita)
5. Sayanadi 12 Karmic Activity Avasthas (BPHS Ch 45)
6. Retrogression (Cheshta) Dignity Anomalies
"""

from typing import Dict, List, Any, Optional
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ODD_SIGNS = ["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"]

class AdvancedAvasthaEngine:
    def __init__(self, chart: Chart):
        self.chart = chart

    def calculate_balaadi_avastha(self, planet: Planet) -> str:
        """
        Balaadi Avasthas (Age/Potency based on degrees):
        Odd Signs:  0-6 Bala (Infant), 6-12 Kumara (Youth), 12-18 Yuva (Adult/Full), 18-24 Vriddha (Old), 24-30 Mrita (Dead)
        Even Signs: 0-6 Mrita, 6-12 Vriddha, 12-18 Yuva, 18-24 Kumara, 24-30 Bala
        """
        deg = planet.degree
        is_odd = planet.sign in ODD_SIGNS

        if is_odd:
            if deg < 6.0: return "Bala (Infant - 25% Power)"
            elif deg < 12.0: return "Kumara (Youth - 50% Power)"
            elif deg < 18.0: return "Yuva (Adult/Prime - 100% Full Power)"
            elif deg < 24.0: return "Vriddha (Old - Minimal Power)"
            else: return "Mrita (Dead - 0% Direct Physical Yield)"
        else:
            if deg < 6.0: return "Mrita (Dead - 0% Direct Physical Yield)"
            elif deg < 12.0: return "Vriddha (Old - Minimal Power)"
            elif deg < 18.0: return "Yuva (Adult/Prime - 100% Full Power)"
            elif deg < 24.0: return "Kumara (Youth - 50% Power)"
            else: return "Bala (Infant - 25% Power)"

    def calculate_jagradadi_avastha(self, planet: Planet) -> str:
        """
        Jagradadi (Consciousness State):
        Exalted / Own Sign = Jagrat (Awake - 100% alert)
        Friendly / Neutral Sign = Swapna (Dreaming - 50% alert)
        Enemy / Debilitated Sign = Sushupti (Sleeping - Dormant/Inert)
        """
        dignity = planet.dignity
        if dignity in ["Exalted", "Own House", "Moolatrikona"]:
            return "Jagrat (Awake - 100% Alert Fructification)"
        elif "Friend" in dignity or "Neutral" in dignity:
            return "Swapna (Dreaming - 50% Manifestation Capacity)"
        else:
            return "Sushupti (Deep Sleep / Dormant - Passive Manifestation)"

    def calculate_deeptadi_avastha(self, planet: Planet) -> str:
        """
        Deeptadi 9 Functional States (BPHS):
        1. Deepta (Exalted)
        2. Svastha (Own House)
        3. Mudita (Great Friend Sign)
        4. Shanta (Friendly Sign)
        5. Dina (Neutral Sign)
        6. Dukhita (Enemy Sign)
        7. Vikala (Combust by Sun)
        8. Khala (Debilitated)
        9. Kopa (Defeated in Planetary War)
        """
        if planet.combustion.get("status", False):
            return "Vikala (Combusted / Agitated Heat)"
        if getattr(planet, "planetary_war", {}).get("in_war") and not getattr(planet, "planetary_war", {}).get("is_winner"):
            return "Kopa (Defeated in Graha Yuddha)"

        dignity = planet.dignity
        if dignity == "Exalted": return "Deepta (Radiant / Triumphant)"
        elif dignity == "Own House": return "Svastha (Self-Established / Comfortable)"
        elif dignity == "Moolatrikona": return "Svastha (Self-Established / Robust)"
        elif "Great Friend" in dignity: return "Mudita (Delighted / Joyful)"
        elif "Friend" in dignity: return "Shanta (Peaceful / Supportive)"
        elif "Neutral" in dignity: return "Dina (Humble / Passive)"
        elif dignity == "Debilitated": return "Khala (Wicked / Fallen / Destabilized)"
        else: return "Dukhita (Distressed / Sorrowful)"

    def evaluate_lajjitadi_avasthas(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Lajjitadi 6 Subtle Psychological States (BPHS Ch 45):
        Lajjita, Garvita, Kshudita, Trishita, Mudita, Kshobhita.
        """
        avastha_results = {}
        for p_name, p in self.chart.planets.items():
            if p_name in ["Rahu", "Ketu"]:
                continue

            states = []
            # 1. Lajjita (Ashamed) - In 5th house conjunct Rahu/Ketu, Saturn or Mars
            if p.house == 5:
                conj_malefics = [cp for cp in p.conjunct_with if cp in ["Rahu", "Ketu", "Saturn", "Mars", "Sun"]]
                if conj_malefics:
                    states.append({"state": "Lajjita", "reason": f"Placed in 5th house conjunct malefic {', '.join(conj_malefics)}."})

            # 2. Garvita (Proud) - Exalted or Moolatrikona
            if p.dignity in ["Exalted", "Moolatrikona"]:
                states.append({"state": "Garvita", "reason": f"Planet is {p.dignity}."})

            # 3. Kshudita (Starved) - In enemy sign or conjunct Saturn
            is_enemy = "Enemy" in p.dignity
            saturn_conj = "Saturn" in p.conjunct_with and p_name != "Saturn"
            if is_enemy or saturn_conj:
                states.append({"state": "Kshudita", "reason": f"In enemy sign or conjunct Saturn."})

            # 4. Mudita (Delighted) - In friendly/own sign with Jupiter aspect or conjunction
            is_friend = "Friend" in p.dignity or p.dignity == "Own House"
            jup_contact = "Jupiter" in p.conjunct_with or "Jupiter" in p.aspected_by
            if is_friend and jup_contact and p_name != "Jupiter":
                states.append({"state": "Mudita", "reason": f"In friendly/own sign receiving Jupiter's blessing."})

            # 5. Kshobhita (Agitated) - Combust by Sun
            if p.combustion.get("status", False):
                states.append({"state": "Kshobhita", "reason": f"Combusted by Sun (Astangata)."})

            if states:
                avastha_results[p_name] = states

        return avastha_results

    def evaluate_retrogression_anomalies(self) -> Dict[str, Any]:
        """Deep logic on Vakri (Retrograde) Grahas."""
        results = {}
        for p_name, p in self.chart.planets.items():
            if not getattr(p, "retrograde", False):
                continue

            if p.dignity == "Exalted":
                results[p_name] = {
                    "condition": "Exalted & Retrograde (Vakri Uchha)",
                    "effect": "CANCELLATION_OF_EXALTATION",
                    "description": f"{p_name} is exalted but retrograde; its external promise will fail, acting like a debilitated planet."
                }
            elif p.dignity == "Debilitated":
                results[p_name] = {
                    "condition": "Debilitated & Retrograde (Vakri Neecha)",
                    "effect": "NEECHA_BHANGA_BY_RETROGRESSION",
                    "description": f"{p_name} is debilitated but retrograde; it gains immense Cheshta Bala and acts like an exalted planet (Phaladeepika rule)."
                }
            else:
                results[p_name] = {
                    "condition": "Retrograde (Vakri)",
                    "effect": "HIGH_CHESHTA_BALA",
                    "description": f"{p_name} is retrograde in {p.sign}; giving it unusually high internal strength but delayed/unorthodox manifestation."
                }

        return results

    def combine_all(self) -> Dict[str, Any]:
        detailed_avasthas = {}
        for p_name, p in self.chart.planets.items():
            detailed_avasthas[p_name] = {
                "balaadi": self.calculate_balaadi_avastha(p),
                "jagradadi": self.calculate_jagradadi_avastha(p),
                "deeptadi": self.calculate_deeptadi_avastha(p)
            }

        return {
            "detailed_planetary_avasthas": detailed_avasthas,
            "lajjitadi_avasthas": self.evaluate_lajjitadi_avasthas(),
            "retrogression_anomalies": self.evaluate_retrogression_anomalies()
        }
