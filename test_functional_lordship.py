import json
import traceback
from vedic_models import Chart, Planet
from functional_benefic_engine import FunctionalBeneficEngine

# The 12 signs in order
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": "Mars", "Scorpio": "Mars",
    "Taurus": "Venus", "Libra": "Venus",
    "Gemini": "Mercury", "Virgo": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Sagittarius": "Jupiter", "Pisces": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn"
}

def create_mock_chart_for_ascendant(ascendant_sign: str) -> Chart:
    chart = Chart(ascendant_sign=ascendant_sign, ascendant_degree=15.0)
    
    asc_idx = ZODIAC_SIGNS.index(ascendant_sign)
    
    # Add planets and calculate their house ownerships relative to this Ascendant
    for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        p = Planet(p_name, "Aries", 15.0, False)
        
        # Determine house ownerships
        for sign, lord in SIGN_LORDS.items():
            if lord == p_name:
                sign_idx = ZODIAC_SIGNS.index(sign)
                house = ((sign_idx - asc_idx) % 12) + 1
                p.owns_houses.append(house)
                
        p.owns_houses.sort()
        chart.add_planet(p)
        
    return chart

def test_all_ascendants():
    print("Testing Functional Lordship Rules Across All 12 Ascendants...\n")
    
    errors = 0
    
    expected_results = {
        "Aries": {
            "Mars": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False}, # 1, 8
            "Sun": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False}, # 5
            "Jupiter": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False}, # 9, 12
            "Saturn": {"Yoga Karaka": False, "Maraka": False, "Badhaka": True}, # 10, 11 (Badhaka for Aries)
            "Venus": {"Yoga Karaka": False, "Maraka": True, "Badhaka": False} # 2, 7 (Maraka)
        },
        "Taurus": {
            "Saturn": {"Yoga Karaka": True, "Maraka": False, "Badhaka": False}, # 9, 10
            "Venus": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False}, # 1, 6
            "Jupiter": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False}, # 8, 11
            "Mars": {"Yoga Karaka": False, "Maraka": True, "Badhaka": False}, # 7, 12
            "Sun": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False} # 4
        },
        "Gemini": {
            "Venus": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False}, # 5, 12
            "Saturn": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False}, # 8, 9
            "Jupiter": {"Yoga Karaka": False, "Maraka": True, "Badhaka": True}, # 7, 10 (7 is Badhaka for dual, and Maraka)
            "Mars": {"Yoga Karaka": False, "Maraka": False, "Badhaka": False} # 6, 11
        },
        "Cancer": {
            "Mars": {"Yoga Karaka": True, "Maraka": False, "Badhaka": False}, # 5, 10
            "Sun": {"Yoga Karaka": False, "Maraka": True, "Badhaka": False}, # 2 (Maraka)
            "Saturn": {"Yoga Karaka": False, "Maraka": True, "Badhaka": False}, # 7, 8 (Maraka)
            "Venus": {"Yoga Karaka": False, "Maraka": False, "Badhaka": True} # 4, 11 (11 is Badhaka for Cancer)
        }
    }
    
    for asc_sign in ZODIAC_SIGNS:
        chart = create_mock_chart_for_ascendant(asc_sign)
        FunctionalBeneficEngine.calculate_functional_roles(chart)
        
        print(f"--- ASCENDANT: {asc_sign} ---")
        for p_name, p in chart.planets.items():
            roles = p.detailed_functional_roles
            role_str = ", ".join(roles) if roles else p.functional_role
            print(f"{p_name:<8} (Owns {str(p.owns_houses):<8}): {role_str}")
            
            # Assert against expected logic
            if asc_sign in expected_results and p_name in expected_results[asc_sign]:
                expected = expected_results[asc_sign][p_name]
                
                # Check Yoga Karaka
                if expected["Yoga Karaka"] and "Yoga Karaka" not in roles:
                    print(f"  [ERROR] {p_name} should be Yoga Karaka!")
                    errors += 1
                elif not expected["Yoga Karaka"] and "Yoga Karaka" in roles:
                    print(f"  [ERROR] {p_name} should NOT be Yoga Karaka!")
                    errors += 1
                    
                # Check Maraka
                if expected["Maraka"] and "Maraka" not in roles:
                    print(f"  [ERROR] {p_name} should be Maraka!")
                    errors += 1
                    
                # Check Badhaka
                if expected["Badhaka"] and "Badhaka" not in roles:
                    print(f"  [ERROR] {p_name} should be Badhaka!")
                    errors += 1
                    
    print(f"\nCompleted with {errors} errors.")

if __name__ == "__main__":
    test_all_ascendants()
