import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_full_chart

# Birth times are LOCAL at the birthplace; timezone passed explicitly.
# (The original version relied on ambient lat/lon -> tz auto-detection inside
# the engine, which the public engine signature no longer performs.)


def generate_steve_jobs_golden():
    # Steve Jobs: Feb 24, 1955, 19:15 PST, San Francisco, CA (37.7749 N, 122.4194 W)
    chart = calculate_full_chart(1955, 2, 24, 19, 15, 37.7749, -122.4194, "America/Los_Angeles")
    with open(os.path.join(os.path.dirname(__file__), "steve_jobs.json"), "w") as f:
        json.dump(chart.get("Basic_Chart"), f, indent=2)


def generate_swami_vivekananda_golden():
    # Swami Vivekananda: Jan 12, 1863, 06:33 IST, Calcutta, India (22.5726 N, 88.3639 E)
    chart = calculate_full_chart(1863, 1, 12, 6, 33, 22.5726, 88.3639, "Asia/Kolkata")
    with open(os.path.join(os.path.dirname(__file__), "swami_vivekananda.json"), "w") as f:
        json.dump(chart.get("Basic_Chart"), f, indent=2)


if __name__ == "__main__":
    generate_steve_jobs_golden()
    generate_swami_vivekananda_golden()
    print("Golden charts generated successfully!")
