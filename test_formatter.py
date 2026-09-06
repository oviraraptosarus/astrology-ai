import json
from deterministic_formatter import format_fallback_response

mock_analysis = {
    "domain": "general_timing",
    "natal_promise_status": "STRONG",
    "supporting_factors": [
        "Raja Yoga is technically present. Significance: STRONG.",
        {"reason": "Raja Yoga is technically present. Significance: STRONG."},
        "Gaja Kesari Yoga is technically present."
    ],
    "contradicting_factors": [
        "11th lord is in Dusthana."
    ],
    "dasha_activation": {
        "status": "NEUTRAL"
    }
}

print(format_fallback_response(mock_analysis))
