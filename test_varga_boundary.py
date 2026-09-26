import math

def get_varga_idx(degree, N):
    quotient = (degree * N) / 30.0
    rounded = round(quotient)
    if math.isclose(quotient, rounded, rel_tol=0.0, abs_tol=1e-13):
        return int(rounded)
    return int(quotient)

N = 7
boundary_2 = 60.0 / 7.0
test_cases = [
    boundary_2 - 1e-12,
    boundary_2 - 1e-10,
    boundary_2 - 1e-9,
    boundary_2 - 1e-8,
    boundary_2,
    boundary_2 + 1e-12,
    boundary_2 + 1e-10,
    boundary_2 + 1e-9,
    boundary_2 + 1e-8,
    9.999999995 # From the bug report (D3 Drekkana)
]

for val in test_cases:
    if val == 9.999999995:
        print(f"Val: {val} (N=3) -> {get_varga_idx(val, 3)}")
    else:
        print(f"Val: {val} (N=7) -> {get_varga_idx(val, 7)}")
