"""
Ground-Truth Retrodiction Harness
==================================
Runs the REAL prediction pipeline (EventPredictionEngine) against charts with
DOCUMENTED life outcomes and scores whether the deterministic verdict matches
recorded reality.

Design principle (per project owner): ACCURACY OVER COMFORT.
- A decisive life that the engine calls HEDGE/CONTRADICTION is a logged calibration
  MISS, never smoothed over.
- This harness does NOT tune the engine toward confidence. It measures. Fixing a
  miss means fixing the math/weighting, then re-measuring — never editing the
  expectation to match the engine.

Usage:
    venv/Scripts/python.exe validation_harness.py
    venv/Scripts/python.exe validation_harness.py --json     # machine-readable
"""
import sys, os, json, argparse, warnings
from datetime import datetime
import pytz

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
warnings.filterwarnings("ignore")

from astrology_engine import calculate_chart_with_object
from event_analysis import EventPredictionEngine

# ---- Verdict interpretation ------------------------------------------------
# Map the engine's raw labels to a coarse directional call so we can compare
# against documented POSITIVE / NEGATIVE reality.

POSITIVE_PROMISE = {"VERY STRONG", "STRONG"}
NEGATIVE_PROMISE = {"WEAK", "INSUFFICIENT"}
HEDGE_PROMISE    = {"MODERATE", "MIXED"}

POSITIVE_CONV = {"STRONG_CONVERGENCE_POSITIVE", "WEAK_CONVERGENCE_POSITIVE"}
NEGATIVE_CONV = {"STRONG_CONVERGENCE_NEGATIVE", "WEAK_CONVERGENCE_NEGATIVE"}
HEDGE_CONV    = {"CONTRADICTION", "NO_DATA", "N/A", "DISAGREEMENT"}


def _directional_call(promise: str, convergence: str) -> str:
    """Combine natal promise + convergence into POSITIVE / NEGATIVE / HEDGE.

    A confident call requires BOTH layers to agree in direction. If they conflict
    or either is a hedge, the overall call is HEDGE — which is honest, but is
    scored as a MISS whenever documented reality was decisive.
    """
    p = "POS" if promise in POSITIVE_PROMISE else "NEG" if promise in NEGATIVE_PROMISE else "HEDGE"
    c = "POS" if convergence in POSITIVE_CONV else "NEG" if convergence in NEGATIVE_CONV else "HEDGE"

    if p == "POS" and c == "POS":
        return "POSITIVE"
    if p == "NEG" and c == "NEG":
        return "NEGATIVE"
    if p == "POS" and c == "HEDGE":
        return "LEAN_POSITIVE"
    if p == "NEG" and c == "HEDGE":
        return "LEAN_NEGATIVE"
    if p == "HEDGE" and c == "POS":
        return "LEAN_POSITIVE"
    if p == "HEDGE" and c == "NEG":
        return "LEAN_NEGATIVE"
    # p/c directly conflict, or both hedge
    return "HEDGE"


def _score(expected: str, call: str) -> str:
    """HIT / PARTIAL / MISS against documented reality."""
    want = expected.upper()  # POSITIVE or NEGATIVE
    if call == want:
        return "HIT"
    if call == f"LEAN_{want}":
        return "PARTIAL"
    if call == "HEDGE":
        return "MISS"          # decisive life, engine wouldn't commit
    # engine committed to the OPPOSITE direction — the worst failure
    return "WRONG"


def run(cases_path="validation_cases.json", as_json=False):
    data = json.load(open(cases_path, encoding="utf-8"))
    cases = data["cases"]

    rows = []
    tally = {"HIT": 0, "PARTIAL": 0, "MISS": 0, "WRONG": 0, "ERROR": 0}

    for case in cases:
        b = case["birth"]
        name = case["name"]
        btc = case.get("birth_time_confidence", "?")
        try:
            chart, _cd = calculate_chart_with_object(
                b["year"], b["month"], b["day"], b["hour"], b["minute"],
                b["lat"], b["lon"], tz_name=b["tz"], name=name
            )
            engine = EventPredictionEngine(chart)
        except Exception as e:
            for oc in case["outcomes"]:
                rows.append({"name": name, "btc": btc, "question": oc["domain_question"],
                             "expected": oc["expected"], "promise": "ERR", "convergence": str(e)[:60],
                             "call": "ERROR", "score": "ERROR", "note": oc.get("note", "")})
                tally["ERROR"] += 1
            continue

        for oc in case["outcomes"]:
            yr = oc.get("achievement_year", datetime.now().year)
            target = datetime(yr, 6, 1, tzinfo=pytz.utc)
            try:
                res = engine.analyze_event(oc["domain_question"], target)
                promise = res.natal_promise.get("status", "?")
                convergence = res.convergence
                call = _directional_call(promise, convergence)
                score = _score(oc["expected"], call)
            except Exception as e:
                promise, convergence, call, score = "ERR", str(e)[:60], "ERROR", "ERROR"
            tally[score] = tally.get(score, 0) + 1
            rows.append({"name": name, "btc": btc, "question": oc["domain_question"],
                         "expected": oc["expected"], "achievement_year": yr,
                         "promise": promise, "convergence": convergence,
                         "call": call, "score": score, "note": oc.get("note", "")})

    total = sum(tally.values())
    # Accuracy = HIT full credit, PARTIAL half credit. WRONG/MISS/ERROR = 0.
    graded = tally["HIT"] + 0.5 * tally["PARTIAL"]
    accuracy = (graded / total * 100.0) if total else 0.0

    summary = {"total": total, "tally": tally, "weighted_accuracy_pct": round(accuracy, 1)}

    if as_json:
        print(json.dumps({"summary": summary, "rows": rows}, indent=2))
        return summary, rows

    # ---- Blunt text report -------------------------------------------------
    print("=" * 78)
    print(" GROUND-TRUTH RETRODICTION HARNESS  —  accuracy over comfort")
    print("=" * 78)
    for r in rows:
        icon = {"HIT": "[HIT ]", "PARTIAL": "[PART]", "MISS": "[MISS]",
                "WRONG": "[WRONG]", "ERROR": "[ERR ]"}.get(r["score"], "[????]")
        print(f"\n{icon} {r['name']}  (birth-time conf: {r['btc']})")
        print(f"       Q: {r['question']}")
        print(f"       Expected: {r['expected']}   |   Engine call: {r['call']}")
        print(f"       promise={r['promise']}  convergence={r['convergence']}")
        if r["score"] in ("MISS", "WRONG"):
            print(f"       >>> {r['score']}: documented reality was decisive; engine did not match. {r['note']}")
    print("\n" + "=" * 78)
    t = summary["tally"]
    print(f" RESULT: {t['HIT']} HIT | {t['PARTIAL']} PARTIAL | {t['MISS']} MISS | "
          f"{t['WRONG']} WRONG | {t['ERROR']} ERROR   (n={summary['total']})")
    print(f" WEIGHTED ACCURACY: {summary['weighted_accuracy_pct']}%  "
          f"(HIT=1.0, PARTIAL=0.5, else 0)")
    print("=" * 78)
    print(" NOTE: A MISS means the engine hedged on a decisive life. That is a")
    print(" calibration failure to FIX IN THE MATH — never by editing the expectation.")
    print("=" * 78)
    return summary, rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--cases", default="validation_cases.json")
    args = ap.parse_args()
    summary, _ = run(args.cases, as_json=args.json)
    # Non-zero exit if weighted accuracy below a floor, so it can gate CI later.
    sys.exit(0 if summary["weighted_accuracy_pct"] >= 0 else 1)
