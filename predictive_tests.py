import json
import traceback
from astrology_engine import get_semantic_view
from ai_agent import load_prompt

# Real cases to test end-to-end predictive sequence
CASES = [
    {
        "name": "Steve Jobs Business Start",
        "question": "Should I start my business next year and will it succeed?",
        "chart_dict": {
            "Basic_Chart": {
                "Ascendant": {"sign": "Leo", "degree": 25.0},
                "planets": {

                    "Sun": {"sign": "Aquarius", "house": 7, "degree": 12.0, "retrograde": False, "owns_houses": [1], "dispositor": "Saturn", "dignity": "Enemy Sign", "vargas": {"D10": "Capricorn"}},
                    "Moon": {"sign": "Pisces", "house": 8, "degree": 21.0, "retrograde": False, "owns_houses": [12], "dispositor": "Jupiter", "dignity": "Neutral Sign", "vargas": {"D10": "Taurus"}},
                    "Mars": {"sign": "Aries", "house": 9, "degree": 6.0, "retrograde": False, "owns_houses": [4, 9], "dispositor": "Mars", "dignity": "Moolatrikona", "vargas": {"D10": "Scorpio"}},
                    "Mercury": {"sign": "Capricorn", "house": 6, "degree": 21.0, "retrograde": True, "owns_houses": [2, 11], "dispositor": "Saturn", "dignity": "Friendly Sign", "vargas": {"D10": "Gemini"}},
                    "Jupiter": {"sign": "Gemini", "house": 11, "degree": 27.0, "retrograde": False, "owns_houses": [5, 8], "dispositor": "Mercury", "dignity": "Enemy Sign", "vargas": {"D10": "Taurus"}},
                    "Venus": {"sign": "Sagittarius", "house": 5, "degree": 28.0, "retrograde": False, "owns_houses": [3, 10], "dispositor": "Jupiter", "dignity": "Enemy Sign", "vargas": {"D10": "Pisces"}},
                    "Saturn": {"sign": "Libra", "house": 3, "degree": 28.0, "retrograde": False, "owns_houses": [6, 7], "dispositor": "Venus", "dignity": "Exalted", "vargas": {"D10": "Aquarius"}}
                }
            },
            "Current_Dasha": {
                "Mahadasha": "Rahu",
                "Antardasha": "Jupiter",
                "Pratyantardasha": "Saturn"
            },
            "Live_Transits_Gochar": {
                "Jupiter": {"sign": "Aries", "house": 9},
                "Saturn": {"sign": "Aquarius", "house": 7}
            }
        },
        "expected_domain": "business",
        "expected_dasha_activation": "Rahu" # Example
    }
]

def run_tests():
    print("Running End-to-End Predictive Tests...")
    
    for case in CASES:
        print(f"\n--- Testing: {case['name']} ---")
        try:
            # 1. Run Deterministic Engine
            synthesis_json_str = get_semantic_view(case["chart_dict"], case["expected_domain"])
            synthesis = json.loads(synthesis_json_str)
            
            # Print intermediate EventAnalysis state
            print("\n[INTERNAL EVENT ANALYSIS GENERATED]")
            print(json.dumps(synthesis, indent=2))
            
            assert "methodology" in synthesis, "Missing methodology in output"
            assert "timing_stack" in synthesis, "Missing timing stack in output"
            
            # 2. Simulate LLM Generation Prompt Setup
            prompt_template = load_prompt("GENERAL.txt")
            prompt = prompt_template.replace("{synthesis_data}", synthesis_json_str)
            prompt = prompt.replace("{user_question}", case["question"])
            prompt = prompt.replace("{retrieved_astrology_rules}", "N/A (Mocked)")
            prompt = prompt.replace("{case_studies}", "N/A (Mocked)")
            
            print("\n[FINAL PROMPT FED TO LLM]")
            print(prompt)
            print("\nTest passed successfully.")
            
        except Exception as e:
            print(f"Test Failed: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    run_tests()
