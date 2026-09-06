import json
import os
from astrology_engine import calculate_full_chart

def generate_steve_jobs_golden():
    # Steve Jobs: Feb 24, 1955, 19:15, San Francisco, CA (37.7749 N, -122.4194 W)
    chart = calculate_full_chart(1955, 2, 24, 19, 15, 37.7749, -122.4194)
    with open("tests/golden_charts/steve_jobs.json", "w") as f:
        json.dump(chart.get("Basic_Chart"), f, indent=2)
        
def generate_swami_vivekananda_golden():
    # Swami Vivekananda: Jan 12, 1863, 06:33:33, Calcutta, India (22.5726 N, 88.3639 E)
    chart = calculate_full_chart(1863, 1, 12, 6, 33, 22.5726, 88.3639)
    with open("tests/golden_charts/swami_vivekananda.json", "w") as f:
        json.dump(chart.get("Basic_Chart"), f, indent=2)

if __name__ == "__main__":
    generate_steve_jobs_golden()
    generate_swami_vivekananda_golden()
    print("Golden charts generated successfully!")
