"""
pre_publish_check.py — Run before every deploy. Blocks if the engine regressed.

Covers exactly the bug classes the LLM layer can't see:
  1. Full regression suite (39 PyJHora-locked checks)
  2. Golden-chart self-test (dasha seed / timeline / cross-engine consistency)
  3. Live provider probes (decommissioned models, missing keys)

Usage:  python pre_publish_check.py
Exit code 0 = safe to deploy. Non-zero = fix before publishing.
"""
import subprocess
import sys

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

failures = []


def banner(t):
    print(f"\n{'=' * 64}\n {t}\n{'=' * 64}")


# 1. Regression suite
banner("STEP 1/4: REGRESSION SUITE (test_engine_validation.py)")
r = subprocess.run([sys.executable, "test_engine_validation.py"],
                   capture_output=True, text=True, cwd=__import__("os").path.dirname(__file__) or ".")
print(r.stdout[-1200:])
if r.returncode != 0:
    failures.append("regression suite FAILED (39 checks must pass)")

# 2. Golden-chart self-test
banner("STEP 2/4: GOLDEN-CHART SELF-TEST (engine_self_test.py)")
from engine_self_test import run_golden_checks, probe_providers
golden = run_golden_checks()
all_ok = True
for key, g in golden.items():
    status = f"{GREEN}PASS{RESET}" if g["ok"] else f"{RED}FAIL{RESET}"
    print(f"  [{status}] {key}")
    for c in g["checks"]:
        if not c["ok"]:
            print(f"      FAILED: {c['name']}: {c['detail']}")
            all_ok = False
if not all_ok:
    failures.append("golden-chart self-test FAILED")

# 3. Provider probes
banner("STEP 3/4: PROVIDER PROBES")
probes = probe_providers()
for prov, status in probes.items():
    is_bad = "DOWN" in status or "MISSING" in status or "NOT_CONFIGURED" in status
    color = RED if is_bad else (YELLOW if "CONFIGURED" in status else GREEN)
    print(f"  {prov:<14} {color}{status}{RESET}")
    # OmniRoute + Ollama are OPTIONAL local dev services — warn, never block deploy
    if is_bad and prov not in ("Ollama", "OmniRoute"):
        failures.append(f"{prov}: {status}")

# 4. Ground-truth retrodiction accuracy floor
banner("STEP 4/4: GROUND-TRUTH RETRODICTION (validation_harness.py)")
ACCURACY_FLOOR = 60.0
try:
    from validation_harness import run as run_validation
    vsummary, _ = run_validation(as_json=True) if False else run_validation()
    acc = vsummary["weighted_accuracy_pct"]
    t = vsummary["tally"]
    if t.get("WRONG", 0) > 0:
        failures.append(f"retrodiction: {t['WRONG']} case(s) called the WRONG direction (worse than a hedge)")
    if acc < ACCURACY_FLOOR:
        failures.append(f"retrodiction accuracy {acc}% below floor {ACCURACY_FLOOR}%")
except Exception as e:
    failures.append(f"validation harness crashed: {e}")

print()
if failures:
    print(f"{RED}✗ PRE-PUBLISH CHECK FAILED — fix before deploying:{RESET}")
    for f in failures:
        print(f"   • {f}")
    sys.exit(1)
else:
    print(f"{GREEN}✓ ALL PRE-PUBLISH CHECKS PASSED — safe to deploy.{RESET}")
    sys.exit(0)
