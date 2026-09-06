import os
import json
from ai_agent import run_astrologer, get_birth_chart

def test_regression():
    print("\n--- Generating chart for test ---")
    try:
        from astrology_engine import calculate_full_chart
        from ai_agent import save_chart
        chart_data = calculate_full_chart(2000, 1, 1, 12, 0, 0.0, 0.0, tz_name="UTC", name="Regression Test")
        save_chart("regression_session", chart_data)
        print("Chart generated successfully.")
    except Exception as e:
        print(f"Failed to generate chart: {e}")
        return

    print("\n\n=== TEST 1: PROVIDER FAILURE FALLBACK ===")
    print("Simulating complete API failure by unsetting all keys and selecting a dead model.")
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("GROQ_API_KEY", None)
    os.environ.pop("AGENTROUTER_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)
    
    # "auto" will try all fallbacks and fail gracefully, returning deterministic result
    response1 = run_astrologer("What does the future hold for my career?", session_id="regression_session", provider="auto")
    
    print("\n--- Fallback Response ---")
    print(response1)
    
    if "⚠️ AI Synthesis Unavailable" in response1 and "Natal Promise:" in response1:
        print("\n✅ TEST 1 PASSED: Deterministic fallback triggered correctly.")
    else:
        print("\n❌ TEST 1 FAILED: Fallback did not contain expected deterministic markers.")


    print("\n\n=== TEST 2: GENERAL QUESTION ROUTING ===")
    print("Testing general question classification logic.")
    
    # We can check the methodology router directly, or check the fallback response domain
    from event_protocols import ProtocolRegistry
    route = ProtocolRegistry.match_event_to_protocol("What does the next year hold for me?")
    print(f"Question: 'What does the next year hold for me?' -> Routed to Domain: {route}")
    
    if route == "general_timing":
        print("\n✅ TEST 2 PASSED: Question routed to general_timing instead of career_promotion.")
    else:
        print("\n❌ TEST 2 FAILED: Question routed to incorrect domain.")

if __name__ == "__main__":
    test_regression()
