import os
from ai_agent import run_astrologer, get_birth_chart

def test():
    print("Generating chart for test...")
    # Generate a dummy chart for the session so fallback has data
    try:
        from astrology_engine import calculate_full_chart
        from ai_agent import save_chart
        chart_data = calculate_full_chart(2000, 1, 1, 12, 0, 0.0, 0.0, "Fallback Test")
        save_chart("fallback_test_session", chart_data)
        print("Chart generated.")
    except Exception as e:
        print(f"Failed to generate chart: {e}")
        return
        
    print("\n--- Running Astrologer with BAD provider to trigger deterministic fallback ---")
    
    # We will pass a provider name that isn't mapped, which defaults to Ollama.
    # Since Ollama isn't running on my container, it should fail and trigger fallback.
    # Actually 'auto' without keys should also fail gracefully. Let's use 'auto'.
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("GROQ_API_KEY", None)
    os.environ.pop("AGENTROUTER_API_KEY", None)
    os.environ.pop("OPENROUTER_API_KEY", None)
    
    response = run_astrologer("What does the future hold for my career?", session_id="fallback_test_session", provider="auto")
    
    print("\n\nRESPONSE FROM AGENT:\n===================")
    print(response)

if __name__ == "__main__":
    test()
