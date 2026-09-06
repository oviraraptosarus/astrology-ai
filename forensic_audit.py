import json
from astrology_engine import calculate_full_chart, get_semantic_view

def run_forensic_audit():
    # Steve Jobs: Feb 24, 1955, 19:15, San Francisco, CA (37.7749 N, -122.4194 W)
    print("Calculating Base Chart for Steve Jobs...")
    chart_dict = calculate_full_chart(1955, 2, 24, 19, 15, 37.7749, -122.4194)
    
    print("\n--- Basic Chart ---")
    print(json.dumps(chart_dict.get("Basic_Chart", {}), indent=2))
    
    import traceback
    try:
        print("\n--- Generating Semantic View for 'Business' ---")
        semantic_view = get_semantic_view(chart_dict, "business")
        print(json.dumps(json.loads(semantic_view), indent=2))
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    run_forensic_audit()
