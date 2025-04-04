import math


def normalize_cyclic(value, min, max):
    deviation = max - min
    if deviation == 0:
        return min
    return value % (deviation) + min


def get_error_rate(value, expected_value):
    return abs(value - expected_value) / (expected_value + 1e-308)


def main():
    tolerance = 0.001 / 100
    tests = (
        (0, 0, 0, 0),
        (1, 0, 0, 0),
        (1, 1, 1, 1),
        (57625, 0, 100, 25),
        (9461.537, 0, 348.5, 52.037),
        (449, 1, 10, 9),
        (-1, 0, 100, 99),
        (math.pi, 0, 2 * math.pi, math.pi),
        (math.pi**2, -math.pi, math.pi, math.pi**2 - 3 * math.pi),
        (-math.pi**2, 0, 2 * math.pi, -math.pi**2 + 2 * math.pi * 2),
        (3 / 4 * 2 * math.pi, 0, 2 * math.pi, 3 / 4 * 2 * math.pi),
    )

    check = True
    for test_parameters in tests:
        value, min, max, answer = test_parameters
        result = normalize_cyclic(value, min, max)
        error_rate = get_error_rate(result, answer)
        remark = error_rate <= tolerance
        print(
            f"{remark} | {error_rate} | Min: {min} | Max: {max} | Result: {result} | Answer {answer}"
        )
        if not remark:
            check = False
    print(check)


if __name__ == "__main__":
    main()
