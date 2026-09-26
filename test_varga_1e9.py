import math

def test_varga_edge_cases():
    test_cases = [0.0, 9.999999995, 29.999999995, 30.0]
    span = 10.0
    epsilon = 1e-9

    print("D3 Drekkana Test (span=10.0):")
    for degree in test_cases:
        raw_div = degree / span
        with_eps = raw_div + epsilon
        div = int(with_eps)
        print(f"Degree: {degree:.10f}, Raw: {raw_div:.12f}, +1e-9: {with_eps:.12f}, int(): {div}")

if __name__ == "__main__":
    test_varga_edge_cases()
