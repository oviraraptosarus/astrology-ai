import os
import sys
from pprint import pprint

# Ensure the core module path is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from event_protocols import ProtocolRegistry
from methodology_router import MethodologyRouter

def test_router():
    questions = [
        "What does the next year hold for me?",
        "Can I start a business?",
        "Should I change careers?",
        "When am I likely to get married?",
        "How is my wealth?",
        "Will I move abroad?",
        "How is my education?",
        "When is a good time to start my business?"
    ]
    
    expected_domains = {
        "What does the next year hold for me?": "general_timing",
        "Can I start a business?": "BUSINESS",
        "Should I change careers?": "CAREER",
        "When am I likely to get married?": "MARRIAGE",
        "How is my wealth?": "WEALTH",
        "Will I move abroad?": "RELOCATION", # correct routing: abroad/relocation is 12th-house matter, not career
        "How is my education?": "EDUCATION",
        "When is a good time to start my business?": "BUSINESS"
    }

    expected_events = {
        "What does the next year hold for me?": "general_timing",
        "Can I start a business?": "business_start",
        "Should I change careers?": "job_change",
        "When am I likely to get married?": "marriage_timing",
        "How is my wealth?": "wealth_general",
        "Will I move abroad?": "relocation_abroad",
        "How is my education?": "education_general",
        "When is a good time to start my business?": "business_timing"
    }

    success = True

    for q in questions:
        route = MethodologyRouter.route_question(q)
        domain = route["domain"]
        event_id = ProtocolRegistry.match_event_to_protocol(q)
        
        print(f"\nQuestion: '{q}'")
        print(f"  -> Domain:   {domain}")
        print(f"  -> Event ID: {event_id}")
        
        if domain != expected_domains[q]:
            print(f"  [ERROR] Expected domain '{expected_domains[q]}' but got '{domain}'")
            success = False
            
        if event_id != expected_events[q]:
            print(f"  [ERROR] Expected event_id '{expected_events[q]}' but got '{event_id}'")
            success = False

    if success:
        print("\n[SUCCESS] All questions routed correctly!")
    else:
        print("\n[FAILURE] Routing test failed.")
        sys.exit(1)

if __name__ == "__main__":
    test_router()
