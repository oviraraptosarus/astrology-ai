from typing import Dict, Any, List
from datetime import datetime
from vedic_models import Chart
from methodology_router import MethodologyRouter

class PrashnaEngine:
    """
    Evaluates Horary (Prashna) charts.
    Answers specific questions based on the time and location the question was asked/received.
    """
    
    @staticmethod
    def identify_karyabhava(domain: str) -> int:
        """
        Identifies the primary house representing the query (Karya Bhava).
        """
        mapping = {
            "CAREER": 10,
            "MARRIAGE": 7,
            "WEALTH": 2,
            "CHILDREN": 5,
            "HEALTH": 6, # 6th for disease, 1st for vitality
            "EDUCATION": 4,
            "PROPERTY": 4,
            "LITIGATION": 6,
            "TRAVEL": 9
        }
        return mapping.get(domain.upper(), 1) # Default to Lagna if unknown

    @staticmethod
    def evaluate_prashna(chart: Chart, question: str) -> Dict[str, Any]:
        """
        Evaluates a Prashna chart.
        The core principles of Prashna:
        1. Lagna Lord (Lagnesh) represents the Querent.
        2. Karya Bhava Lord (Karyaesh) represents the Object/Query.
        3. Ithasala Yoga (Applying aspect/conjunction) between Lagnesh and Karyaesh guarantees success.
        4. Easarpha Yoga (Separating aspect/conjunction) indicates failure or missed opportunity.
        """
        domain = MethodologyRouter.identify_domain(question)
        karya_bhava = PrashnaEngine.identify_karyabhava(domain)
        
        # 1. Identify Lagnesh (Querent)
        lagna_sign = chart.ascendant_sign
        lagnesh_name = chart.SIGN_LORDS[lagna_sign]
        lagnesh = chart.planets[lagnesh_name]
        
        # 2. Identify Karyaesh (Query)
        # Find the sign of the Karya Bhava (Ascendant + house offset)
        asc_idx = chart.get_sign_index(lagna_sign)
        karya_sign_idx = (asc_idx + karya_bhava - 1) % 12
        karya_sign = chart.ZODIAC_SIGNS[karya_sign_idx]
        karyaesh_name = chart.SIGN_LORDS[karya_sign]
        karyaesh = chart.planets[karyaesh_name]
        
        # 3. Evaluate Relationship (Tajaka Yogas)
        # In a full implementation, we'd calculate exact degrees to check if the faster planet 
        # is behind the slower planet (Ithasala) or ahead (Easarpha).
        # We simulate the basic logic here.
        
        relation_status = "NEUTRAL"
        explanation = ""
        
        if lagnesh_name == karyaesh_name:
            relation_status = "STRONG_SUCCESS"
            explanation = f"The Querent and the Query are ruled by the same planet ({lagnesh_name}). Success is highly likely."
        elif karyaesh_name in lagnesh.conjunct_with:
            # Need to check degrees for Ithasala vs Easarpha
            if lagnesh.degree < karyaesh.degree:
                relation_status = "SUCCESS_APPLYING"
                explanation = f"Lagnesh ({lagnesh_name}) is conjunct and applying to Karyaesh ({karyaesh_name}) (Ithasala Yoga). The event will happen."
            else:
                relation_status = "FAILURE_SEPARATING"
                explanation = f"Lagnesh ({lagnesh_name}) is conjunct but separating from Karyaesh ({karyaesh_name}) (Easarpha Yoga). The opportunity has passed."
        elif karyaesh.sign in lagnesh.aspected_by:
             # Basic mutual aspect check
             relation_status = "SUCCESS_WITH_EFFORT"
             explanation = f"Lagnesh ({lagnesh_name}) and Karyaesh ({karyaesh_name}) are in aspect. Success is possible through effort or negotiation."
        else:
            relation_status = "NO_CONNECTION"
            explanation = f"There is no direct connection between the Querent ({lagnesh_name}) and the Query ({karyaesh_name}). The event is unlikely to manifest."
            
        return {
            "question": question,
            "domain": domain,
            "lagnesh": lagnesh_name,
            "karya_bhava": karya_bhava,
            "karyaesh": karyaesh_name,
            "relation_status": relation_status,
            "explanation": explanation
        }
