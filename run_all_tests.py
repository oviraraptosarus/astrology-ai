import sys, os, glob, subprocess

test_files = glob.glob("tests/test_*.py")
print(f"Discovered {len(test_files)} test files.")

passed = []
failed = []

for tf in sorted(test_files):
    print(f"Running {tf}...", end=" ", flush=True)
    res = subprocess.run(["venv/Scripts/python.exe", tf], capture_output=True, text=True)
    if res.returncode == 0:
        print("OK")
        passed.append(tf)
    else:
        print("FAILED")
        failed.append((tf, res.stderr, res.stdout))

print("=" * 60)
print(f"SUMMARY: {len(passed)} PASSED, {len(failed)} FAILED")
print("=" * 60)

if failed:
    print("\nFAILED TESTS DETAILS:")
    for tf, err, out in failed:
        print(f"\n--- {tf} ---")
        if err.strip():
            print("STDERR:\n", err[-1000:])
        if out.strip():
            print("STDOUT:\n", out[-1000:])
